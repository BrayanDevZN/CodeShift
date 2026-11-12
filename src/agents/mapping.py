from src.logs import logger 
from .response.interface import ModelResponse
from src.utils.file import FileControl
from src.utils.tree import Tree
from src.prompt.prompts import Prompts
from ..schema import OutPutMapping
from .clean import clean_json
import json
import os
class MappingAgent(ModelResponse, Tree, FileControl): 

    def __init__(self)->None:
        super().__init__()
        Tree.__init__(self)  # Settings.__init__ não chama super(), então o Tree precisa ser iniciado aqui
        self.prompt:str = Prompts.mapping

    def cli(self) -> None:
        self._header("🗺  Mapeamento do projeto")

        print(f"\n{self.color.bold(self.color.blue('Modelo:'))} {self.color.green(self.name)}")
        print(self.color.cyan("\n⏳ Carregando, isso pode demorar um pouco...\n"))
        self.load()
        print(self.color.green(f"\n✔ Modelo {self.color.bold(self.name)} pronto!"))

        self.mapping()

        print(self.color.green(f"\n✔ Mapa salvo em {self.color.bold(os.path.abspath('.codeshift/mapping.json'))}"))


    def mapping(self) -> None:

        self.save_tree()
        self.show()
        resp  = json.dumps(self.load_tree())

        logger.info("Generanting Mapping...")

        content = []

        while True:

            content.append({"role": "user", "content": resp})

            raw = self.response(prompt=self.prompt, input=content)

            
            """
            {
            "action": {
                name: (quit, save, read),
                arg: se for save, deve ser [conteudo que ira ser salvo], read [caminho do arquivo], None
            },
            content: resultado da ultima execução
            }
            """

            response = OutPutMapping.model_validate_json(clean_json(raw))

            try:

                match response.action.name:
                    case "quit":
                        break 
                    case "read":
                        resp = self.read(response.action.arg, type="txt")

                    case "save":

                        resp = self.save(path=".codeshift/mapping.json", data=json.dumps(response.action.arg))
                        resp = f"saved {response.action.arg}"

                

            except  FileNotFoundError as error:
                resp = str(error)

            content.append({"role": "assistant", "content": raw})
            

            

            


if __name__ == "__main__":
    MappingAgent().cli()
