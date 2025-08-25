import requests
from requests.auth import HTTPBasicAuth

# Configura tus credenciales y la URL base del repositorio Nexus
NEXUS_URL = "https://nexus-gnx-ssp-r01a-ip.mss.ms/service/rest/v1/assets"
REPOSITORY = "arq-mss-r01-snapshot"
DIRECTORY = "lmunozm-test01-mss/components"
USERNAME = "tu_usuario"
PASSWORD = "tu_contraseña_o_token"

# Parámetros para la solicitud: repositorio y ruta de carpeta
params = {
    "repository": REPOSITORY,
    "sort": "name",
    "direction": "asc"
}

# Función para obtener todos los archivos del directorio
def get_assets():
    results = []
    continuation_token = None

    while True:
        if continuation_token:
            params["continuationToken"] = continuation_token

        response = requests.get(
            NEXUS_URL,
            auth=HTTPBasicAuth(USERNAME, PASSWORD),
            params=params
        )

        if response.status_code != 200:
            print("Error:", response.status_code, response.text)
            break

        data = response.json()

        for item in data.get("items", []):
            for asset in item.get("assets", []):
                if DIRECTORY in asset.get("path", ""):
                    results.append(asset["downloadUrl"])

        continuation_token = data.get("continuationToken")
        if not continuation_token:
            break

    return results

# Ejecutar y mostrar resultados
if __name__ == "__main__":
    assets = get_assets()
    print("Archivos encontrados en la carpeta:")
    for url in assets:
        print(url)
