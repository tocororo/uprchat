
# Proyecto uprchat

*Este texto constituye un borrador de trabajo, una guía para la escritura del proyecto, puede contener errores y cambiar con el tiempo. No tomarlo como medida o guía de nada.*

Los últimos avances de la inteligencia artifical, especialmente los llamados grandes modelos de lenguaje (Large Languaje Models, LLMs en inglés), han permitido desarrollar aplicaciones como ChatGPT que entre otras cuestiones, plantean una nueva forma de interacción hombre máquina, a través del lenguaje natural.
Se está desarrollando todo un nuevo ecosistema de aplicaciones y servicios alrededor del uso de los LLMs, con gran impacto en todas las ramas de la actividad humana, particularmente en la enseñanza y la investigación científica. El alcance de las implicaciones que esto tiene para las universidades aún se están valorando.

TODO: *una explicación sobre la necesidad de desarrollar desde Cuba y nuestra universidad estudiar y dominar esta nueva tecnología, incluir también algo del debate open vs close source, posible inspiración la entrevista del Lex Friedman a Yann Lecun*

TODO: *uno de los tipos de aplicaciones más comunes son los chats, que básicamente constituyen una forma de consultar e interactuar con los datos internos de una institución*

TODO: *hablar sobre la factibilidad de construir este tipo de aplicaciones con los pocos recursos disponibles en la universidad*

De lo anterior se deriva el objetivo general de desarrollar un chat para interactuar con los datos de la universidad a través del un LLM de código abierto.

**Objetivo general:**
Desarrollar una aplicacion chat con los datos de la Universidad de Pinar del Rio.

**Tareas principales**
Las principales tareas se deben plantear a partir de la tubería de datos (pipeline) típica de un proyecto de data science. Esto es:
1- Recolección de datos
2- Entrenamiento
3- Evaluación
4- Despliegue

## Recolección de datos

La definición de fuentes de datos está guiada por las principales actividades de la universidad: docencia e investigación, todo lo relacionado con ellas es suceptible de ser recolectado.

Bajo esta premisa se definen las siguientes fuentes de datos:

- rc: Repositorio institucional, en principio constituye la investigación científica que se desarrolla en la universidad. Metadatos: OAH-PMH. Documentos: Sword y web scrapping.
- catalogo: catálogo de libros impresos de la biblioteca, metadatos. 
- earchivos: biblioteca digital, incluye libros de textos no accesibles fuera de la universidad, tesis de grado, entre otros elementos.
- revistas de la univesidad: aunque se publican investigaciones que no son de la upr, considero que es válido incluirlas.
- recursos de aprendizaje, los moodle de pregrado y de postgrado
- información del sistema de recursos humanos, al menos la lista de trabajadores con su información básica, excluir salario u otra información sensible.
- sistema de gestión de notas, sigenu, este contiene información sobre los estudiantes y sus profesores y las asignaturas. Excluir notas u otra información sensible.

- Todas las páginas web bajo el dominio dominio upr.edu.cu deben recolectarse. Es decir que debería hacerse un crawler que recolecte todo, de una manera genérica, con la salvedad de que los sitemas especificados más arriba se recolectan de manera especial en cada caso.

La tarea de la recolección de datos se define entonces por desarrollar un crawler específico para upr.edu.cu. Que tenga además funciones especiales para algunos sistemas, por ejemplo, en los moodle el elemento central son los cursos, en el repositorio los documentos científicos. Otros sistemas o sitios bajo upr.edu.cu, también pueden tener una información específica que obtener, por ejemplo algunos sitios con información administrativa.
La recolección de datos es una tarea de la mayor importancia pues garantiza la calidad de todo lo demás.

## Entrenamiento

Esta tarea es fuertemente dependiente tanto del objetivo general como de la tecnología y técnicas que se decidan usar. Por tanto constituye, o debe plantearse como tarea de investigación.

El uso de los LLMs tiene dos vertientes principales:

- fine-tuning
- técnicas o estrategias de promts como retrived augmented generation(RAG)

Cúal técnica a usar constituye un elemento a decidir. Se considera que la mejor manera de adentrarse en el desarrollo de aplicaciones usando LLMs, es comenzar por la ingeniería del prompt, usando RAG u otro tipo de estrategias. A partir de ahí, la complegidad de los problemas que se intentan resolver pueden llevar a la necesidad de hacer un fine-tuning de un modelo.
En cualquier caso, esta es una decisión que se debe tomar de manera informada, es decir debemos ser capaces y haber experimentado con ambos enfoques antes de decidir la aquitectura final de uprchat.
Esta también es una decisión que implica determinar si se va a usar un modelo desplegado "en la casa", internamente en la upr, o si uprchat va hacer uso de servicios externos (incluso chatGpt).

Si se va a utilizar un modelo interno, esto implica otra cuestión a decidir. En el ecosistema que se está constuiyento existen distintos modelos fundacionales que son desarrollados por instituciones que disponen de los recursos para ello y son puestos a disposición del público en acceso abierto, en aras de aumentar la calidad y diversidad de las aplicaciones de IA. Es decir, la típica idea del código abierto, que ha demostrado obtener buenos resultados a través de la historia. Estos LLMs fundacionales, pueden posteriormente ser ajustados (fine-tuning) para tareas y datos específicos. En la práctica esto implica "continuar" el entrenamiento que la organización que libera el llm realizó para obtenerlo, teniendo en cuenta en esta ocasión las tareas y los datos específicos de la organización que utiliza el modelo fundacional como base.
Al momento de escibir esto, los proyectos de código abierto más importantes en codigo abierto son:

- Llama (Meta-Facebook) EEUU
- Gemma (Google) EEUU
- Mixtral (Mistral) Francia

Todos tienen arquitecturas diferentes, por lo que, en principio el uso no es exactamente igual en cada caso. Por tanto deberíamos ser capaces de utilzar los tres (o alguna de sus derivados) y comparar la calidad del resultado.
Por el momento, hasta donde conocemos, no hay modelos similares en China (el otro polo importante de desarrollo de la IA, además de EEUU), pero esto puede cambiar en el futuro cercano, así que deberíamos estar pendientes.

## Evaluación

Esta tarea se refiere a que uprchat debe brindar posibilidades al usuario final para evaluar el resultado de lo que está consultando. Esta interacción debe registrarse pues constituyen datos valiosos tanto para utilizar en tecnicas de aprendizaje por refuerzo como para posteriores ciclos de entrenamiento.

## Despliegue

Al llegar a este punto se conoce al detalle la arquitectura del sistema, los recursos que necesita y se han desarrollado las herramientas principales.

## Tecnologias a estudiar

- FastApi: Api Rest-Full [https://fastapi.tiangolo.com/]
- LangChain: Prompt Eng [https://python.langchain.com/]
- Scrapy: Web scrapping y crawler [https://scrapy.org/]
- Angular: frontend
- PyTorch [https://pytorch.org/docs/stable/index.html]
- HuggingFace libs, Gradio. [https://huggingface.co/gradio]
- Ollama [https://github.com/ollama/ollama]
- Unstructured [https://unstructured-io.github.io/unstructured/]
- OpenAPI Specification [https://www.openapis.org/]
- Postgres
