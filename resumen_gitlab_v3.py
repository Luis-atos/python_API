import sys
from datetime import datetime
import requests
import configparser

def mostrar_ayuda():
    """Muestra las instrucciones de uso del script."""
    ayuda = """
Uso: python script.py [--help]

Este script lee una lista de URLs de repositorios desde un archivo, consulta las ramas
de cada repositorio usando la API de GitLab, y muestra un resumen de las ramas.

Configuración:
- Asegúrese de tener un archivo 'config.ini' con las siguientes secciones:

[gitlab]
token = TU_TOKEN_PRIVADO  # Token de acceso personal de GitLab
url_base = https://gitlab.com  # Base URL de GitLab (puede ser personalizada)

[general]
fichero_urls = urls.txt  # Nombre del archivo que contiene las URLs de los repositorios

Parámetros:
--help      Muestra esta ayuda y termina la ejecución del script.

Ejemplo de uso:
python script.py

Asegúrese de que el archivo 'urls.txt' contenga una lista de URLs de repositorios GitLab,
una por línea.
"""
    print(ayuda)
    sys.exit(0)

def leer_configuracion(fichero_config):
    """Lee la configuración desde un archivo INI."""
    config = configparser.ConfigParser()
    config.read(fichero_config)
    return config

def leer_urls(fichero_rutas):
    """Lee las URLs de un archivo de texto."""
    try:
        with open(fichero_rutas, 'r') as f:
            return [url.strip() for url in f if url.strip()]
    except FileNotFoundError:
        print(f"El fichero {fichero_rutas} no se encuentra.")
        sys.exit(1)
    except Exception as e:
        print(f"Error leyendo el fichero {fichero_rutas}: {e}")
        sys.exit(1)

def obtener_branches(repo_url, token, url_base):
    """Obtiene todas las ramas de un repositorio desde la API de GitLab."""
    if url_base not in repo_url:
        print(f"URL no coincide con la base configurada: {repo_url}")
        return []

    try:
        project_path = repo_url.split(url_base + '/')[1].replace('/', '%2F')  # Codificar para URL
        headers = {'PRIVATE-TOKEN': token}
        full_url = f"{url_base}/api/v4/projects/{project_path}/repository/branches"

        response = requests.get(full_url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error accediendo a {repo_url}: {e}")
        return []

def convertir_fecha(fecha_str):
    """Convierte una cadena de fecha ISO 8601 a un objeto datetime, manejando zonas horarias."""
    try:
        if '.' in fecha_str:
            return datetime.strptime(fecha_str.split('.')[0], "%Y-%m-%dT%H:%M:%S")
        else:
            return datetime.strptime(fecha_str.split('Z')[0], "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        print(f"Formato de fecha no reconocido: {fecha_str}")
        return datetime.min

def procesar_branch(branch):
    """Extrae información relevante de cada rama."""
    fecha_actualizacion = convertir_fecha(branch['commit']['committed_date'])
    fecha_actualizacion_legible = fecha_actualizacion.strftime("%d-%m-%Y %H:%M:%S")
    return {
        'nombre': branch['name'],
        'ultima_actualizacion': fecha_actualizacion_legible,
        'ultimo_autor': branch['commit']['author_name'],
        'fecha_actualizacion_original': fecha_actualizacion  # Guardar el objeto datetime para comparaciones
    }

def mostrar_resumen(repo_url, resumen):
    """Muestra el resumen de todas las ramas del repositorio."""
    if not resumen:
        print(f"No se encontraron ramas en el repositorio {repo_url}.")
        return

    print(f"\nResumen para el repositorio: {repo_url}")
    print("-" * 70)
    print(f"{'Rama':<40} {'Última Actualización':<25} {'Último Autor':<20}")
    print("-" * 70)

    for branch in resumen:
        print(f"{branch['nombre']:<40} {branch['ultima_actualizacion']:<25} {branch['ultimo_autor']:<20}")

    rama_mas_actualizada = max(resumen, key=lambda x: x['fecha_actualizacion_original'])
    fecha_mas_reciente_legible = rama_mas_actualizada['fecha_actualizacion_original'].strftime("%d-%m-%Y %H:%M:%S")
    print("-" * 70)
    print(f"Rama más actualizada: {rama_mas_actualizada['nombre']}")
    print(f"Último autor: {rama_mas_actualizada['ultimo_autor']}")
    print(f"Fecha de última modificación: {fecha_mas_reciente_legible}")
    print("=" * 70)

def main():
    """Función principal para coordinar la ejecución del script."""
    if '--help' in sys.argv:
        mostrar_ayuda()

    config = leer_configuracion('config.ini')
    
    token = config['gitlab']['token']
    url_base = config['gitlab']['url_base']
    fichero_rutas = config['general']['fichero_urls']
    
    urls = leer_urls(fichero_rutas)

    for url in urls:
        branches = obtener_branches(url, token, url_base)
        resumen = [procesar_branch(branch) for branch in branches]
        mostrar_resumen(url, resumen)

if __name__ == "__main__":
    main()

