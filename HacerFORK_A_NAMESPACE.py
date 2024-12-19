****************
Codigo Python para hacer un fork de un proyecto por el id a un namespace
*******************************************
  
TOKEN_LUIS_GIT
glpat-Nwx-kHyyowvJbyxq_cKV
=================
curl --header "PRIVATE-TOKEN: glpat-Nwx-kHyyowvJbyxq_cKV" "https://git.servdev.mdef.es/api/v4/groups/sistemas"
curl --header "PRIVATE-TOKEN: glpat-Nwx-kHyyowvJbyxq_cKV" "https://git.servdev.mdef.es/api/v4/groups/sistemas/subgroups"


============
import requests

# Configuración
api_url = "https://git.servdev.mdef.es/api/v4/projects/1093/fork"
headers = {
    "PRIVATE-TOKEN": "glpat-Nwx-kHyyowvJbyxq_cKV",  # Reemplaza con tu token
    "Content-Type": "application/json"
}
data = {
    "namespace": "sistemas/EXPERIMENTOS"  # Namespace destino
}

# Realizar la solicitud
response = requests.post(api_url, headers=headers, json=data)

# Verificar la respuesta
if response.status_code == 201:
    print("Fork creado exitosamente:", response.json())
else:
    print("Error al crear el fork:", response.status_code, response.json())

==========================================
