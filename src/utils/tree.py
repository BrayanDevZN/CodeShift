import os
from typing import Literal
from src.color import Color
from src.utils.file import FileControl
from src.exceptions import AmbiguousFile
from src.logs import logger

Status = Literal["pending", "visited"]

IGNORE = {".git", ".venv", "__pycache__", ".codeshift", "node_modules"}


class Node:
    def __init__(self, name: str, path: str, is_dir: bool, status: Status = "pending") -> None:
        self.name = name
        self.path = path
        self.is_dir = is_dir
        self.status: Status = status  # só faz sentido para arquivos
        self.left: "Node | None" = None   # primeiro filho
        self.right: "Node | None" = None  # próximo irmão

    def to_dict(self) -> dict:
        data = {
            "name": self.name,
            "path": self.path,
            "type": "dir" if self.is_dir else "file",
        }
        if not self.is_dir:
            data["status"] = self.status
        data["left"] = self.left.to_dict() if self.left else None
        data["right"] = self.right.to_dict() if self.right else None
        return data


class Tree(FileControl):
    """Árvore binária (filho-esquerda / irmão-direita) das pastas e arquivos."""

    def __init__(self, root: str = ".") -> None:
        self.color = Color()
        self.root = root
        self.file_path = ".codeshift/tree.json"
        self.head: Node | None = None
        self.dirs = 0
        self.files = 0
        self._old_status: dict[str, Status] = {}

    @staticmethod
    def _walk(data: dict | None):
        """Percorre o dict da árvore (filho-esquerda / irmão-direita) sem recursão."""
        stack = [data]
        while stack:
            node = stack.pop()
            if node is None:
                continue
            yield node
            stack.append(node["right"])
            stack.append(node["left"])

    def _build(self, path: str, name: str) -> Node:
        is_dir = os.path.isdir(path)
        node = Node(name, path, is_dir, self._old_status.get(os.path.normpath(path), "pending"))
        if not node.is_dir:
            self.files += 1
            return node
        self.dirs += 1
        entries = sorted(
            (e for e in os.listdir(path) if e not in IGNORE),
            key=lambda e: (not os.path.isdir(os.path.join(path, e)), e.lower()),
        )
        prev: Node | None = None
        for entry in entries:
            child = self._build(os.path.join(path, entry), entry)
            if prev is None:
                node.left = child
            else:
                prev.right = child
            prev = child
        return node

    def build(self) -> Node:
        if not os.path.exists(self.root):
            logger.error(f"Root not found: {self.root}")
            raise FileNotFoundError(f"Not exists {self.root}")
        logger.info(f"Scanning {self.color.bold(os.path.abspath(self.root))}...")
        self.dirs = self.files = 0
        # guarda o status dos arquivos já salvos, para o rebuild não zerar tudo
        self._old_status = {}
        if os.path.exists(self.file_path):
            self._old_status = {
                os.path.normpath(n["path"]): n["status"]
                for n in self._walk(self.load_tree())
                if n["type"] == "file" and "status" in n
            }
        self.head = self._build(self.root, os.path.basename(os.path.abspath(self.root)))
        logger.success(
            f"Tree built: {self.color.blue(self.dirs)} folders, {self.color.green(self.files)} files"
        )
        return self.head

    def save_tree(self) -> dict:
        data = self.build().to_dict()
        self.save(self.file_path, data)
        logger.success(f"Tree saved in {self.color.bold(self.file_path)}")
        return data

    def load_tree(self) -> dict:
        return self.read(self.file_path)

    def get_tree(self, refresh: bool = False) -> dict:
        if refresh or not os.path.exists(self.file_path):
            logger.warning(f"Building tree: {self.color.bold(self.file_path)} not found or refresh requested")
            return self.save_tree()
        return self.load_tree()

    def update_status(self, name: str, status: Status = "visited") -> str:
        """Procura o arquivo pelo nome (ou caminho) na árvore salva e atualiza o status.

        Retorna o caminho do arquivo atualizado.
        """
        data = self.get_tree()
        target = os.path.normpath(name)

        matches = [
            n for n in self._walk(data)
            if n["type"] == "file" and (n["name"] == name or os.path.normpath(n["path"]) == target)
        ]

        if not matches:
            logger.error(f"File not found in tree: {name}")
            raise FileNotFoundError(f"Not found in tree: {name}")
        if len(matches) > 1:
            paths = ", ".join(n["path"] for n in matches)
            raise AmbiguousFile(f"{name} matches more than one file: {paths}. Use the full path")

        matches[0]["status"] = status
        self.save(self.file_path, data)
        logger.success(f"{self.color.bold(matches[0]['path'])} -> {status}")
        return matches[0]["path"]

    def show(self) -> None:
        if self.head is None:
            self.build()
        line = self.color.purple("═" * 50)
        print(f"\n{line}\n  {self.color.bold(self.color.cyan('🌳  Árvore do projeto'))}\n{line}")
        print(self.color.bold(self.color.cyan(self.head.name + "/")))
        self._show(self.head.left, "")
        print(
            f"\n{self.color.blue(f'{self.dirs} pastas')} {self.color.gray('·')} "
            f"{self.color.green(f'{self.files} arquivos')}\n"
        )

    def _show(self, node: "Node | None", prefix: str) -> None:
        while node is not None:
            last = node.right is None
            branch = "└── " if last else "├── "
            label = self.color.blue(node.name + "/") if node.is_dir else self.color.green(node.name)
            print(f"{self.color.gray(prefix + branch)}{label}")
            if node.is_dir:
                self._show(node.left, prefix + ("    " if last else "│   "))
            node = node.right


if __name__ == "__main__":
    t = Tree()
    t.save_tree()
    t.show()
