import requests
import json
import argparse

# Configuración
sonarqube_url = 'http://sonar.servdev.mdef.es'  # URL de tu servidor SonarQube
project_key = 'es.mdef.divindes:agt'  # Clave del proyecto que deseas consultar
metrics = 'ncloc,complexity,violations,coverage,bugs,vulnerabilities,code_smells'  # Métricas que deseas obtener
username = 'jenkinstask'  # Tu nombre de usuario de SonarQube
password = 'zV5f583nPW'  # Tu contraseña de SonarQube

def main(args):
    print(f"El parámetro recibido es: {args}")
    print(f"El primero recibido es: {args.project_key}")
    print(f"El parámetro recibido es: {args.project_name}")
    # Inicializar el contenido HTML
    project_key = {args.project_key}
    project_name = {args.project_name}
    # Endpoint para obtener el estado del Quality Gate del proyecto
    quality_gate_endpoint = f'{sonarqube_url}/api/qualitygates/project_status'
    # Parámetros de la consulta
    params = {
        'projectKey': project_key
    }
    # Solicitud GET para obtener el estado del Quality Gate
    quality_gate_response = requests.get(quality_gate_endpoint, params=params, auth=(username,password))
    # Endpoint de la API
    api_url = f'{sonarqube_url}/api/measures/component?component={args.project_key}&metricKeys={metrics}'

    # Realizar la solicitud con autenticación básica
    response = requests.get(api_url, auth=(username, password))
    html_content = '''
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SonarQube Project Quality Gates</title>
        <style>
            table {
                width: 50%;
                border-collapse: collapse;
            }
            table tbody:after {
                content: "";
                display: block;
                height: 20px;
            }
            th, td {
                border: 1px solid black;
                padding: 8px;
                text-align: left;
            }
            th {
                background-color: #f2f2f2;
            }
            .PASSED {
                background-color: #d4edda;
            }
            .FAILED {
                background-color: #f8d7da;
            }
        </style>
    </head>
    <body>
        <h1>SonarQube Project Quality Gates</h1>
        <table>
            <thead>
                <tr>
                    <th>Proyecto</th>
                    <th>Estado del Quality Gate</th>
                </tr>
            </thead>
            <tbody>
    '''
    # Verifica si la solicitud fue exitosa
    if quality_gate_response.status_code == 200:
        quality_gate_data = quality_gate_response.json()
        print(json.dumps(quality_gate_data, indent=2))  # Formatear y mostrar la respuestadata
        quality_gate_status = quality_gate_data.get('projectStatus', {}).get('status')
        html_content += f'''
        <tr class="{quality_gate_status}">
            <td>{project_name}</td>
            <td>{quality_gate_status}</td>
        </tr>
       </tbody>
       </table>
        '''
        print(f'Proyecto: {project_name}, Estado del Quality Gate: {quality_gate_status}')
    else:
        print(f'Error al obtener el estado del Quality Gate para el proyecto {project_name}: {quality_gate_response.status_code}')
    # Verificar el estado de la respuesta
    if response.status_code == 200:
        data = response.json()
        print(json.dumps(data, indent=2))  # Formatear y mostrar la respuestadata
        #data_coverage = data.get('cobertura de codigo', {}).get('coverage')
        #data_vulnerabilities = data.get('vulnerabilities', {}).get('vulnerabilities')
        html_content += f''' <h1>SonarQube Metricas</h1>
        <table>
            <thead>
                <tr>
                    <th>Proyecto</th>
                    <th>Estado del Quality Gate</th>
                </tr>
            </thead>
            <tbody>
        '''
        lmetricas = data["component"]["measures"]
        for metricas in lmetricas:
           print ("metrica :",metricas["metric"])
           print ("value :", metricas["value"])
           html_content += f'''
          <tr class="{quality_gate_status}">
            <td>{metricas["metric"]}</td>
            <td>{metricas["value"]}</td>
          </tr>
          '''
       # print(json.dumps(data, indent=2))  # Formatear y mostrar la respuesta
    else:
        print(f'Error al obtener las metricas para el proyecto {project_name}: {response.status_code}')
        html_content += '''
            </tbody>
        </table>
    </body>
    </html>
    '''
	# Guardar el contenido HTML en un archivo
    file_name = f"{args.project_name}.html"
    with open(file_name, 'w', encoding='utf-8') as file:
        file.write(html_content)
    print('El archivo HTML se ha generado correctamente.')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Qualitygates Sonarqube")
    parser.add_argument('project_key', type=str, help='Clave del proyecto que deseas consultar')
    parser.add_argument('project_name', type=str, help='Nombre del proyecto que deseas consultar')
    args = parser.parse_args()
    main(args)



