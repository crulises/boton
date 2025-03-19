from typing import Any
from openai import AzureOpenAI

from boton.review.base_reviewer import BaseReviewer
from boton.utils.logger import BotonLogger

logger = BotonLogger.get_logger()

class AzureOpenAIReviewer(BaseReviewer):
    def __init__(
            self, 
            endpoint: str, 
            prompt_file: str, 
            api_key: str,
            api_version: str = "2024-05-01-preview"
        ) -> None:
        super().__init__(prompt_file)
        self.reviewer = AzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version=api_version,
        )
    
    def pre_process_prompts(self) -> list:
        raise NotImplementedError()
    
    def review(self, prompt: str) -> str:
        # Esto con el fin de cumplir con la clase abstracta 
        raise NotImplementedError()

    def review_single(self,  
                      prompt: str, 
                      diff_codigo: str, 
                      model: str = "openai_code_review",
                      reviewer_temperature: float = 0.0,
                      reviewer_top_p: float = 0.95,
                      reviewer_frequency_penalty: float = 0.0,
                      reviewer_presence_penalty: float = 0.0,
                      reviewer_stop: Any = None) -> str:
        
        # Payload a ser enviado al LLM, esto puede variar segun el proveedor/modelo/endpoint/api/etc.
        message_text = [
            {
                "role": "developer",
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
                frequency_penalty=reviewer_frequency_penalty,
                presence_penalty=reviewer_presence_penalty,
                stop=reviewer_stop
            )
            
            return (response.choices[0].message.content.strip() 
                    if response.choices 
                    else f"No correct answer from OpenAI!\n{response.text}")
            
        except Exception as e:
            return f"OpenAI failed to generate a review: {e}"

    def review_w_all_prompts(self, diff_codigo: str) -> str:
        prompts = self.config.get_prompts()
        responses = []
        
        for i, p in enumerate(prompts):    
            logger.info(f"Revisando prompt {i+1}/{len(prompts)}")
            review = self.review_single(prompt=p, diff_codigo=diff_codigo)
            responses.append(review)

        return responses
    
    def post_process_responses(self) -> list:
        raise NotImplementedError()