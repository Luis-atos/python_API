import requests

# Configuración
GITLAB_URL = 'https://git.servdev.mdef.es'  # Reemplaza con la URL de tu instancia de GitLab si es self-hosted
GROUP_ID = '469'  # Reemplaza con el ID de tu grupo
PRIVATE_TOKEN = 'glpat-bztPmF7g1AQ3LuYsEjgt'  # Reemplaza con tu token de acceso personal

# Headers para la autenticación
headers = {
    'Private-Token': PRIVATE_TOKEN
}

# Función para obtener todos los proyectos del grupo
def get_all_projects(group_id):
    projects = []
    page = 1
    per_page = 100  # Número máximo de proyectos por página

    while True:
        url = f'{GITLAB_URL}/api/v4/groups/{group_id}/projects'
        params = {
            'per_page': per_page,
            'page': page
        }
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            print(f'Error al obtener proyectos: {response.status_code} - {response.text}')
            break

        data = response.json()
        if not data:
            break

        projects.extend(data)
        page += 1

    return projects

# Función para desarchivar un proyecto
def unarchive_project(project_id):
    url = f'{GITLAB_URL}/api/v4/projects/{project_id}/unarchive'
    response = requests.post(url, headers=headers)
    if response.status_code == 201:
        print(f'Proyecto {project_id} desarchivado con éxito.')
    else:
        print(f'Error al desarchivar el proyecto {project_id}: {response.status_code} - {response.text}')

def main():
    projects = get_all_projects(GROUP_ID)
    if not projects:
        print('No se encontraron proyectos en el grupo o ocurrió un error.')
        return

    for project in projects:
        if project.get('archived'):
            print(f'Desarchivando proyecto: {project.get("name")} (ID: {project.get("id")})')
            unarchive_project(project.get('id'))
        else:
            print(f'El proyecto {project.get("name")} ya está activo.')

if __name__ == '__main__':
    main()

