from typing import Any


class Color:
    RESET = "\033[0m"
    BOLD = "\033[1m"

    # Standard and bright ANSI color codes
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    GRAY = "\033[90m"

    @staticmethod
    def red(value: Any) -> str:
        return f"{Color.RED}{value}{Color.RESET}"

    @staticmethod
    def green(value: Any) -> str:
        return f"{Color.GREEN}{value}{Color.RESET}"

    @staticmethod
    def yellow(value: Any) -> str:
        return f"{Color.YELLOW}{value}{Color.RESET}"

    @staticmethod
    def blue(value: Any) -> str:
        return f"{Color.BLUE}{value}{Color.RESET}"

    @staticmethod
    def purple(value: Any) -> str:
        return f"{Color.PURPLE}{value}{Color.RESET}"

    @staticmethod
    def cyan(value: Any) -> str:
        return f"{Color.CYAN}{value}{Color.RESET}"

    @staticmethod
    def gray(value: Any) -> str:
        return f"{Color.GRAY}{value}{Color.RESET}"

    @staticmethod
    def bold(value: Any) -> str:
        return f"{Color.BOLD}{value}{Color.RESET}"
