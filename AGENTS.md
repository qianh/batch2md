# Repository Guidelines

## Project Structure & Module Organization
Source code lives in `src/batch2md`, split into focused modules such as `cli.py` (argument parsing), `scanner.py` (directory traversal), `converters.py` (Doc→PDF→Markdown pipeline), and `output_manager.py` (artifact layout). Entry points sit in `main.py` and `__main__.py`, exposing the `batch2md` console script. Tests mirror the modules under `tests/`, with fixtures stored in `tests/fixtures/` and helper scripts in `scripts/` (e.g., `create_fixtures.py` and `check_deps.sh`). Keep documentation in the repo root (`README.md`, `TESTING.md`, `STATUS.md`).

## Build, Test & Development Commands
Use `uv sync --extra dev` (or `pip install -e ."[dev]"`) to install runtime plus tooling. Run `batch2md /path/to/documents --dry-run` to verify the CLI locally. Execute `pytest tests/ -v` for the full suite, `pytest -m unit` for fast checks, and `pytest --cov=batch2md --cov-report=html` before release. Static analysis relies on `black src tests` (line length 100), `flake8 src tests`, and `mypy src`. Scripts such as `bash scripts/check_deps.sh` help confirm LibreOffice and MinerU availability.

## Coding Style & Naming Conventions
Follow Black formatting (100-char lines, 4-space indents) and favor type hints on public functions. Name modules with lowercase underscores and keep test filenames in the `test_*.py` form already configured in `pyproject.toml`. Functions and variables should use descriptive snake_case. Prefer dataclasses or TypedDicts from `models.py` for shared data contracts instead of ad-hoc dicts.

## Testing Guidelines
Pytest is mandatory; respect existing markers (`unit`, `integration`, `slow`) and keep coverage ≥80% (see `TESTING.md`). Integration tests expect LibreOffice (`soffice`) and MinerU with downloaded models (`mineru download`). Test names should describe behavior (e.g., `test_scan_skips_non_docs`). Always add fixtures to `tests/fixtures/` and document large assets in git-lfs if needed.

## Commit & Pull Request Guidelines
Write imperative, descriptive commit subjects similar to `Fix missing shutil import in CLI`. Group logical changes per commit and keep diffs small. For PRs, include: purpose summary, key verification commands (tests, linters), linked issues, and screenshots/log excerpts when touching user-visible CLI output. Call out any skipped tests or unmet acceptance criteria so reviewers can respond quickly.

## Security & Configuration Tips
Do not commit MinerU model weights or generated PDFs. Store credentials for cloud storage conversions in environment variables, not code. When adding new configuration flags, document them in `README.md` and ensure defaults keep conversions sandboxed on local paths.
