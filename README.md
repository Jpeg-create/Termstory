# TermStory

A personal developer memory engine — tracks shell history to rebuild the story of your projects.

## Install

```bash
curl -fsSL https://raw.githubusercontent.com/bitflicker64/Termstory/main/install.sh | bash
```

Or from PyPI:
```bash
pip install termstory
```

## Quick Start

```bash
termstory today          # What did I work on today?
termstory search <query> # Find that command from last week
termstory insights       # Stats, streaks, productivity
termstory predict        # What will I work on next?
termstory sleep --show   # View consolidated context summaries
```

## Features

- Shell history ingestion (Zsh, Bash, Fish, PowerShell)
- Session detection with 30-min idle threshold
- Project auto-detection (Git, npm, Maven, Cargo)
- AI summaries (Groq, OpenAI, Ollama)
- RAG semantic search
- REM Sleep context consolidation
- TUI dashboard with Matrix defrag animation
- Ghost Typer playback
- Vampire Coder Index, RPG classes, Necromancer score
- Web export with heatmaps and timelines
- SQLite FTS5 full-text search

## Docs

See [AGENTS.md](AGENTS.md) for architecture, [CHANGELOG.md](CHANGELOG.md) for releases, [TRACKER.md](TRACKER.md) for batch status.
