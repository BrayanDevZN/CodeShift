import re

# ```json ... ``` ou ``` ... ```
_FENCE = re.compile(r"```[a-zA-Z0-9_-]*\s*(.*?)```", re.DOTALL)


def clean_json(text: str) -> str:
    """Remove cercas de markdown e texto solto em volta, deixando só o objeto JSON."""

    text = text.strip()

    fenced = _FENCE.search(text)
    if fenced:
        text = fenced.group(1).strip()

    # cerca aberta e nunca fechada (resposta cortada)
    text = text.removeprefix("```json").removeprefix("```").strip()

    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end > start:
        text = text[start:end + 1]

    return text.strip()
