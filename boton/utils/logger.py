import logging

class BotonLogger:
    _logger = None
    
    @classmethod
    def get_logger(self):
        if self._logger is None:
            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s [%(levelname)s] %(message)s",
                handlers=[
                    logging.StreamHandler()
                ]
            )
        
            self._logger =  logging.getLogger(__name__)
        return self._logger