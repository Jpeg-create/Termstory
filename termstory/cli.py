import typer
from termstory.config import get_history_files, get_db_path
from termstory.parser import parse_all_histories
from termstory.session import create_sessions
from termstory.project import detect_projects
from termstory.database import Database
from termstory.formatter import format_today_output

app = typer.Typer(help="TermStory CLI - Parse local shell history and summarize your day")

@app.callback()
def callback():
    """TermStory - local shell history parsing and session summaries"""
    pass

@app.command("today")
def show_today():
    """Display today's shell sessions, projects, and command statistics"""
    db_path = get_db_path()
    db = Database(db_path)
    db.init_db()
    
    # 1. Load history files
    history_files = get_history_files()
    if not history_files:
        # Avoid crashing, print a nice explanation message
        typer.echo("Warning: No shell history files found (~/.zsh_history or ~/.bash_history).", err=True)
        # We can construct empty objects to proceed gracefully or return empty output.
        # But normally we expect at least one. Let's raise Exit if completely empty.
        raise typer.Exit(code=1)
        
    commands = parse_all_histories(history_files)
    
    # 2. Process command list into sessions and projects
    sessions = create_sessions(commands)
    projects = detect_projects(sessions)
    
    # 3. Store everything in the SQLite database
    db.save_data(projects, sessions, commands)
    
    # 4. Query today's sessions and associated projects
    today_sessions = db.get_today_sessions()
    
    project_ids = list(set(s.project_id for s in today_sessions if s.project_id is not None))
    today_projects = db.get_projects_by_ids(project_ids)
    
    # 5. Format and print the result
    output = format_today_output(today_sessions, today_projects)
    typer.echo(output)

if __name__ == "__main__":
    app()
