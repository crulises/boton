import json
import os
import requests
from typing import List

from boton.utils.logger import BotonLogger

logger = BotonLogger.get_logger()

class GitHubInterface:
    def __init__(self) -> None:
        self.pr_template = "https://api.github.com/repos/{github_repo}/pulls/{numero_pr}/{entidad}"
        self.base_header = {"Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}"}
        self.GITHUB_REPOSITORY = os.getenv("GITHUB_REPOSITORY")
        self.GITHUB_EVENT_PATH = os.getenv("GITHUB_EVENT_PATH")

    def get_pr_number(self) -> int:
        """Extrae el numero del Pull Request desde el evento de GitHub."""
        try:
            with open(self.GITHUB_EVENT_PATH, "r") as f:
                datos_evento = json.load(f)
            numero_pr = datos_evento["pull_request"]["number"]
            logger.info(f"Numero del PR: {numero_pr}")
            return numero_pr
        except Exception as e:
            logger.error(f"No se pudo obtener el numero del PR: {e}")
            raise

    def get_files_changed(self, numero_pr: int) -> list:
        """Obtiene la lista de archivos modificados en el Pull Request."""
        url = self.pr_template.format(github_repo=self.GITHUB_REPOSITORY, numero_pr=numero_pr, entidad="files")

        try:
            res = requests.get(url, headers=self.base_header)
            res.raise_for_status()
            archivos_modificados = [archivo["filename"] for archivo in res.json()]
            logger.info(f"Archivos modificados en PR #{numero_pr}: {archivos_modificados}")
            return archivos_modificados
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al obtener archivos modificados: {e}")
            raise
    
    def get_file_diffs(self, 
                       numero_pr: int, 
                       ruta_archivo: str) -> str:
        """Obtiene el diff de un archivo especifico en el PR."""
        url = self.pr_template.format(github_repo=self.GITHUB_REPOSITORY, numero_pr=numero_pr, entidad="files")

        try:
            res = requests.get(url, headers=self.base_header)
            res.raise_for_status()
            archivos = res.json()

            for archivo in archivos:
                if archivo["filename"] == ruta_archivo:
                    logger.info(f"Se obtuvo el diff del archivo: {ruta_archivo}")
                    return archivo["patch"]

            logger.warning(f"No se encontro diff para el archivo: {ruta_archivo}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al obtener el diff del archivo: {e}")
            raise
    
    def get_all_diffs(self) -> List[str]:
        """Obtiene los diffs de todos los archivos modificados en el PR."""
        numero_pr = self.get_pr_number()
        archivos_modificados = self.get_files_changed(numero_pr)
        diferencias = []
        for archivo in archivos_modificados:
            diferencias.append(self.get_file_diffs(numero_pr, archivo))
        return diferencias
    
    def comment_pr(self, 
                   numero_pr: int, 
                   comentario: str, 
                   prefijo_comentario: str ="### Revision de Codigo con LLM") -> None:
        """Publica un comentario en el PR con los resultados del LLM."""
        url = self.pr_template.format(github_repo=self.GITHUB_REPOSITORY, numero_pr=numero_pr, entidad="comments")
        header = self.base_header
        header["Accept"] = "application/vnd.github.v3+json"

        logger.info(f"--------Lo que le mandamos a Github--------")
        logger.info(f"Header: {header}")
        logger.info(f"Comentario: {comentario}")
        logger.info(f"--------Find lo que le mandamos a Github--------")

        try:
            datos = {"body": f"""{prefijo_comentario}\n\n{comentario}"""}
            logger.info(json.dumps(datos, indent=4))
            res = requests.post(url, json=datos, headers=header)
            res.raise_for_status()
            logger.info(f"Comentario publicado en el PR #{numero_pr}")
        except requests.exceptions.RequestException as e:
            logger.info(datos)
            logger.error(f"Error al publicar el comentario en el PR: {e}")
            raise