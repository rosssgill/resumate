# Resumate

A declarative Python CLI tool that generates resumes from [JSON Resume](https://jsonresume.org/schema) files using Typst templates with optional AI feedback.

## Setup

Requires [uv](https://docs.astral.sh/uv/).

```sh
uv sync
```

## Writing your resume

Resumes must follow the [JSON Resume schema](https://jsonresume.org/schema), with two differences:

- Dates must be full ISO dates (`2023-01-01`). Only the month and year are shown.
- `**double asterisks**` make text bold, e.g. in highlights and project descriptions.

Leave out `endDate` for a current role to show "Present".

## Compiling to PDF

```sh
uv run src/main.py compile cv.json
```

This writes `cv.pdf` next to the input. If the resume doesn't fit, the text shrinks from 11pt down to 10pt; if it still doesn't fit, the PDF is written anyway with a warning.

| Option | Default | |
|---|---|---|
| `--output PATH` | input path with `.pdf` | Where to write the PDF |
| `--max-pages N` | `1` | Page limit to fit within |
| `--paper` | `a4` | `a4` or `us-letter` |

## Configuration

Settings are read from, in order of priority: command-line flags, environment variables, a `.env` in the current directory, then `~/.config/resumate/.env`. Resumate's own settings use a `RESUMATE_` prefix:

| Variable | Default | |
|---|---|---|
| `RESUMATE_MODEL` | none | Model for `coach` |
| `RESUMATE_PAPER` | `a4` | Default paper size |
| `RESUMATE_MAX_PAGES` | `1` | Default page limit |
| `RESUMATE_DEFAULT_FONT_SIZE` | `11` | Starting text size in pt |
| `RESUMATE_MIN_FONT_SIZE` | `10` | Smallest text size when fitting |
| `RESUMATE_FONT_SIZE_STEP` | `0.25` | How much to shrink per attempt |

The same files can hold provider settings such as API keys. Keep keys in `~/.config/resumate/.env`, outside any repository, so they can't be committed by accident.

## AI feedback

```sh
uv run src/main.py coach cv.json [--job posting.txt | --job https://...]
```

Prints feedback with suggested rewrites, each shown next to the original text. Your file is never changed. Pass `--job` to tailor the feedback to a job posting; if a site blocks fetching the URL, save the posting to a file instead.

Rewrites are told never to invent facts and to use `[placeholders]` instead, but models can still slip, so check each rewrite before using it.

### Choosing a model

Bring your own model: set `RESUMATE_MODEL` (or pass `--model`) to any [pydantic-ai model string](https://pydantic.dev/docs/ai/models/overview/). There is no default, so your resume is never sent anywhere you didn't choose.

**Hosted API**: set the provider's API key. Your resume, including contact details, is sent to that provider.

```sh
# ~/.config/resumate/.env
ANTHROPIC_API_KEY=sk-ant-...
RESUMATE_MODEL=anthropic:claude-sonnet-5-5
```

OpenAI (`openai:...`, `OPENAI_API_KEY`) and Google (`google:...`, `GOOGLE_API_KEY`) work the same way. A Claude.ai subscription does not include API access; create a key at [console.anthropic.com](https://console.anthropic.com).

**Local model with Ollama**: free, and your resume never leaves your machine.

```sh
# ~/.config/resumate/.env
OLLAMA_BASE_URL=http://localhost:11434/v1
RESUMATE_MODEL=ollama:hf.co/unsloth/Qwen3.8-27B-GGUF:UD-Q3_K_XL
```

Ollama's default 4,096-token context is too small: reasoning models think for 3–15K tokens before answering, and the run fails with a token limit error. Raise it with `sudo systemctl edit ollama`:

```ini
[Service]
Environment="OLLAMA_CONTEXT_LENGTH=32768"
Environment="OLLAMA_FLASH_ATTENTION=1"
Environment="OLLAMA_KV_CACHE_TYPE=q4_0"
```

Pick a model build that fits entirely in your GPU's memory, alongside about 1.5 GB for the context and whatever your desktop uses. Run `ollama ps` while it's working: anything other than `100% GPU` means part of the model is on the CPU and it will be several times slower. As a reference, Qwen3.8 27B `UD-Q3_K_XL` (13 GB) on a 16 GB Radeon RX 9070 runs at about 30 tokens/s, taking 2–5 minutes per review.

## Development

```sh
uv run pytest
make lint
make format
```

The bundled Font Awesome fonts in `src/fonts/` are licensed under the SIL OFL 1.1; see `src/fonts/FONTAWESOME-LICENSE.txt`.
