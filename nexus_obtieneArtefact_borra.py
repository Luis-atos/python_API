================== Metodo de ejecucion ========
python3 <nombre_Funcion> <Componente_Repositorio> <Repositorio>
python3 nexus_artifacts2.py "LUIS_SIADIDEF_AP" "snapshots"
=================================================================

import requests
import sys
import json
import subprocess
from requests.auth import HTTPBasicAuth

# Configuración
nexus_url = "http://nexus.servdev.mdef.es:8081"  # URL de tu Nexus (ajusta el puerto si es diferente)
nexus_url_https = "https://nexus.servdev.mdef.es"  # URL de tu Nexus (ajusta el puerto si es diferente)

username = "deployjenkins"  # Usuario de Nexus
password = "cc0msi2016."  # Contraseña de Nexus


def delete_old_component(nexus_url, repository_name, username, password, componente):
    # Asignación de las variables usando los parámetros de la función
    usuarioDBProperties = username
    claveDBProperties = password
    print("Resultado :", componente, "****" , nexus_url)
    if (repository_name == "snapshots"):
       ruta = "PruebaTest/PruebaTest/"
    else:
       ruta = ""
    # Comando curl correctamente formado
    comando_curl = [
        "curl",
        "--request", "DELETE",
        "--user", f"{usuarioDBProperties}:{claveDBProperties}",
        f"{nexus_url}/service/rest/v1/assets/{componente}"
    ]

    resultado = subprocess.run(comando_curl, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

    # Imprimir resultados
    print("Salida:", resultado.stdout)
    print("Error:", resultado.stderr)



def list_raw_folders(nexus_url, repository_name, username, password, repo):
    # Endpoint de búsqueda de componentes
    endpoint = f"{nexus_url}/service/rest/v1/assets?repository={repository_name}"
    params = {}
    if (repository_name == "snapshots"):
       params = {"q": "PruebaTest/PruebaTest"}
    auth = HTTPBasicAuth(username, password)

    folders = set()
    continuation_token = None

    while True:
        if continuation_token:
            params["continuationToken"] = continuation_token

        response = requests.get(endpoint, auth=auth, params=params)

        if response.status_code != 200:
            print(f"Error: {response.status_code} - {response.text}")
            break

        data = response.json()
        #print(json.dumps(data, indent=4, ensure_ascii=False))
        for item in data.get("items", []):
            path = item.get("path")
            id = item.get("id")
            if repo in path:
                #folders.add(path)
                folders.add(id)
        continuation_token = data.get("continuationToken")
        if not continuation_token:
            break

    return sorted(folders)


if __name__ == "__main__":
    componente = sys.argv[1]
    repository_name = sys.argv[2]
    folders = list_raw_folders(nexus_url, repository_name, username, password, componente)
    if folders:
        setCarpetas =  len(folders)
        print("La longitud es ...", setCarpetas)
        if setCarpetas == 5 or  setCarpetas > 5:
          print(f"******** Longitud igul o mayor a 5 ******")
          idComponentes = list(folders)
          delete_old_component(nexus_url_https, repository_name, username, password, idComponentes[0])
        elif setCarpetas < 5:
          print(f"********** Carpetas principales en el repositorio RAW '{repository_name}':")
          for folder in folders:
            print(f"- {folder}")
    else:
      print(f"No se encontraron carpetas en el repositorio '{repository_name}'.")

