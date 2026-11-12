import json
import os
from _codeshift.logs import logger
from typing import Literal, Any


class FileControl:
    """Lê e salva arquivos no caminho exato recebido (relativo à pasta onde o comando roda)."""

    @staticmethod
    def read(path: str, type: Literal["json", "txt"] = "json") -> Any:

        logger.info(f"Reading {path}...")

        if not os.path.exists(path):
            raise FileNotFoundError(f"not exists {path}")

        with open(path, "r", encoding="utf-8") as file:

            logger.success("Read with success")
            return json.load(file) if type == "json" else file.read()

    @staticmethod
    def save(path: str, data: Any, type: Literal["json", "txt"] = "json") -> None:

        folder = os.path.dirname(path)
        if folder:
            os.makedirs(folder, exist_ok=True)

        logger.info(f"Saving {path}...")

        with open(path, "w", encoding="utf-8") as file:

            json.dump(data, file, ensure_ascii=False, indent=4) if type == "json" else file.write(data)

            logger.success("Saved with success")

    @staticmethod
    def update(path: str, new_path:str, content:str) -> None:

        if not os.path.exists(path):
            raise FileNotFoundError(f"Not exists {path}")

        logger.info(f"Updating {path}...")

        os.rename(path, new_path)

        with open(new_path, "w", encoding="utf-8") as f:

            f.write(content)

        logger.success(f"{path} updated with success")
