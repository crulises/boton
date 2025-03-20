from abc import ABC, abstractmethod
from boton.utils.config_parser import BotonConfigParser

class BaseReviewer(ABC):
    def __init__(self, prompt_file: str):
        self.prompt_file = prompt_file
        self.config = BotonConfigParser(archivo=prompt_file)
        self.pre_process_fns = []
        self.post_process_fns = []

    def add_pre_process_fn(self, fn: callable):
        self.pre_process_fns.append(fn)

    def add_post_process_fn(self, fn: callable):
        self.post_process_fns.append(fn)

    @abstractmethod
    def review(self, prompt: str) -> str:
        pass
    
    @abstractmethod
    def pre_process_prompts(self) -> list:
        pass
    
    @abstractmethod
    def post_process_responses(self) -> list:
        pass