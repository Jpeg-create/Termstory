import os
import time
from termstory.parser import parse_zsh_history
from termstory.session import create_sessions
from termstory.database import Database
from termstory.project import find_project_root, Project

def test_end_to_end_integration(tmp_path):
    # 1. Create a mock Zsh history file
    hist_file = tmp_path / "zsh_history"
    
    # We will write some timestamped commands.
    # Note: 1717675200 is June 6, 2026 12:00:00 UTC.
    now = 1717675200
    lines = [
        f": {now}:0;cd {tmp_path}\n",
        f": {now + 10}:0;pytest --verbose\n",
        f": {now + 50}:0;git commit -m \"feat: initial commit\"\n"
    ]
    hist_file.write_text("".join(lines), encoding="utf-8")
    
    # 2. Parse the history file
    commands = parse_zsh_history(str(hist_file))
    assert len(commands) == 3
    assert commands[0].command == f"cd {tmp_path}"
    assert commands[1].command == "pytest --verbose"
    assert commands[2].command == "git commit -m \"feat: initial commit\""
    
    # Associate commands with project_id
    project_root = find_project_root(str(tmp_path))
    p1 = Project(id=1, name="Integration Project", path=project_root, first_seen=now, last_seen=now + 50, session_count=1, total_time=50)
    
    for cmd in commands:
        cmd.project_id = p1.id
        
    # 3. Build sessions
    sessions = create_sessions(commands)
    assert len(sessions) == 1
    session = sessions[0]
    session.id = 1
    session.project_id = p1.id
    for cmd in commands:
        cmd.session_id = session.id
        
    # 4. Initialize Database
    db_file = tmp_path / "integration.db"
    db = Database(str(db_file))
    db.init_db()
    
    # Save projects, sessions, commands
    db.save_data([p1], [session], commands)
    
    # 5. Search sessions
    results = db.search_sessions("verbose")
    assert len(results) == 1
    assert results[0]["session_id"] == 1
    assert "pytest --verbose" in results[0]["matching_commands"]
