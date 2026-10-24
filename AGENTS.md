# Resumate

Python CLI that renders a [JSON Resume](https://jsonresume.org/schema) file to a PDF with Typst, plus an optional LLM `coach` command. See `README.md` for usage.

## Commands

```sh
uv sync                                # install
uv run pytest                          # test
make lint                              # ruff check, ruff format --check, ty check
make format                            # fix lint and format
uv run src/main.py compile cv.json     # run the CLI
```

Add/remove dependencies with `uv add` and `uv remove`, never by manually editing `pyproject.toml`.

## Layout

| Path | Purpose |
|---|---|
| `src/main.py` | Typer CLI: `compile` and `coach` |
| `src/models.py` | Pydantic models for the JSON Resume schema |
| `src/render.py` | Typst rendering and shrink-to-fit |
| `src/coach.py` | pydantic-ai agent for resume feedback |
| `src/core/config.py` | `Settings`, read from `RESUMATE_*` env vars and `./.env` |
| `src/templates/cv.typ` | CV template; reads the resume via `sys.inputs` |
| `src/fonts/` | Bundled fonts |

## Conventions

- **Resume format:** stay compatible with JSON Resume. Unknown fields are kept, not dropped. Dates must be full `YYYY-MM-DD`. `**bold**` is the only inline markup.
- **Settings:** add new options to `Settings` with a `RESUMATE_` env var. CLI flags override env vars, which override `.env`. Document new options in the README table and `.env.example`.
- **Template:** size everything relative to `font-size` (multiples or `em`) so shrink-to-fit scales the whole layout. System fonts are ignored for reproducible output, so any new font must be added to `src/fonts/`.
- **CLI output:** use `typer.echo`/`typer.secho`; `print` is a lint error. Errors go to stderr and exit 1.
- **Coach:** must never invent facts about the user. Rewrites may only rephrase, reorder, merge or cut; new specifics are `[placeholders]`. There is no default model, so a resume is only sent to a provider the user chose.

## Tests

- Tests import from `src` directly (`from models import Resume`).
- `tests/conftest.py` isolates every test from `RESUMATE_*` env vars and runs it in a temp directory.
- Never call real LLMs or the network: use pydantic-ai's `TestModel`/`FunctionModel` and monkeypatch `httpx.get`.

## Privacy

- `.env` holds API keys and must never be committed.

## Git

Conventional commits: `feat:`, `fix:`, `docs:`, `chore:`. Never skip pre-commit hooks.
