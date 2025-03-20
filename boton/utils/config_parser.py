from typing import Any, Dict, List 
from fuzzywuzzy import process
import yaml

from boton.utils.logger import BotonLogger

logger = BotonLogger.get_logger()

class BotonConfigParser:
    config = None
    
    def __init__(self, archivo) -> None:
        self.load_yaml(f=archivo)

    def load_yaml(self, f) -> None:
        """
        Carga un archivo de configuración YAML y establece la configuración.
        Args:
            f (str): La ruta del archivo al archivo de configuración YAML.
        Sets:
            self.config (dict): La configuración YAML cargada como un diccionario. 
                    Si el archivo no existe o contiene sintaxis inválida, 
                    se establece un diccionario vacío.
        Raises:
            FileNotFoundError: Si el archivo especificado no existe.
            yaml.YAMLError: Si hay un error de sintaxis en el archivo YAML.
        """

        try:
            with open(f, "r") as file:
                yaml_configs = yaml.safe_load(file)
            self.config = yaml_configs if yaml_configs else {}
        except FileNotFoundError:
            logger.error(f"Error: El archivo '{f}' no existe.")
            self.config = {}
        except yaml.YAMLError as e:
            logger.error(f"Error: Sintaxis invalida en '{f}': {e}")
            self.config = {}
    
    def get_prompts(self, attr: str, valor: str) -> List[str]:
        """
        Obtiene una lista de prompts del archivo de configuración. Si `attr` o `valor` es es nulo
        se devuelven todos los prompts. Si se especifica un atributo y valor, se devuelven los prompts
        que coinciden con el atributo y valor especificados

        Args:
            attr (str): El atributo por el cual filtrar los prompts.
            valor (str): El valor del atributo para filtrar los prompts.
        Returns:
            List[str]: Una lista de prompts del archivo de configuración.
        """
        
        if attr is None or valor is None:
            return list(map(lambda p: p["prompt"], self.config.get("prompts", [])))
        
        return list(map(lambda p: p["prompt"], self.__filtrar_por_attr(attr=attr, valor=valor)))

    def __filtrar_por_attr(self, attr: str, valor: str) -> List[Dict[str, Any]]:
        """
        Filtra una lista de prompts por un atributo y su valor correspondiente.
        
        Args:
            attr (str): El nombre del atributo por el cual filtrar. Si el atributo no existe en un elemento, este se ignora.
            valor (str): El valor del atributo que deben tener los prompts filtrados.
        Returns:
            list: Una lista de prompts que coinciden con el atributo y valor especificados.
        
        """
        return [p for p in self.config.get("prompts", []) if p.get(attr) == valor]
    
    def fz_filtrar_prompt(self, consulta: str, limite: int = 3) -> List[Dict[str, Any]]:
        """
        Filtra una lista de prompts por el prompt correspondiente.
        
        Args:
            prompt (str): El prompt por el cual filtrar.
        Returns:
            list: Una lista de prompts que coinciden con el prompt especificado.
        
        """
        prompts_text = [p["prompt"] for p in self.config.get("prompts", [])]
        coincidencias = process.extract(consulta, prompts_text, limit=limite)

        # Devuelve los objetos completos que coincidan con los textos encontrados
        return [p for p in self.config.get("prompts", []) if p["prompt"] in [c[0] for c in coincidencias]]