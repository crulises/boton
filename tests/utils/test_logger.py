import logging

from boton.utils.logger import BotonLogger

def test_get_logger_returns_logger_instance():
    """Verifica que `get_logger()` devuelve una instancia de `logging.Logger`"""
    logger = BotonLogger.get_logger()
    assert isinstance(logger, logging.Logger)

def test_get_logger_singleton():
    """Verifica que `get_logger()` devuelve siempre la misma instancia (singleton)"""
    logger1 = BotonLogger.get_logger()
    logger2 = BotonLogger.get_logger()
    assert logger1 is logger2  # Deben ser el mismo objeto en memoria porque es un singleton

def test_logger_logs_message(caplog):
    """Prueba que los mensajes de log se imprimen correctamente"""
    logger = BotonLogger.get_logger()
    
    with caplog.at_level(logging.INFO):
        logger.info("Este es un mensaje de prueba")
    
    # Verificar que el mensaje se encuentra en los registros capturados
    assert "Este es un mensaje de prueba" in caplog.text
