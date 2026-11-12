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

    def start(self) -> None:

        if isinstance(self.instance, ModelTransform):
            self.instance.start()

    def load(self) -> None:

        if isinstance(self.instance, ModelTransform):
            self.instance.load()

    def response(self, prompt:str, input:list) -> str:
        args = locals()
        del args["self"]
        return self.instance.response(**args)
    

    