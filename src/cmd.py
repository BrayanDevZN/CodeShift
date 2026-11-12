import subprocess


def run(command: str) -> str:
    """Roda um comando no terminal, mostra a saída enquanto ele executa e devolve ela em str."""

    process = subprocess.Popen(
        command, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )

    output = ""
    for line in process.stdout:
        print(line, end="")
        output += line

    process.wait()
    return output
