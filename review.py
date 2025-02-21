import os
import requests
import json
import logging

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
LLM_ENDPOINT = os.getenv("LLM_ENDPOINT")
API_KEY = os.getenv("API_KEY")
PROMPT_FILE = os.getenv("PROMPT_FILE")
REPOSITORIO_GITHUB = os.getenv("GITHUB_REPOSITORY")
EVENTO_GITHUB = os.getenv("GITHUB_EVENT_PATH")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def obtener_numero_pr():
    """Extrae el numero del Pull Request desde el evento de GitHub."""
    try:
        with open(EVENTO_GITHUB, "r") as f:
            datos_evento = json.load(f)
        numero_pr = datos_evento["pull_request"]["number"]
        logger.info(f"Numero del PR: {numero_pr}")
        return numero_pr
    except Exception as e:
        logger.error(f"No se pudo obtener el numero del PR: {e}")
        raise


def obtener_archivos_modificados(numero_pr):
    """Obtiene la lista de archivos modificados en el Pull Request."""
    url = f"https://api.github.com/repos/{REPOSITORIO_GITHUB}/pulls/{numero_pr}/files"
    header = {"Authorization": f"Bearer {GITHUB_TOKEN}"}

    try:
        res = requests.get(url, headers=header)
        res.raise_for_status()
        archivos_modificados = [archivo["filename"] for archivo in res.json()]
        logger.info(f"Archivos modificados en PR #{numero_pr}: {archivos_modificados}")
        return archivos_modificados
    except requests.exceptions.RequestException as e:
        logger.error(f"Error al obtener archivos modificados: {e}")
        raise


def obtener_diferencia_archivo(numero_pr, ruta_archivo):
    """Obtiene el diff de un archivo especifico en el PR."""
    url = f"https://api.github.com/repos/{REPOSITORIO_GITHUB}/pulls/{numero_pr}/files"
    header = {"Authorization": f"Bearer {GITHUB_TOKEN}"}

    try:
        res = requests.get(url, headers=header)
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


def revisar_codigo_con_llm(diff_codigo):
    _ = diff_codigo
    print("Esto es un PoC No esta implementado.")
    return "Esto es un comentario del llm..."


def comentar_en_pr(numero_pr, comentario):
    """Publica un comentario en el PR con los resultados del LLM."""
    url = f"https://api.github.com/repos/{REPOSITORIO_GITHUB}/issues/{numero_pr}/comments"
    header = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    try:
        datos = {"body": f"### Revision de Codigo con LLM 🤖\n\n{comentario}"}
        res = requests.post(url, json=datos, headers=header)
        res.raise_for_status()
        logger.info(f"Comentario publicado en el PR #{numero_pr}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error al publicar el comentario en el PR: {e}")
        raise


def main():
    logger.info("Iniciando el proceso de revision de codigo con LLM...")

    ### Esto lo hacemos a modo educacional - Imprimimos los secretos ###
    logger.info(f"llm_endpoint: {LLM_ENDPOINT}")
    logger.info(f"api_key: {API_KEY}")
    logger.info(f"github_token: este no lo imprimo")
    logger.info(f"prompt_file: {PROMPT_FILE}")
    #### Fin de impresión con fines educativos ###

    try:
        numero_pr = obtener_numero_pr()
        archivos_modificados = obtener_archivos_modificados(numero_pr)

        for archivo in archivos_modificados:
            diferencia = obtener_diferencia_archivo(numero_pr, archivo)
            if diferencia:
                # Esto dispararía el LLM la idea es que esto es un PoC
                revision = revisar_codigo_con_llm(diferencia)
                comentar_en_pr(numero_pr, f"#### Archivo: `{archivo}`\n{revision}")

        logger.info("Proceso de revision de codigo con LLM completado con exito.")
    except Exception as e:
        logger.error(f"Proceso de revision fallido: {e}")


if __name__ == "__main__":
    main()
