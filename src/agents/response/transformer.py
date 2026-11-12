from transformers import pipeline
from src.logs import logger
class ModelTransform:

    def __init__(self, name:str, temperature:float)-> None:
        self.name = name 
        self.temperature = temperature
        

        

    def start(self) -> bool:
        self._header("🤖  Carregar modelo")
        print(f"\n{self.color.bold(self.color.blue('Modelo:'))} {self.color.green(self.name)}")
        print(f"{self.color.bold(self.color.blue('Temperatura:'))} {self.color.yellow(self.temperature)}\n")

        while True:
            answer = input(self._prompt("Quer carregar o modelo agora", "Y/n")).strip().lower()

            if answer in ("y", "yes", "s", "sim", ""):
                print(self.color.cyan("\n⏳ Carregando, isso pode demorar um pouco...\n"))
                self.load()
                print(self.color.green(f"\n✔ Modelo {self.color.bold(self.name)} pronto!"))
                return True

            if answer in ("n", "no", "nao", "não"):
                print(self.color.yellow("\n⚠ Modelo não carregado."))
                return False

            print(self.color.red("✘ Resposta inválida, digite Y ou n."))

    def load(self) -> None:

        logger.info(f"Loading model {self.name}...")

        self.model = pipeline("text-generation", model=self.name)

        logger.success(f"{self.name} loaded with success")


    def response(self, prompt:str, input:list) -> str:

        logger.info(f"Generating response from model {self.name}...")

        input.insert(0, {"role": "system", "content":prompt})

        resp = self.model(input, temperature=self.temperature, do_sample=True)

        logger.success("Response generated with sucess")

        return resp[0]["generated_text"][-1]["content"]

