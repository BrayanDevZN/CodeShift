
import os
from _codeshift.logs import logger
from _codeshift.schema import AppConfig
from _codeshift.color import Color
from _codeshift import ui
from _codeshift.utils.file import FileControl
from _codeshift.exceptions import ModelNotFound, TemperatureError, PathNotFound, NotFoundEnv
from dotenv import load_dotenv
DEFAULT_ENV_FILE = ".env"

AVAILABLE_MODELS = [
    "Qwen/Qwen3-Coder-Next",
    "Qwen/Qwen2.5-Coder-14B-Instruct",
    "Qwen/Qwen2.5-Coder-7B-Instruct",
    "Qwen/Qwen2.5-Coder-3B-Instruct",
]

class Settings(FileControl):

    def __init__(self)->None:

        
        self.color = Color() 

    def _header(self, title: str) -> None:
        ui.header(title)

    def _prompt(self, text: str, hint: str = "") -> str:
        return ui.prompt(text, hint)

    def get_config(self) -> dict:

        self.file = self.read(".codeshift/config.json")

        return AppConfig.model_validate(self.file).model_dump()


    def set_settings(self) -> None:

        data= {}

        self._header("⚙  Configuração do CodeShift")
        print(f"\n{self.color.bold(self.color.blue('Modelos disponíveis:'))}")
        MODELS = AVAILABLE_MODELS

        for number in range(len(MODELS)):
            print(f"  {self.color.yellow(f'[{number}]')} {self.color.green(MODELS[number])}")
        print()

        model = input(self._prompt("Digite o número do modelo"))
        model = int(model)

        temperature = float(input(self._prompt("Escolha uma temperatura", "0.2 a 0.9")))

        if model > len(MODELS) -1:
            raise ModelNotFound(f"Not found model")

        if 0.2 > temperature or temperature > 0.9:
            raise TemperatureError(f"Invalid temperature {temperature}")

        data["model"] = {
            "name": MODELS[model],
            "temperature": temperature
        }

        env_file = input(self._prompt("Caminho do arquivo .env", "opcional, Enter para pular")).strip()

        if env_file:
            env_file = os.path.abspath(os.path.expanduser(env_file))

            if not os.path.isfile(env_file):
                raise PathNotFound(f"Not found env file {env_file}")

            data["env_file"] = env_file
        else:
            data["env_file"] = DEFAULT_ENV_FILE

        self.save(".codeshift/config.json", data)

        print(self.color.green(f"\n✔ Configurações salvas em {self.color.bold(os.path.abspath('.codeshift/config.json'))}"))
        logger.success(f"Settings saved with success")

    def update_settings(self) -> None:
        data = self.get_config()
        models = AVAILABLE_MODELS

        self._header("✎  Atualizar configurações")

        while True:
            option = input(
                f"\n{self.color.bold('Configurações do Modelo')} "
                f"({self.color.yellow('name')}, {self.color.yellow('temperature')}, {self.color.red('exit')})\n"
                + self._prompt("Qual você deseja alterar")
            ).strip().lower()

            if option == "exit":
                break

            match option:
                case "name":
                    print(f"\n{self.color.bold(self.color.blue('Modelos disponíveis:'))}")
                    for idx, m in enumerate(models, start=1):
                        print(f"  {self.color.yellow(f'[{idx}]')} {self.color.green(m)}")

                    choice = input("\n" + self._prompt("Digite o número do modelo")).strip()

                    if not choice.isdigit() or not (1 <= int(choice) <= len(models)):
                        raise ModelNotFound(f"Not found model index {choice}")

                    selected_model = models[int(choice) - 1]
                    data["model"]["name"] = selected_model
                    print(self.color.green(f"✔ Modelo alterado para {self.color.bold(selected_model)}"))
                    break

                case "temperature":
                    temperature = float(input(self._prompt("Digite uma temperatura", "0.2 a 0.9")))

                    if not (0.2 <= temperature <= 0.9):
                        raise TemperatureError(f"Invalid temperature {temperature}")

                    data["model"]["temperature"] = temperature
                    print(self.color.green(f"✔ Temperatura alterada para {self.color.bold(temperature)}"))
                    break

                case _:
                    print(self.color.red("✘ Não existe essa opção."))

        self.save(".codeshift/config.json", data)

        logger.success(f"Saved with success")

        return data

    def get_envs(self) -> dict:

        NAMES = ["url", "api_key"]

        data = self.get_config()
        envs = {}
        load_dotenv(data.get("env_file") or DEFAULT_ENV_FILE)

        for name in NAMES:

            envs[name] = os.getenv(name)

        return envs

        

        

    

    

