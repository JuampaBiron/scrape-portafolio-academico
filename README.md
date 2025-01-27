# Portafolio Académico Scraper
Este proyecto es un scraper para el Portafolio Académico de la Universidad de Chile, diseñado para recopilar información sobre académicos, sus publicaciones, proyectos y tesis.
## Características

  Extracción de datos de académicos por repartición
  Recopilación de publicaciones académicas
  Obtención de información sobre proyectos de investigación
  Recopilación de tesis dirigidas
  Sistema de reintentos automáticos en caso de fallos
  Manejo de rate limiting y delays
  Guardado de datos en formatos JSON y CSV

## Instalación

- Clonar el repositorio:
- Crear y activar un entorno virtual:
- python -m venv venv
- Instalar dependencias:

## Uso
Primero que todo, obtener la unidad académica de la cual obtener información, para esto, se puede ejecutar 
python get_unidades.py 
y se obtiene el listado de unidades académicas, por ejemplo, 788 para la facultad de ciencias físicas y matemáticas

El scraper puede ejecutarse de diferentes maneras:
- Obtener solo académicos:
python get_profesors.py

- Obtener publicaciones:
python get_publicaciones.py

- Obtener proyectos:
python get_projects.py

- Obtener tesis:
python get_tesis.py

- Ejecutar el proceso completo:
python main.py

Estructura de Archivos

main.py: Punto de entrada principal
config.py: Manejo de configuración
api_client.py: Cliente API con funciones de decodificación
get_profesors.py: Scraper de académicos
get_publicaciones.py: Scraper de publicaciones
get_projects.py: Scraper de proyectos
get_tesis.py: Scraper de tesis
config.yaml: Archivo de configuración

Estructura de Datos
Los datos se guardan en la carpeta process_data en los siguientes archivos:

academicos_raw.json: Información de académicos
todas_las_publicaciones.csv: Publicaciones académicas
todos_los_proyectos.csv: Proyectos de investigación
todas_las_tesis.csv: Tesis dirigidas
