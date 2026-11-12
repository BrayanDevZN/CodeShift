from pathlib import Path
from src.utils.file import FileControl

BASE_DIR = Path(__file__).resolve().parent
REFACTOR = FileControl().read(path=BASE_DIR / "REFACTOR.md", type="txt")
