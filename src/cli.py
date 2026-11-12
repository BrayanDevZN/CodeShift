import json
import os
import socket
import sys
from importlib.metadata import PackageNotFoundError, version
from urllib.parse import urlparse

from src import ui

CONFIG_FILE = ".codeshift/config.json"

# ─── Bonequinho ────────────────────────────────────────────────────────────
# Pixel art: cada caractere vira um "pixel" de 2 colunas.
#   B = corpo   E = olho   . = vazio
# Para trocar o desenho, edite só esta lista (todas as linhas com o mesmo tamanho).
MASCOT = [
    "..BBBBBB..",
    "BBBBBBBBBB",
    "BBEBBBBEBB",
    ".BBBBBBBB.",
    "..BB..BB..",
]
MASCOT_COLORS = {"B": ui.ORANGE, "E": ui.DARK}


def mascot_lines() -> list[str]:
    lines = []
    for row in MASCOT:
        line = ""
        for pixel in row:
            color = MASCOT_COLORS.get(pixel)
            line += ui.fg("██", color) if color else "  "
        lines.append(line)
    return lines


# ─── Dados do ambiente ─────────────────────────────────────────────────────
def _version() -> str:
    try:
        return version("codeshift")
    except PackageNotFoundError:
        return "dev"


def _short_path(path: str) -> str:
    home = os.path.expanduser("~")
    return "~" + path[len(home):] if path.startswith(home) else path


def read_config() -> dict | None:
    try:
        with open(CONFIG_FILE, encoding="utf-8") as file:
            return json.load(file)
    except (OSError, ValueError):
        return None


def server_url(config: dict) -> str | None:
    from dotenv import dotenv_values
    env_file = config.get("env_file") or ".env"
    return dotenv_values(env_file).get("url") if os.path.isfile(env_file) else None


def server_online(url: str) -> bool:
    parsed = urlparse(url)
    host, port = parsed.hostname, parsed.port or (443 if parsed.scheme == "https" else 80)
    try:
        with socket.create_connection((host, port), timeout=0.4):
            return True
    except OSError:
        return False


def status_lines() -> list[str]:
    config = read_config()
    if config is None:
        return [
            ui.fg("▲ Sem configuração", ui.YELLOW, bold=True),
            ui.fg("  use a opção 3 para começar", ui.GRAY),
        ]

    model = config["model"]
    name = model["name"].split("/")[-1]
    lines = [
        f"{ui.fg('Modelo  ', ui.GRAY)} {ui.fg(name, ui.GREEN, bold=True)} {ui.fg('· temp ' + str(model['temperature']), ui.GRAY)}"
    ]

    url = server_url(config)
    if url is None:
        lines.append(f"{ui.fg('Origem  ', ui.GRAY)} {ui.fg('modelo local (transformers)', ui.CYAN)}")
    elif server_online(url):
        lines.append(f"{ui.fg('Servidor', ui.GRAY)} {ui.fg('●', ui.GREEN)} {ui.fg(url, ui.CYAN)}")
    else:
        lines.append(f"{ui.fg('Servidor', ui.GRAY)} {ui.fg('●', ui.RED)} {ui.fg(url + ' (offline)', ui.RED)}")
    return lines


# ─── Telas ─────────────────────────────────────────────────────────────────
def banner() -> None:
    art = mascot_lines()
    info = [
        f"{ui.gradient('CodeShift', ui.ORANGE, ui.PURPLE)} {ui.fg('v' + _version(), ui.GRAY)}",
        ui.fg("Migração de código para C++ com IA", ui.PURPLE),
        *status_lines(),
        f"{ui.fg('Pasta   ', ui.GRAY)} {ui.fg(_short_path(os.getcwd()), ui.BLUE)}",
    ]
    info = info[:len(art)] if len(info) > len(art) else info + [""] * (len(art) - len(info))

    wide = ui.width() >= 64
    rows = [f"{a}   {i}" if wide else i for a, i in zip(art, info)]
    print()
    print(ui.box(rows, title="CodeShift" if not wide else "", color=ui.PURPLE))


MENU = [
    ("1", "Migrar projeto para C++", "substitui os .py por C++", ui.GREEN),
    ("2", "Carregar modelo agora", "prepara o modelo antes de usar", ui.PURPLE),
    ("3", "Configurar modelo", "escolhe modelo e temperatura", ui.CYAN),
    ("4", "Atualizar configurações", "muda uma configuração salva", ui.YELLOW),
    ("5", "Ver árvore do projeto", "lista pastas e arquivos", ui.BLUE),
    ("0", "Sair", "", ui.RED),
]

# modelo carregado pelo menu, reaproveitado na migração para não carregar duas vezes
_loaded = None


def show_menu() -> None:
    label_width = max(len(label) for _, label, _, _ in MENU)
    rows = []
    for key, label, hint, color in MENU:
        rows.append(f"{ui.badge(key, color)}  {ui.pad(ui.fg(label, color, bold=True), label_width)}  {ui.fg(hint, ui.GRAY)}")
    print()
    print(ui.box(rows, title="O que você quer fazer?", color=ui.GRAY))
    print(ui.fg("  digite o número e pressione Enter", ui.GRAY))
    print()


def clear() -> None:
    if sys.stdout.isatty():
        print("\033[2J\033[H", end="")


def pause() -> None:
    try:
        input(f"\n{ui.fg('↵', ui.GRAY)} {ui.fg('Enter para voltar ao menu', ui.GRAY)} ")
    except (EOFError, KeyboardInterrupt):
        print()


def ask(text: str) -> str:
    return input(ui.prompt(text)).strip()


# ─── Ações ─────────────────────────────────────────────────────────────────
def require_config() -> bool:
    if os.path.isfile(CONFIG_FILE):
        return True
    ui.warn("Nenhuma configuração encontrada. Use a opção 3 primeiro.")
    return False


def action_migrate() -> None:
    if not require_config():
        return

    print()
    print(ui.box([
        ui.fg("A migração SUBSTITUI os arquivos .py do projeto atual por C++.", ui.YELLOW, bold=True),
        ui.fg("Faça um commit ou backup antes de continuar.", ui.YELLOW),
    ], title="Atenção", color=ui.YELLOW))
    print()

    if ask("Continuar? (s/N)").lower() not in ("s", "sim", "y", "yes"):
        print(ui.fg("Cancelado.", ui.GRAY))
        return

    from src.agents.refactor import RefactorAgent
    agent = RefactorAgent()
    if _loaded is not None:
        agent.instance = _loaded.instance
    agent.cli()


def action_load() -> None:
    global _loaded
    if not require_config():
        return

    from src.agents.response.interface import ModelResponse
    model = ModelResponse()
    if model.start():
        _loaded = model


def action_configure() -> None:
    global _loaded
    from src.settings.config import Settings
    Settings().set_settings()
    _loaded = None


def action_update() -> None:
    global _loaded
    if not require_config():
        return
    from src.settings.config import Settings
    Settings().update_settings()
    _loaded = None


def action_tree() -> None:
    from src.utils.tree import Tree
    tree = Tree()
    tree.build()
    tree.show()


ACTIONS = {
    "1": action_migrate,
    "2": action_load,
    "3": action_configure,
    "4": action_update,
    "5": action_tree,
}


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] in ("-v", "--version"):
        print(f"codeshift {_version()}")
        return 0

    while True:
        clear()
        banner()
        show_menu()

        try:
            choice = ask("Escolha uma opção")
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if choice in ("0", "q", "exit", "sair"):
            break

        action = ACTIONS.get(choice)
        if action is None:
            ui.error("Opção inválida.")
            pause()
            continue

        try:
            action()
        except KeyboardInterrupt:
            print()
            ui.warn("Interrompido.")
        except Exception as error:
            print()
            ui.error(str(error))

        pause()

    print(f"\n{ui.gradient('Até logo!', ui.ORANGE, ui.PURPLE)} 👋\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
