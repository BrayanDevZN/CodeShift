<p align="center">
  <img src="assets/logo.svg" alt="CodeShift" width="520">
</p>

<p align="center">
  Migre projetos <b>Python</b> para <b>C++</b> com um agente de IA, direto do terminal.
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=3776AB&labelColor=1c1c24">
  <img alt="C++" src="https://img.shields.io/badge/alvo-C%2B%2B20-00599C?style=for-the-badge&logo=cplusplus&logoColor=00599C&labelColor=1c1c24">
  <img alt="Versao" src="https://img.shields.io/badge/vers%C3%A3o-0.1.0-d97757?style=for-the-badge&logo=semver&logoColor=d97757&labelColor=1c1c24">
  <img alt="Status" src="https://img.shields.io/badge/status-alpha-f5c518?style=for-the-badge&logo=statuspage&logoColor=f5c518&labelColor=1c1c24">
  <img alt="CLI" src="https://img.shields.io/badge/interface-CLI-a78bfa?style=for-the-badge&logo=gnubash&logoColor=a78bfa&labelColor=1c1c24">
</p>

<p align="center">
  <img alt="Pydantic" src="https://img.shields.io/badge/Pydantic-v2-E92063?style=for-the-badge&logo=pydantic&logoColor=E92063&labelColor=1c1c24">
  <img alt="OpenAI" src="https://img.shields.io/badge/OpenAI%20SDK-compat%C3%ADvel-412991?style=for-the-badge&logo=openaigym&logoColor=a78bfa&labelColor=1c1c24">
  <img alt="LM Studio" src="https://img.shields.io/badge/LM%20Studio-local-1f6feb?style=for-the-badge&logo=lmstudio&logoColor=1f6feb&labelColor=1c1c24">
  <img alt="Transformers" src="https://img.shields.io/badge/Transformers-opcional-FFD21E?style=for-the-badge&logo=huggingface&logoColor=FFD21E&labelColor=1c1c24">
  <img alt="Qwen" src="https://img.shields.io/badge/Qwen-Coder-6f42c1?style=for-the-badge&logo=alibabacloud&logoColor=6f42c1&labelColor=1c1c24">
  <img alt="dotenv" src="https://img.shields.io/badge/dotenv-.env-3fb950?style=for-the-badge&logo=dotenv&logoColor=3fb950&labelColor=1c1c24">
</p>

---

## O que é

O **CodeShift** percorre o seu projeto Python arquivo por arquivo e pede a um modelo de código que escreva a versão equivalente em C++. Tudo roda num menu de terminal, e o modelo pode ser local (LM Studio, Ollama ou qualquer servidor compatível com a API da OpenAI) ou carregado via `transformers`.

> ⚠️ **Fase alpha.** A migração **substitui** os arquivos `.py` pelos arquivos C++. Faça um commit ou backup antes de rodar. Modelos pequenos (3B a 7B) ainda cometem erros: **revise e compile o resultado**.

## Instalação

Requer Python 3.10 ou mais novo.

```bash
git clone <url-do-repositorio> CodeShift
cd CodeShift

# recomendado: comando global isolado
pipx install .

# ou numa venv, em modo de desenvolvimento (as mudanças no código valem na hora)
python -m venv .venv && source .venv/bin/activate
pip install -e .
```

Para usar um modelo **local** pelo `transformers` (baixa o `torch`, é pesado):

```bash
pipx install ".[local]"      # ou: pip install -e ".[local]"
```

Depois de instalado, só o comando `codeshift` fica disponível. Não há API para importar.

## Configuração

### 1. Servidor do modelo

O jeito mais simples é o [LM Studio](https://lmstudio.ai):

```bash
lms server start
lms load qwen2.5-coder-7b-instruct --context-length 16384 -y
```

Crie um `.env` na pasta do projeto que você quer migrar:

```env
url = http://localhost:1234/v1
api_key = lm-studio
```

Sem a variável `url`, o CodeShift usa o modelo local via `transformers`.

### 2. Modelo e temperatura

Abra o `codeshift` e use a opção **Configurar modelo**. A escolha fica salva em `.codeshift/config.json`.

| Modelo | Observação |
|---|---|
| `Qwen/Qwen3-Coder-Next` | o mais capaz |
| `Qwen/Qwen2.5-Coder-14B-Instruct` | bom equilíbrio |
| `Qwen/Qwen2.5-Coder-7B-Instruct` | padrão para testar |
| `Qwen/Qwen2.5-Coder-3B-Instruct` | leve, erra mais |

Temperaturas entre `0.2` e `0.3` costumam gerar JSON mais estável.

## Uso

Entre na pasta do projeto Python e rode:

```bash
cd meu-projeto
codeshift
```

```
╭────────────────────────────────────────────────────────╮
│  ██████        CodeShift v0.1.0                        │
│  ██████████    Migração de código para C++ com IA      │
│  ████  ████    Modelo   Qwen2.5-Coder-7B · temp 0.2    │
│    ████████    Servidor ● http://localhost:1234/v1     │
│      ██  ██    Pasta    ~/meu-projeto                  │
╰────────────────────────────────────────────────────────╯
```

| Opção | O que faz |
|---|---|
| **1** Migrar projeto para C++ | Roda o agente e substitui os `.py` por C++ |
| **2** Carregar modelo agora | Prepara o modelo antes de usar |
| **3** Configurar modelo | Escolhe modelo, temperatura e arquivo `.env` |
| **4** Atualizar configurações | Muda uma configuração já salva |
| **5** Ver árvore do projeto | Lista pastas e arquivos |

`codeshift --version` mostra a versão.

## Como funciona

```
          ┌──────────────────────────────────────────────┐
          │              .codeshift/tree.json            │
          │  árvore binária: pastas, arquivos e status   │
          └───────────────┬──────────────────────────────┘
                          │ a cada turno
                          ▼
   ┌──────────┐    árvore + resultado    ┌──────────────┐
   │ CodeShift│ ───────────────────────▶ │    Modelo    │
   │  (loop)  │ ◀─────────────────────── │  (Qwen etc.) │
   └────┬─────┘     JSON com ações       └──────────────┘
        │ executa: read · save · update · update_status · quit
        ▼
   arquivos do projeto
```

1. O CodeShift monta uma **árvore binária** do projeto (`left` = primeiro filho, `right` = próximo irmão). Cada arquivo tem o status `pending` ou `visited`.
2. A cada turno o modelo recebe a lista de arquivos pendentes, a árvore e o resultado da rodada anterior.
3. Ele responde com **um JSON** de ações, executadas em ordem:

| Ação | `arg` | Efeito |
|---|---|---|
| `read` | `"caminho"` | devolve o texto do arquivo |
| `save` | `["caminho", "conteúdo"]` | cria um arquivo novo (ex.: um `.hpp`) |
| `update` | `["caminho", "novo_caminho", "novo_conteúdo"]` | troca o conteúdo e renomeia (`.py` → `.cpp`) |
| `update_status` | `["caminho", "visited"]` | marca o arquivo como tratado |
| `quit` | — | encerra |

4. O agente só termina quando não sobra nenhum `.py` pendente. O código recusa caminhos fora do projeto e pastas como `.git`, `.venv` e `.env*`.

O prompt completo do agente está em [`src/prompt/REFACTOR.md`](src/prompt/REFACTOR.md).

## Estrutura

```
CodeShift/
├── assets/logo.svg
├── pyproject.toml
├── src/
│   ├── cli.py              # menu e telas do terminal
│   ├── ui.py               # cores, caixas e componentes visuais
│   ├── cmd.py              # roda comandos no terminal
│   ├── schema.py           # modelos pydantic (config e ações)
│   ├── agents/
│   │   ├── refactor.py     # loop do agente
│   │   ├── clean.py        # limpa cercas de markdown do JSON
│   │   └── response/       # OpenAI-compatível e transformers
│   ├── prompt/REFACTOR.md  # prompt do agente
│   ├── settings/config.py  # configuração e .env
│   └── utils/              # arquivos e árvore binária
└── tests/estoque/          # projeto Python de exemplo (5 arquivos)
```

## Limitações conhecidas

- O resultado **não é compilado** automaticamente. Pode haver erros de include, tipos e consistência entre arquivos.
- Modelos de 7B ou menos podem ignorar o formato de saída ou reescrever estruturas em vez de portá-las.
- O contexto do modelo precisa caber o prompt, a árvore e o arquivo lido. Arquivos muito grandes podem estourar.
- Bibliotecas sem equivalente direto (ex.: `torch`) precisam de adaptação manual.

## Próximos passos

- [ ] Compilar cada arquivo com `g++ -fsyntax-only` e devolver o erro ao modelo
- [ ] Passar os headers já gerados como contexto nos arquivos seguintes
- [ ] Opção de gravar o C++ numa pasta separada, sem tocar nos `.py`
- [ ] Publicar no PyPI

## Testando com o exemplo

```bash
cp -r tests/estoque /tmp/estoque && cd /tmp/estoque
codeshift
```

O projeto de exemplo é um controle de estoque pequeno, com 5 arquivos que dependem uns dos outros.
