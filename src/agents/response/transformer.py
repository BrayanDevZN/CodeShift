from src.logs import logger
class ModelTransform:

    def __init__(self, name:str, temperature:float)-> None:
        self.name = name 
        self.temperature = temperature
        

        

    def load(self) -> None:

        if hasattr(self, "model"):
            return  # já carregado

        try:
            from transformers import pipeline
        except ImportError as error:
            raise ImportError("Modelo local requer: pip install 'codeshift[local]'") from error

        logger.info(f"Loading model {self.name}...")

        self.model = pipeline("text-generation", model=self.name)

        logger.success(f"{self.name} loaded with success")


    def response(self, prompt:str, input:list) -> str:

        logger.info(f"Generating response from model {self.name}...")

        input.insert(0, {"role": "system", "content":prompt})

        resp = self.model(input, temperature=self.temperature, do_sample=True)

        logger.success("Response generated with sucess")

        return resp[0]["generated_text"][-1]["content"]

