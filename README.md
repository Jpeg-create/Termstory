# TermStory

TermStory parses your local shell history, groups command executions into sessions, identifies projects, and provides a beautifully structured summary of what you did today.

## Features
* 📁 **Project Detection**: Extracts working directories from successful `cd` commands.
* ⏱️ **Session Grouping**: Automatically clusters commands into developer sessions based on 30+ minute gaps.
* 📋 **Daily summaries**: Quickly answer "What did I do today?" with `termstory today`.
* 🔒 **100% Local & Private**: All data is saved into a local SQLite database (`~/.termstory/termstory.db`).

## Installation

Install directly in development mode:
```bash
pip install -e .
```

Or install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the following command to see today's summary:
```bash
termstory today
```

Example Output:
```
╭────────────────────────────────────────╮
│ 📋 Today (Tuesday, June 02, 2026)     │
╰────────────────────────────────────────╯

📁 Apache HugeGraph (1 session)
⏱️  3h 41m

📝 Commands:
  Git                  14 times
  Docker               12 times
  Maven                7 times
  Editor               8 times

📅 Sessions:
  9:00 AM - 11:15 AM (2h 15m)
  2:30 PM - 4:26 PM  (1h 56m)
```

## Running Tests

Run the test suite using `pytest`:
```bash
pytest tests/
```
