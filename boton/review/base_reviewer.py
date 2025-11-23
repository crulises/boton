from abc import ABC, abstractmethod
from boton.utils.config_parser import BotonConfigParser

class BaseReviewer(ABC):
    def __init__(self, prompt_file: str):
        self.prompt_file = prompt_file
        self.config = BotonConfigParser(archivo=prompt_file)
        self.pre_process_fns = []
        self.post_process_fns = []

    # adds fn to a fn list to be implemented and run into each class that inherits
    def add_pre_process_fn(self, fn: callable):
        self.pre_process_fns.append(fn)

    def add_post_process_fn(self, fn: callable):
        self.post_process_fns.append(fn)

    @abstractmethod
    def review(self, code_diff) -> str:
        pass

    @abstractmethod
    def run_pre_process_fns(self) -> dict:
        pass

    @abstractmethod
    def run_post_process_fns(self) -> dict:
        pass