# Estructura de archivos

## Modulo recoleccion

Carpeta raiz: harvester

- Carpeta `spiders`: contendra los archivos con las implemntaciones de loa spiders, y a ella se deberan agregar las nuevas spiders que sean implemntadas.
  - `CustomSpider.py`: sera la clase principal a implementar en un primer momento dado que constituira un modelo para la posterior implmentacion de spiders mas especializados que herden de esta.
  - El restos de las spiders que sean implementadas
- `DBPipeline.py `: implmentacion de clase en python con metodos `open_spider(self, spider)`, `close_spider(self, spider)` y `process_item(self, item, spider)` donde en este ultimo se implementara la funcionalidad de guardar en la base de datos.
- `items.py`: fichero donde iran items, encargados de establecer una estructura para la informacion que devuelve un parse determinado, y itemloaders, encargados de realizar cierta limpieza sobre estos datos.
- `starting_crawl.py`: implmentacion de funcion `start_crawling` que recibira los datos del crawler a utilizar y se encargara de instanciar un `CrawlerProcess` con la spider correspondiente(se debera buscar una manera de hacer que de acuerdo al `name` recibido se pueda saber que clase de spider usar, por ejemplo se me ocurre un diccionario con los nombres como claves y las clases como valor). Finalmente esta funcion iniciara el proceso de recoleccion.
