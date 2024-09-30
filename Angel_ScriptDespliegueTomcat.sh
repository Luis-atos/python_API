FICHERO DesarrolloConfig.sh

# Archivo de configuración para el script de despliegue
# Usuario por defecto para conexión remota (puede ser sobrescrito desde línea de comandos)
USER="root"
# Servidor remoto por defecto (puede ser sobrescrito desde línea de comandos)
SERVER="srvcceacml58D"
# Ruta de acceso al archivo .war que se generará en Jenkins
JENKINS_WAR_PATH="source/target/acceda-firma-cron.war"
# Directorio donde se encuentra la aplicación web en el servidor
DIR_WEBAPPS="/tomcatws/webapps"
# Comando para detener Tomcat
SHUTDOWN_TOMCAT_CMND="sh /tomcatws/bin/shutdown.sh"
# Comando para iniciar Tomcat
START_TOMCAT_CMND="sh /tomcatws/bin/startup.sh"
# Directorio temporal para archivos
TEMP_DIR="/tmp/comparacion_deploy"
# Directorio remoto para las aplicaciones en el servidor
COPIA_WEBAPPS_DIR="/tmp/webapps"
# Otras variables de configuración
SRC_WEBAPP="$WORKSPACE/target/webapps"
BACKUP=true
DEPLOY_WAR=true

*********************************************************************************
================
#!/bin/bash

# ==============================================================================
# Version 0.1
# Script para el despliegue de aplicaciones Tomcat.
#
# Fecha de creación: 23-09-2024
# Fecha de última modificación: 30-09-2024
# Autor: EVIDEN (Grupo Atos)
#
# Este script permite realizar el despliegue de aplicaciones web en un servidor
# remoto, incluyendo la opción de realizar respaldos previos.
#
# Puede utilizarse de dos formas:
# 1. Mediante un archivo de configuración que define los parámetros (DesarrolloConfig.sh).
# 2. Mediante parámetros de línea de comandos. En este caso, los parámetros
#    anularán cualquier configuración definida en el archivo.
#
# Parámetros:
#   --help                Muestra esta ayuda.
#   --backup              Hacer un respaldo del directorio antes de desplegar (opcional).
#   --server <servidor>   Especifica el servidor remoto para el despliegue (obligatorio).
#   --user <usuario>      Especifica el usuario para conectar al servidor remoto (obligatorio).
#   --src <ruta>          Especifica la ruta del directorio o archivos a desplegar (obligatorio).
#   --config <archivo>    Especifica un archivo de configuración diferente (opcional).
#   --deploy-war          Indica que se debe copiar un .war desde Jenkins (opcional).
#
# Ejemplo:
#   $0 --backup --server 192.168.1.100 --user admin --src /path/a/directorio
#
# Notas:
# - Verificar que el archivo de configuración esté correctamente definido antes
#   de ejecutar el script.
# - El uso de parámetros anula el uso del archivo de configuración.
# ==============================================================================

# Cargar variables de configuración
source ./DesarrolloConfig.sh

# Variables para logs y comparación
SCRIPT_NAME="${0##*/}"  # Extrae solo el nombre del script (sin el path)
LOG_FILE="./${SCRIPT_NAME%.sh}_$(date +%Y%m%d%H%M%S).log"
DIFF_FILE="./diff_$(date +%Y%m%d%H%M%S).log"

# Verificar si SRC_WEBAPP está definido, si no, usar la ruta del config.sh
if [ -z "$SRC_WEBAPP" ]; then
    echo "ERROR: SRC_WEBAPP no está definido. Verifica tu configuración." | tee -a $LOG_FILE
    exit 1
fi

# Crear directorio temporal para archivos
mkdir -p $TEMP_DIR

# Función para mostrar ayuda
function mostrar_ayuda() {
    echo "Uso: $0 [opciones]"
    echo
    echo "Opciones:"
    echo "  --help                Muestra esta ayuda."
    echo "  --backup              Hacer un respaldo del directorio antes de desplegar."
    echo "  --server <servidor>   Especifica el servidor remoto para el despliegue."
    echo "  --user <usuario>      Especifica el usuario para conectar al servidor remoto."
    echo "  --src <ruta>          Especifica la ruta del directorio o archivos a desplegar."
    echo "  --config <archivo>    Especifica un archivo de configuración diferente."
    echo "  --deploy-war          Indica que se debe copiar un .war desde Jenkins."
    echo
    echo "Ejemplo:"
    echo "  $0 --backup --server 192.168.1.100 --user admin --src /path/a/directorio"
    exit 0
}

# Función para hacer respaldo del directorio webapps
function hacer_respaldo() {
    TIMESTAMP=$(date +%Y%m%d%H%M%S)
    echo "Haciendo respaldo de $DIR_WEBAPPS en $SERVER..." | tee -a $LOG_FILE
    ssh $USER@$SERVER "cp -r $DIR_WEBAPPS $DIR_WEBAPPS-backup-$TIMESTAMP"
    if [ $? -ne 0 ]; then
        echo "Error al hacer respaldo. Abortando despliegue." | tee -a $LOG_FILE
        exit 1
    fi
}

# Función para detener Tomcat
function detener_tomcat() {
    echo "Deteniendo Tomcat en $SERVER..." | tee -a $LOG_FILE
    ssh $USER@$SERVER $SHUTDOWN_TOMCAT_CMND
    if [ $? -ne 0 ]; then
        echo "Error al detener Tomcat. Abortando despliegue." | tee -a $LOG_FILE
        exit 1
    fi
}

# Función para eliminar el contenido del directorio webapps
function limpiar_webapps() {
    echo "Eliminando el contenido de $DIR_WEBAPPS en $SERVER..." | tee -a $LOG_FILE
    ssh $USER@$SERVER "rm -rf $DIR_WEBAPPS/*" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "Error al eliminar archivos de $DIR_WEBAPPS. Abortando despliegue." | tee -a $LOG_FILE
        exit 1
    fi
}

# Función para copiar la nueva aplicación
function copiar_aplicacion() {
    if [ "$DEPLOY_WAR" = true ]; then
        echo "Copiando el archivo .war desde Jenkins a $DIR_WEBAPPS en $SERVER..." | tee -a $LOG_FILE
        # Suponiendo que el archivo .war se encuentra en un directorio específico en Jenkins
        scp $JENKINS_WAR_PATH $USER@$SERVER:$DIR_WEBAPPS/
    else
        echo "Copiando la nueva aplicación desde $SRC_WEBAPP a $DIR_WEBAPPS en $SERVER..." | tee -a $LOG_FILE
        scp -r $SRC_WEBAPP $USER@$SERVER:$DIR_WEBAPPS/
    fi

    if [ $? -ne 0 ]; then
        echo "Error al copiar la nueva aplicación. Restaurando respaldo..." | tee -a $LOG_FILE
        restaurar_respaldo
        exit 1
    fi
}

# Función para iniciar Tomcat
function iniciar_tomcat() {
    echo "Iniciando Tomcat en $SERVER..." | tee -a $LOG_FILE
    ssh $USER@$SERVER $START_TOMCAT_CMND
    if [ $? -ne 0 ]; then
        echo "Error al iniciar Tomcat. Abortando despliegue." | tee -a $LOG_FILE
        exit 1
    fi
}

# Función para verificar que Tomcat esté corriendo
function verificar_tomcat() {
    echo "Verificando que Tomcat esté corriendo en $SERVER..." | tee -a $LOG_FILE
    ssh $USER@$SERVER "curl -s http://localhost:8080" > /dev/null
    if [ $? -eq 0 ]; then
        echo "Tomcat está corriendo correctamente." | tee -a $LOG_FILE
    else
        echo "Error: Tomcat no se inició correctamente. Restaurando respaldo..." | tee -a $LOG_FILE
        restaurar_respaldo
        exit 1
    fi
}

# Función para restaurar el respaldo si hay fallos
function restaurar_respaldo() {
    echo "Restaurando el respaldo en $SERVER..." | tee -a $LOG_FILE
    ssh $USER@$SERVER "rm -rf $DIR_WEBAPPS/* && cp -r $DIR_WEBAPPS-backup-$TIMESTAMP/* $DIR_WEBAPPS/"
    if [ $? -ne 0 ]; then
        echo "Error al restaurar el respaldo. Revisa manualmente." | tee -a $LOG_FILE
        exit 1
    fi
}

# Función para generar el log de comparación
function comparar_contenido() {
    echo "Comparando el contenido de la aplicación actual en el servidor con lo que se va a desplegar..." | tee -a $LOG_FILE

    # Crear un backup temporal del directorio remoto para la comparación
    ssh $USER@$SERVER "cp -r $DIR_WEBAPPS $COPIA_WEBAPPS_DIR" 2>/dev/null

    # Traer los archivos remotos a un directorio temporal local para la comparación
    scp -r $USER@$SERVER:$COPIA_WEBAPPS_DIR $TEMP_DIR/ 2>/dev/null

    # Comparar los archivos actuales con los que se quieren desplegar
    diff -r $SRC_WEBAPP $TEMP_DIR/remote_webapps > $DIFF_FILE

    if [ $? -eq 0 ]; then
        echo "No hay diferencias entre los archivos actuales y los archivos que se van a desplegar." | tee -a $LOG_FILE
    else
        echo "Se encontraron diferencias entre los archivos actuales y los archivos que se van a desplegar." | tee -a $LOG_FILE
        echo "Las diferencias se han guardado en $DIFF_FILE" | tee -a $LOG_FILE
    fi
}

# Función principal para coordinar el despliegue
function desplegar() {
    # Comparar el contenido antes de desplegar
    comparar_contenido

    # Si está activada la opción de respaldo, hacer un respaldo
    if [ "$BACKUP" = true ]; then
        hacer_respaldo
    fi

    # Detener Tomcat
    detener_tomcat

    # Limpiar el directorio webapps
    limpiar_webapps

    # Intentar copiar la nueva aplicación
    copiar_aplicacion

    # Iniciar Tomcat
    iniciar_tomcat

    # Verificar que Tomcat esté corriendo correctamente
    verificar_tomcat

    echo "Despliegue completado con éxito." | tee -a $LOG_FILE
}

# Manejo de opciones de línea de comandos con getopts

if [[ "$#" -eq 0 ]]; then
    echo "No se han proporcionado argumentos. Muestra la ayuda con --help." | tee -a $LOG_FILE
    mostrar_ayuda
fi

while [[ "$#" -gt 0 ]]; do
    case $1 in
        --help) mostrar_ayuda ;;  # Llamar a la función de ayuda
        --backup) BACKUP=true ;;  # Activar respaldo
        --server) SERVER="$2"; shift ;;  # Especificar servidor
        --user) USER="$2"; shift ;;  # Especificar usuario
        --src) SRC_WEBAPP="$2"; shift ;;  # Especificar ruta a desplegar
        --config) source "$2"; shift ;;  # Especificar archivo de configuración
        --deploy-war) DEPLOY_WAR=true ;;  # Activar despliegue desde Jenkins
        *) echo "Opción no reconocida: $1"; mostrar_ayuda ;;  # Mostrar ayuda si hay opciones inválidas
    esac
    shift
done

# Llamada a la función principal de despliegue
desplegar
