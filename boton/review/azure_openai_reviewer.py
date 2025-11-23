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
        # this is a dict bc for now comment size it's not a problem but if you run into multiple responses, the dict makes it easier to have multiple comments. on top of this you could have lists as the values and make each value of the list be a diff comment
        self.responses = {
            "line": '',
            "file": 'Placeholder for future implementation',
            "project": 'Placeholder for future implementation',
        }
        self.add_pre_process_fn(self.pre_process_line)
        self.add_post_process_fn(self.post_process_special_chars)
    
    def pre_process_line(self) -> str:
        base = self.config.get_prompts("tipo", "base")
        reglas = self.config.get_prompts("tipo", "regla")
        return "\n".join(base + reglas)
    
    # re think when implementing other scopes, the append won't cut it
    def run_pre_process_fns(self) -> dict:
        prompt_list = []
        for fn in self.pre_process_fns:
            result = fn()
            prompt_list.append(result)

        prompts = {
            "line": prompt_list[0],
            "file": 'Placeholder for future implementation',
            "project": 'Placeholder for future implementation',
        }
        return prompts

    def post_process_special_chars(self, responses) -> None:
        for key, value in responses.items():
            if isinstance(value, str):
                cleaned = value.replace('\"',"'")
                responses[key] = cleaned

    def run_post_process_fns(self, responses) -> dict:
        for fn in self.post_process_fns:
            fn(responses)

        return responses

    def review_single(self,  
                      prompt: str, 
                      code_diff: str, 
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
                "content": code_diff
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

    def merge_responses(self, responses: dict) -> str:
        merged_parts = []

        for key, value in responses.items():
            if not value:
                continue  # skip None / empty strings
            
            # Normalize to string
            text = str(value).strip()
            
            # Skip empty text
            if text and "Placeholder" not in text:
                merged_parts.append(text)

        # Join each section with two new lines
        return "\n\n".join(merged_parts)

    # future work: add other scopes
    def review(self, code_diff: str) -> str:
        prompts = ""
        
        """
        for i, p in enumerate(prompts):    
            logger.info(f"Revisando prompt {i+1}/{len(prompts)}")
            review_result = self.review_single(prompt=p, code_diff=code_diff)
            responses.append(review)
        """
        prompts = self.run_pre_process_fns()

        line_review_result = self.review_single(prompts["line"], code_diff)

        self.responses["line"] = line_review_result
        
        clean_responses = self.run_post_process_fns(self.responses)

        merged_responses = self.merge_responses(clean_responses)

        return merged_responses
