import json 
import os 
from src.logs import logger

class FileControl:

    @staticmethod
    def read(path:str) -> dict:

        logger.info(f"Reading {path}...")

        if not os.path.exists(path):
            raise FileNotFoundError(f"not exists {path}")

        with open(path, "r", encoding="utf-8") as file:

            logger.success(f"Read with success")
            return json.load(file)


    @staticmethod
    def save(path:str, data:dict) -> None:

        logger.info(f"Saving {path}...")


        with open(path, "w", encoding="utf-8") as file:

            json.dump(data, file, ensure_ascii=False, indent=4)
            logger.success(f"Saved with success")