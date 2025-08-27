=================================================================
llamada al python desde jenkins CI/CD 
 output = steps.sh(script: """
                python3 ../list_checksum_Reponexus.py --repo ${repo} --subfolders ${folder}  --usu \$USERNAME --clavepass \$PASSWORD
            """, returnStdout: true).trim()
 // Agregar resultado al archivo
            steps.sh """#!/bin/bash
                echo "${output}" >> listaChecksum.txt
            """

====================================================================
import requests
from requests.auth import HTTPBasicAuth
import argparse
import json
import sys

# Ruta base que quieres analizar
BASE_PATH = "lmunozm-test01-mss/"
NEXUS_URL = "https://nexus-gnx-ssp-r01a-ip.mss.ms/service/rest/v1/components"

def get_jar_files(repository,subfolders,usu,clavepass):
    params = {
        "repository": repository
    }
    jar_files = []
    checksum_files = []
    continuation_token = None
    full_path = BASE_PATH + subfolders
    USERNAME = usu
    PASSWORD = clavepass

    while True:
        if continuation_token:
            params["continuationToken"] = continuation_token

        try:
            response = requests.get(
                NEXUS_URL,
                auth=HTTPBasicAuth(USERNAME, PASSWORD),
                params=params,
                verify=False,  # Cambiar a True si tienes certificado válido
                timeout=10
            )
        except requests.exceptions.RequestException as e:
            print(json.dumps({"error": f"Error de conexión: {e}"}))
            sys.exit(1)

        if response.status_code == 404:
            print(json.dumps({"error": f"Repositorio '{repository}' no encontrado (404)."}))
            sys.exit(1)
        elif response.status_code == 401:
            print(json.dumps({"error": "Credenciales inválidas (401 Unauthorized)."}))
            sys.exit(1)
        elif response.status_code != 200:
            print(json.dumps({"error": f"Error HTTP {response.status_code}: {response.text}"}))
            break

        data = response.json()

        for item in data.get("items", []):
            for asset in item.get("assets", []):
                path = asset.get("path", "")
                if (path.startswith(full_path) and (path.endswith(".jar") or path.endswith(".tar.gz") or path.endswith(".zip"))):
                    jar_md5 = asset.get("checksum", {}).get("md5"),
                    print(f"→ PATH:{path} → MD5: {jar_md5}")
                    if jar_md5:
                       checksum_files.append(jar_md5)

        continuation_token = data.get("continuationToken")
        if not continuation_token:
            break
    return sorted(checksum_files)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="List .jar-checksum files from Nexus repository inside a base path.")
    parser.add_argument('--repo', required=True, help='Nombre del repositorio en Nexus')
    parser.add_argument('--subfolders', required=True, help='subfolder components - vs necesarios para obtener artefactos')
    parser.add_argument('--usu', required=True, help='Usuario administrador nexus')
    parser.add_argument('--clavepass', required=True, help='Clave encriptada usuario administrador')
    args = parser.parse_args()

    checkJarsTags = get_jar_files(args.repo,args.subfolders,args.usu,args.clavepass)
    print(json.dumps({"checksum_files": checkJarsTags}, indent=2))
