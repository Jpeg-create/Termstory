# TermStory

TermStory parses your local shell history, groups command executions into sessions, identifies project folders, maps recent Git commits to your active sessions, and provides a beautifully structured, terminal-based dashboard of what you did.

Using the `Rich` library, TermStory provides colored panels, structured tables, and block-character progress bar charts for a highly premium terminal experience.

---

## Features
* 📁 **Project Detection**: Extracts working directories from successful `cd` commands. Prioritizes Git, Mercurial, and SVN roots.
* ⏱️ **Session Grouping**: Automatically clusters commands into developer sessions based on 30+ minute gaps.
* 💬 **Git Commit Mapping**: Automatically syncs and maps local Git commits to developer sessions (with a 5-minute pre-buffer and 10-minute post-buffer). Commit messages are automatically cleaned (stripping emojis, JIRA codes, conventional commit prefixes like `feat:`, and PR references).
* 🔍 **Fuzzy History Search**: Search across your entire work history (commands, commits, and projects) using `termstory search`.
* 💡 **Developer Insights**: Get focus scores (concentration levels), project time splits, hourly time-of-day allocations, day-of-week active hours, and rule-based insights.
* 📋 **Daily Summaries**: Quickly answer "What did I do today?" with `termstory today`.
* 🔒 **100% Local & Private**: All history, commits, and insights are stored in a local SQLite database (`~/.termstory/termstory.db`).

---

## Installation

Install in development mode:
```bash
pip install -e .
```

Or install dependencies:
```bash
pip install -r requirements.txt
```

---

## Usage

### 1. Daily Summary
Show today's summary:
```bash
termstory today
```

Options:
* `--detailed`: Show all exact commands and Git commits mapped to each session.
* `--compare`: Compare today's project durations with yesterday's work.
* `--stats`: Show a complete, sorted command execution count breakdown table.

### 2. Weekly Summary
Show this week's (Monday-Sunday) work statistics, day-of-week active hours bar charts, and commits:
```bash
termstory week
```

Options:
* `--last`: Show last week's summary instead of this week's.
* `--project NAME`: Filter the report to only show a specific project.
* `--detailed`: Show all exact commands in each session.

### 3. Monthly Summary
Show this month's summary of logged days, project times, and averages:
```bash
termstory month
```

Options:
* `[MONTH_YEAR]`: Query a specific month/year (e.g. `termstory month "June 2026"`).
* `--last`: Show last month's summary.
* `--detailed`: Show all exact commands in each session.

### 4. Fuzzy History Search
Fuzzy search across commands, Git commits, and projects in history:
```bash
termstory search "docker"
```

Options:
* `--project NAME`: Filter matching sessions by project name.
* `--since YYYY-MM-DD`: Search for sessions starting after a specific date.
* `--limit LIMIT`: Limit results (default: 50).
* `--detailed`: Display all commands and commits inside matched sessions.

### 5. Developer Insights
Analyze your work patterns, hourly/daily splits, and focus concentration score:
```bash
termstory insights
```

Options:
* `--days DAYS`: Number of days to analyze history for insights (default: 30).

### 6. Project Details
Show a 30-day dashboard for a specific project:
```bash
termstory project <name>
```
*Prioritizes exact name matches first, then prefix matches, and then fuzzy path matches.*

Options:
* `--last-week`: Show summary for last week instead of last 30 days.
* `--since YYYY-MM-DD`: Show summary since a specific date.
* `--files`: Show only the list of related files modified (inferred from editor commands).
* `--stats`: Show only top command statistics.

### 7. List All Projects
List all tracked projects ranked by total work time:
```bash
termstory projects
```

Options:
* `--sort [time|recent|name]`: Sort projects by total hours, last activity date, or alphabetically.

### 8. Date Override
Override the date for any subcommand or run a positional date query:
```bash
termstory 2026-06-02           # Runs today's summary for June 2nd
termstory --date 2026-06-02    # Runs today's summary for June 2nd
termstory --date 2026-06-02 week # Runs weekly summary for the week containing June 2nd
```

---

## Running Tests

Run the test suite using `pytest`:
```bash
pytest tests/
```
