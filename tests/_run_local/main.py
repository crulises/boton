from boton.utils.logger import BotonLogger
logger = BotonLogger.get_logger()

logger.info("Todo lo que esté definido en este directorio como .py, va a ser copiado al contenedor")
logger.info("Si ejecutamos el interactivo, podremos correr los .py manualmente")
logger.info("Si ejecutamos el auto, se va a ejecutar main.py al finalizar la creacion de la imagen y el contenedor quede corriendo")