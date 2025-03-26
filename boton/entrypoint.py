from boton import REVIEWERS_DISPONIBLES, LLM_PROVIDER, LLM_ENDPOINT, LLM_API_KEY, PROMPT_FILE
from boton.interfaces.github_interface import GitHubInterface
from boton.utils.logger import BotonLogger

logger = BotonLogger.get_logger()

def review():
    logger.info("Iniciando el proceso de revision de codigo con LLM...")
    
    logger.info(f"llm_provider: {LLM_PROVIDER}")
    logger.info(f"llm_endpoint: {LLM_ENDPOINT}")
    logger.info(f"prompt_file(s): {PROMPT_FILE}")

    # Asegurar que el reviewer provisto por el usuario es uno de los disponibles
    rvwr = REVIEWERS_DISPONIBLES.get(LLM_PROVIDER, "azure_openai")
    assert rvwr is not None, f"El proveedor de LLM {LLM_PROVIDER} no se encuentra disponible. Los disponibles hasta el momento son {REVIEWERS_DISPONIBLES.keys()}"

    # Cuestiones relacionadas a github para el manejo de PRs
    gh = GitHubInterface()
    numero_pr = gh.get_pr_number()

    # Las diferencias de código en el PR vienen en una lista, se unen todos los elementos en un solo string
    diffs_codigo = gh.get_all_diffs()
    diffs_codigo_str ="\n\n".join(diffs_codigo)

    if len(diffs_codigo) == 0:
        logger.warning("No se encontraron diferencias de códigos en el PR.")
        return
    
    # Consideramos el proveedor de LLM a utilizar, por defecto vamos con "azure_openai"
    c = rvwr(endpoint=LLM_ENDPOINT, prompt_file=PROMPT_FILE, api_key=LLM_API_KEY)
    revision = c.review_w_all_prompts(diff_codigo=diffs_codigo_str)
    gh.comment_pr(numero=numero_pr, comentario=revision)

if __name__ == "__main__":
    review()