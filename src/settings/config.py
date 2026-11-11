
import os
from src.logs import logger
from .schema import AppConfig
from src.color import Color
from src.file import FileControl
from src.exceptions import ModelNotFound, TemperatureError, CliError, PathNotFound

class Settings(FileControl):

    def __init__(self)->None:

        
        self.color = Color() 

    def _header(self, title: str) -> None:
        line = self.color.purple("═" * 50)
        print(f"\n{line}\n  {self.color.bold(self.color.cyan(title))}\n{line}")

    def _prompt(self, text: str, hint: str = "") -> str:
        hint_str = f" {self.color.gray('(')}{self.color.yellow(hint)}{self.color.gray(')')}" if hint else ""
        return f"{self.color.cyan('❯')} {self.color.bold(text)}{hint_str}{self.color.cyan(':')} "

    def  get_config(self, path: str=".codeshift") -> dict:

        self.file = self.read(path + "/config.json")

        return AppConfig.model_validate(self.file).model_dump()


    def set_settings(self) -> None:

        data= {}

        self._header("⚙  Configuração do CodeShift")
        print(f"\n{self.color.bold(self.color.blue('Modelos disponíveis:'))}")
        MODELS = ["qwen3-coder-next:80b", "qwen2.5-coder:14b", "qwen2.5-coder:7b"]

        for number in range(len(MODELS)-1):
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

        get_path = input("\n" + self._prompt("Quer escolher um caminho pra pasta do modelo ser salva", "Y/n"))

        if not get_path in ["Y", "n"]:
            raise CliError("Invalid response")

        path = "./"

        if get_path == "Y":
            path = input(self._prompt("Digite o caminho"))

            if not os.path.exists(path):
                raise PathNotFound(f"Not found path {path}")

        data["path"] = path 

        

        self.BASE_DIR = ".codeshift" if path is not None else f"{path}/.codeshift"
        os.makedirs(self.BASE_DIR, exist_ok=True)

        self.save(self.BASE_DIR + "/config.json", data)

        print(self.color.green(f"\n✔ Configurações salvas em {self.color.bold(self.BASE_DIR)}"))
        logger.success(f"Settings saved with success")

    def update_settings(self) -> None:
        data = self.get_config()
        models = ["qwen3-coder-next:80b", "qwen2.5-coder:14b", "qwen2.5-coder:7b"]

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





    

    


        


