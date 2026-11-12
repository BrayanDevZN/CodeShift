from src.settings.config import Settings
from .openai import ModelOpenAi
from .transformer import ModelTransform

class ModelResponse(Settings):

    def __init__(self)->None:
        super().__init__()

        config = self.get_config()
        self.name = config["model"]["name"]
        self.temperature = config["model"]["temperature"]

        self.secrets = self.get_envs()
        self._get_instance()


    def _get_instance(self) -> None:

        if self.secrets["url"] is not None:

            self.instance = ModelOpenAi(url=self.secrets["url"], key=self.secrets["api_key"],
                                        name=self.name, temperature=self.temperature)

        else:

            self.instance = ModelTransform(name=self.name, temperature=self.temperature)

    def start(self) -> bool:
        """Pergunta se quer carregar o modelo agora. Devolve True se o modelo ficou pronto."""

        c = self.color
        self._header("🤖  Carregar modelo")
        print(f"\n{c.bold(c.blue('Modelo:'))} {c.green(self.name)}")
        print(f"{c.bold(c.blue('Temperatura:'))} {c.yellow(self.temperature)}\n")

        if not isinstance(self.instance, ModelTransform):
            print(c.green(f"✔ Usando o servidor {self.secrets['url']}: não precisa carregar aqui."))
            print(c.gray("  Se o modelo não estiver carregado no servidor (LM Studio), carregue lá."))
            return True

        while True:
            answer = input(self._prompt("Quer carregar o modelo agora", "Y/n")).strip().lower()

            if answer in ("y", "yes", "s", "sim", ""):
                print(c.cyan("\n⏳ Carregando, isso pode demorar um pouco...\n"))
                self.load()
                print(c.green(f"\n✔ Modelo {c.bold(self.name)} pronto!"))
                return True

            if answer in ("n", "no", "nao", "não"):
                print(c.yellow("\n⚠ Modelo não carregado."))
                return False

            print(c.red("✘ Resposta inválida, digite Y ou n."))

    def load(self) -> None:

        if isinstance(self.instance, ModelTransform):
            self.instance.load()

    def response(self, prompt:str, input:list) -> str:
        args = locals()
        del args["self"]
        return self.instance.response(**args)
    

    