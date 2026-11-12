from pathlib import Path
from _codeshift.utils.file import FileControl

BASE_DIR = Path(__file__).resolve().parent
REFACTOR = FileControl().read(path=BASE_DIR / "REFACTOR.md", type="txt")
