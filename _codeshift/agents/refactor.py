from _codeshift.logs import logger 
from .response.interface import ModelResponse
from _codeshift.utils.file import FileControl
from _codeshift.utils.tree import Tree
from _codeshift.prompt.prompts import REFACTOR
from ..schema import OutPutMapping
from .clean import clean_json
import json
import os
class RefactorAgent(ModelResponse, Tree, FileControl): 

    def __init__(self)->None:
        super().__init__()
        Tree.__init__(self)  # Settings.__init__ não chama super(), então o Tree precisa ser iniciado aqui
        self.prompt:str = REFACTOR

    def _info(self, label: str, value: str) -> None:
        print(f"  {self.color.gray('•')} {self.color.bold(self.color.blue(label + ':'))} {value}")

    def _progress(self) -> tuple[int, int]:
        """Conta (visited, total) de arquivos na árvore salva."""
        files = [n for n in self._walk(self.get_tree()) if n["type"] == "file"]
        visited = sum(1 for n in files if n.get("status") == "visited")
        return visited, len(files)

    def cli(self) -> None:
        c = self.color

        self._header("🛠  Refatoração do projeto")

        print()
        self._info("Modelo", c.green(self.name))
        self._info("Temperatura", c.yellow(self.temperature))
        self._info("Projeto", c.cyan(os.path.abspath(self.root)))

        print(c.cyan("\n⏳ Carregando o modelo, isso pode demorar um pouco...\n"))
        self.load()
        print(c.green(f"✔ Modelo {c.bold(self.name)} pronto!"))

        self._header("🔄  Executando")
        try:
            self.refactor()
        except KeyboardInterrupt:
            print(c.yellow("\n\n⚠ Interrompido pelo usuário. O progresso fica salvo na árvore."))
        except Exception as error:
            print(c.red(f"\n✖ Erro durante a refatoração: {error}"))
            raise
        else:
            print(c.green("\n✔ Refatoração concluída!"))
        finally:
            visited, total = self._progress()
            line = c.purple("─" * 50)
            print(f"\n{line}")
            print(f"  {c.bold('Resumo')}")
            print(f"  {c.green(f'{visited} visitados')} {c.gray('·')} {c.yellow(f'{total - visited} pendentes')} "
                  f"{c.gray('·')} {c.blue(f'{total} arquivos')}")
            print(f"  {c.gray('Árvore em')} {c.bold(os.path.abspath(self.file_path))}")
            print(f"{line}\n")

    BLOCKED = {".git", ".venv", "venv", "node_modules", "__pycache__", ".codeshift"}

    def _check_path(self, path: str) -> None:
        """Garante que o caminho fica dentro do projeto e fora das pastas proibidas."""
        norm = os.path.normpath(path)
        parts = norm.split(os.sep)
        if os.path.isabs(norm) or ".." in parts:
            raise PermissionError(f"Path outside the project: {path}")
        if any(part in self.BLOCKED for part in parts) or os.path.basename(norm).startswith(".env"):
            raise PermissionError(f"Path not allowed: {path}")

    def _files(self, status: str) -> list[str]:
        """Caminhos dos arquivos da árvore com o status dado."""
        return [n["path"] for n in self._walk(self.get_tree()) if n["type"] == "file" and n.get("status") == status]

    def _pending_hint(self) -> str:
        pending = self._files("pending")
        return "Valid pending paths: " + (", ".join(pending) if pending else "none")

    def _run_action(self, action) -> str:
        """Executa uma ação e devolve o texto do resultado."""
        arg = action.arg

        match action.name:

            case "save":
                self._check_path(arg[0])
                if os.path.exists(arg[0]):
                    return f"ERROR: {arg[0]} already exists. save only creates NEW files; use update to replace an existing file."
                self.save(path=arg[0], data=arg[1], type="txt")
                return f"Saved path {arg[0]}"

            case "read":
                self._check_path(arg)
                text = self.read(path=arg, type="txt")
                self._read.add(os.path.normpath(arg))
                return f"{arg}:\n{text}"

            case "update_status":
                self._check_path(arg[0])
                return f"Status updated: {self.update_status(name=arg[0], status=arg[1])} -> {arg[1]}"

            case "update":
                self._check_path(arg[0])
                self._check_path(arg[1])
                if os.path.normpath(arg[0]) not in self._read:
                    return f"ERROR: you have not read {arg[0]}. Use read first, then write its C++ from the real code."
                old, new = os.path.normpath(arg[0]), os.path.normpath(arg[1])
                if os.path.dirname(old) != os.path.dirname(new):
                    return f"ERROR: new_path must stay in the same folder as {arg[0]}. Use {os.path.splitext(arg[0])[0]}.cpp or .hpp."
                if os.path.splitext(new)[1] not in (".cpp", ".hpp", ".h"):
                    return f"ERROR: new_path must end in .cpp, .hpp or .h, got {arg[1]}."
                self.update(path=arg[0], new_path=arg[1], content=arg[2])
                return f"{arg[0]} updated for {arg[1]}"

        return f"Unknown action {action.name}"

    def refactor(self) -> None:
        """
        Resposta esperada do modelo (JSON):
        {
          "actions": [{"name": "...", "arg": ...}],
          "content": "resumo do que foi feito e do que vem a seguir"
        }

        name -> arg:
          read          -> "caminho"
          save          -> [caminho, conteudo]
          update        -> [caminho_atual, novo_caminho, novo_conteudo]
          update_status -> [caminho, "visited" | "pending"]
          quit          -> sem arg
        As actions rodam em ordem; cada uma é uma chamada separada.
        """

        report = ""   # resultado das ações do turno anterior
        notes = ""    # "content" que o modelo escreveu no turno anterior
        read_paths: set[str] = set()
        self._read: set[str] = set()

        while True:

            parts = []
            if report:
                parts.append(f"RESULT OF YOUR LAST ACTIONS:\n{report}")
            if notes:
                parts.append(f"WHAT YOU DID IN THE LAST TURN:\n{notes}")
            pending = self._files("pending")
            parts.append("PENDING FILES (use these exact paths, never paths from the examples):\n"
                         + ("\n".join(f"- {path}" for path in pending) if pending else "(none)"))
            parts.append(f"PROJECT TREE:\n{self.get_tree()}")

            raw = self.response(prompt=self.prompt, input=[{"role": "user", "content": "\n\n".join(parts)}])

            try:
                response = OutPutMapping.model_validate_json(clean_json(raw))
            except ValueError as error:
                report = f"Your last reply was not valid JSON in the required format. Answer again with ONLY the JSON object. {error}"
                continue

            results = []
            done = False
            marked: list[str] = []

            for action in response.actions:

                if action.name == "quit":
                    left = [path for path in self._files("pending") if path.endswith(".py")]
                    if left:
                        results.append("ERROR: you cannot quit yet, these Python files are still pending: " + ", ".join(left))
                    else:
                        done = True
                    break

                try:
                    result = self._run_action(action)
                    if action.name == "update_status" and action.arg[1] == "visited":
                        marked.append(action.arg[0])
                    if action.name == "read":
                        if action.arg in read_paths:
                            result += (f"\nHINT: you already read {action.arg}. Do NOT read it again. "
                                       "Now write its C++ version: update_status, then update.")
                        read_paths.add(action.arg)
                    results.append(result)
                except Exception as error:
                    results.append(f"ERROR in {action.name}: {error}. {self._pending_hint()}")
                    break  # as próximas ações dependem desta

            if done:
                return

            # um .py marcado como visited mas ainda existente não foi substituído por C++
            for path in marked:
                if path.endswith(".py") and os.path.exists(path):
                    self.update_status(name=path, status="pending")
                    results.append(
                        f"ERROR: {path} was NOT replaced, it still exists as Python, so it is pending again. "
                        f"Replace it now with update: [\"{path}\", \"<same path with .cpp or .hpp>\", \"<complete C++ code>\"]. "
                        "Do not use save for it."
                    )

            report = "\n".join(results)
            notes = response.content


if __name__ == "__main__":
    RefactorAgent().cli()
