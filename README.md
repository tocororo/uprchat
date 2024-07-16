# uprchat (nombre provisional)

## Modulos

- model: modelo de datos (inicialmente basado en CERIF)
- harvester: recolección de datos
- mapper: transformación de datos estructurados y texto a grafo de conocimiento
- agents: agents inteligentes que usan el grafo

## Instalación

### Requisitos
- python v3.12.3
- poetry

### Instalar poetry en Linux o MacOs:
` curl -sSL https://install.python-poetry.org | python3 - `

**Nota:** al final de la instalación de poetry, mostrará un mensaje indicando añadir una línea al fichero de configuración de la terminal de tu sistema.

Una vez realizado ese paso podrás verificar la instalación con el comando:
`poetry --version`.

### Instalar Dependencias 
`poetry install`

### Otros
`black ./` Para formatear todo el proyecto