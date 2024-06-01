# Estructura del Recolector

## Atributos

- name(str): nombre del recolector.
- starts_urls(str | list[str]): url o lista de ellas por donde iniciara el proceso de recoleccion.
- allowed_domains(str | list[str]): dominio o lista de ellos bajo los que el recolector debera mantenerse.
- collector_type: su estructura dependera de si se desea crear un recolector "predefined" o "custom".
  - predefined(dict):
    - name(str): nombre del recolector predefined
  - custom(list[dict]): sera una lista de diccionarios que seran las reglas(rules) que regiran el recoelector. Estas tendran la estructura siguiente:
    - rules(dict):
      - regex_allowed(str | list[str]): expresiones regulares o lista de ellas que determinan las urls que se deberan parsear con determinada función de parse.
      - regex_deny(str | list[str]): expresiones regulares o lista de ellas que determinan las urls que deben ser ignoradas.
      - parse(str): nombre de la funcion de parse a usar para las urls que sigan el patron dado por las "regex_allowed".
      - follow(bool): determina si se deben seguir los enlaces encontrados por en la pagina.

## Metodos

Se tendran 2 tipos de spiders las custom definidas haciendo uso de una clase "custom_spider" la que permitira asignar a el spider diferentes comportamientos acorde a ciertos patrones en la urls(rules). El otro tipo de spiders serian las "predefinidas" las cuales seran deberan ser implementadas por un usuario "administrador" y le daran a este cierta libertad para establecer comportamientos aun mas especificos acorde a sus necesidades. La custom_spider sera la clase principal a implementar en un primer momento dado que constituira un modelo para la posterior implmentacion de spiders mas especializados que herden de esta.

### CustomSpider

- parse(self, response): metodo de parse por defecto, su implementacion ira dirijida a extraer de sitios web el texto correspondiente a url, title y body.

- parse_pdf(self, response): este extraera la url donde encontro un documento pdf y el contenido de textual de este.

- parse_docx(self, response): este extraera la url donde encontro un documento docx y el contenido de textual de este.

- parse_txt(self, response): este extraera la url donde encontro un documento txt y el contenido de textual de este.

**Nota:** Para definir esta estructura me base en las clases spider y crawlspider de Scrapy.
