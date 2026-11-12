import os
from src.color import Color
from src.utils.file import FileControl
from src.logs import logger

IGNORE = {".git", ".venv", "__pycache__", ".codeshift", "node_modules"}


class Node:
    def __init__(self, name: str, path: str, is_dir: bool) -> None:
        self.name = name
        self.path = path
        self.is_dir = is_dir
        self.left: "Node | None" = None   # primeiro filho
        self.right: "Node | None" = None  # próximo irmão

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "path": self.path,
            "type": "dir" if self.is_dir else "file",
            "left": self.left.to_dict() if self.left else None,
            "right": self.right.to_dict() if self.right else None,
        }


class Tree(FileControl):
    """Árvore binária (filho-esquerda / irmão-direita) das pastas e arquivos."""

    def __init__(self, root: str = ".") -> None:
        self.color = Color()
        self.root = root
        self.file_path = ".codeshift/tree.json"
        self.head: Node | None = None
        self.dirs = 0
        self.files = 0

    def _build(self, path: str, name: str) -> Node:
        node = Node(name, path, os.path.isdir(path))
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
