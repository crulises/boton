from typing import Any
from openai import OpenAI

from boton.review.base_reviewer import BaseReviewer
from boton.utils.logger import BotonLogger

logger = BotonLogger.get_logger()

class DatabricksAnthropicReviewer(BaseReviewer):
    def __init__(
            self, 
            endpoint: str, 
            prompt_file: str, 
            api_key: str,
        ) -> None:
        super().__init__(prompt_file)
        self.reviewer = OpenAI(
            api_key=api_key, base_url=endpoint
        )
    
    def pre_process_prompts(self) -> list:
        raise NotImplementedError()
    
    def review(self, prompt: str) -> str:
        # Esto con el fin de cumplir con la clase abstracta 
        raise NotImplementedError()

    def review_single(self,  
                      prompt: str, 
                      diff_codigo: str, 
                      model: str = "claude-3-7-sonnet-20250219", # TODO: Esto por ahi lo vamos a tener que cambiar
                      reviewer_temperature: float = 0.0,
                      reviewer_top_p: float = 0.95,
                      reviewer_stop: Any = None
                      ) -> str:
        
        # Payload a ser enviado al LLM, esto puede variar segun el proveedor/modelo/endpoint/api/etc.
        message_text = [
            {
                "role": "system",
                "content": prompt
            },
            {
                "role": "user",
                "content": diff_codigo
            }
        ]

        try:
            response = self.reviewer.chat.completions.create(
                model=model,
                messages=message_text,
                temperature=reviewer_temperature,
                top_p=reviewer_top_p,
                stop=reviewer_stop
            )
            
            return (response.choices[0].message.content.strip() 
                    if response.choices 
                    else f"No correct answer from Anthropic!\n{response.text}")
            
        except Exception as e:
            return f"Anthropic failed to generate a review: {e}"

    def review_w_all_prompts(self, diff_codigo: str) -> str:
        prompts = self.config.get_prompts()
        responses = []
        
        for i, p in enumerate(prompts):    
            logger.info(f"Revisando prompt {i+1}/{len(prompts)}")
            review = self.review_single(prompt=p, diff_codigo=diff_codigo)
            responses.append(review)

        return " ".join(responses)
    
    def post_process_responses(self) -> list:
        raise NotImplementedError()