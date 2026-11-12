import re
import shutil

RESET = "\033[0m"
_ANSI = re.compile(r"\033\[[0-9;]*m")

# Paleta (RGB)
ORANGE = (217, 119, 87)
PURPLE = (167, 139, 250)
CYAN = (103, 232, 249)
BLUE = (147, 197, 253)
GREEN = (134, 239, 172)
YELLOW = (253, 224, 71)
RED = (252, 165, 165)
GRAY = (113, 113, 122)
DARK = (28, 28, 36)

MIN_WIDTH, MAX_WIDTH = 50, 78


def fg(text, color: tuple[int, int, int], bold: bool = False) -> str:
    weight = "\033[1m" if bold else ""
    return f"{weight}\033[38;2;{color[0]};{color[1]};{color[2]}m{text}{RESET}"


def badge(text, color: tuple[int, int, int]) -> str:
    """Texto escuro sobre fundo colorido, como um botão."""
    return f"\033[48;2;{color[0]};{color[1]};{color[2]}m\033[38;2;{DARK[0]};{DARK[1]};{DARK[2]}m\033[1m {text} {RESET}"


def gradient(text: str, start: tuple[int, int, int], end: tuple[int, int, int], bold: bool = True) -> str:
    """Pinta cada letra numa cor entre start e end."""
    size = max(len(text) - 1, 1)
    out = []
    for i, char in enumerate(text):
        color = tuple(round(start[k] + (end[k] - start[k]) * i / size) for k in range(3))
        out.append(fg(char, color, bold))
    return "".join(out)


def vlen(text: str) -> int:
    return len(_ANSI.sub("", text))


def pad(text: str, size: int) -> str:
    return text + " " * max(size - vlen(text), 0)


def width() -> int:
    return max(MIN_WIDTH, min(shutil.get_terminal_size((80, 24)).columns, MAX_WIDTH))


def box(lines: list[str], title: str = "", color: tuple[int, int, int] = PURPLE) -> str:
    """Caixa com cantos arredondados. Cada item de `lines` é uma linha (pode ter cor)."""
    inner = width() - 4
    border = lambda s: fg(s, color)

    if title:
        label = f" {title} "
        top = border("╭─") + fg(label, color, bold=True) + border("─" * (inner + 1 - vlen(label)) + "╮")
    else:
        top = border("╭" + "─" * (inner + 2) + "╮")

    rows = [f"{border('│')} {pad(line, inner)} {border('│')}" for line in lines]
    bottom = border("╰" + "─" * (inner + 2) + "╯")
    return "\n".join([top, *rows, bottom])


def header(title: str) -> None:
    line = fg("━" * width(), PURPLE)
    print(f"\n{line}\n  {gradient(title, CYAN, PURPLE)}\n{line}")


def prompt(text: str, hint: str = "") -> str:
    hint_str = f" {fg('(' + hint + ')', GRAY)}" if hint else ""
    return f"{fg('❯', ORANGE, bold=True)} {fg(text, (228, 228, 231), bold=True)}{hint_str}{fg(':', ORANGE)} "


def ok(text: str) -> None:
    print(f"{fg('✔', GREEN, bold=True)} {fg(text, GREEN)}")


def warn(text: str) -> None:
    print(f"{fg('▲', YELLOW, bold=True)} {fg(text, YELLOW)}")


def error(text: str) -> None:
    print(f"{fg('✖', RED, bold=True)} {fg(text, RED)}")


def info(text: str) -> None:
    print(f"{fg('•', GRAY)} {text}")
