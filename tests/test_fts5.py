import pytest
import sqlite3
from termstory.database import Database
from termstory.models import Project, Session, Command

def test_fts5_migration_and_search(tmp_path):
    db_file = tmp_path / "test_fts5.db"
    db = Database(str(db_file))
    db.init_db()

    # Verify search_index table exists
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='search_index';")
    row = cursor.fetchone()
    assert row is not None, "FTS5 search_index table should be created"
    
    # Check that FTS is indeed enabled
    assert db._is_fts_enabled(cursor) is True
    conn.close()

    # Insert test data
    p = Project(id=1, name="Antigravity Web", path="~/projects/antigravity", first_seen=1000, last_seen=2000, session_count=1, total_time=500)
    cmd1 = Command(timestamp=1050, command="npm run dev --port 3000", session_id=1, project_id=1)
    s1 = Session(id=1, start_time=1000, end_time=1500, duration_seconds=500, project_id=1, commands=[cmd1])
    db.save_data([p], [s1], [cmd1])

    # Check search index got commands
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT content, type, ref_id FROM search_index;")
    rows = cursor.fetchall()
    assert len(rows) == 1
    assert rows[0] == ("npm run dev --port 3000", "command", "1")
    conn.close()

    # Search for commands using FTS
    results = db.search_sessions("npm")
    assert len(results) == 1
    assert results[0]["session_id"] == 1
    assert "npm run dev --port 3000" in results[0]["matching_commands"]

    # Search prefix
    results = db.search_sessions("port")
    assert len(results) == 1
    assert results[0]["session_id"] == 1

    # Save session AI summary and verify FTS updates
    db.save_session_ai_summary(1, "Configured the local dev server and verified web sockets")
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT content, type, ref_id FROM search_index WHERE type = 'session_summary';")
    rows = cursor.fetchall()
    assert len(rows) == 1
    assert rows[0] == ("Configured the local dev server and verified web sockets", "session_summary", "1")
    conn.close()

    # Search session summary
    results = db.search_sessions("sockets")
    assert len(results) == 1
    assert results[0]["session_id"] == 1

    # Save git commits and verify FTS updates
    commits = [
        {"hash": "abcdef123456", "timestamp": 1100, "message": "feat: configure dev server port", "cleaned_message": "Configure dev server port"}
    ]
    db.save_commits(1, commits)

    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT content, type, ref_id FROM search_index WHERE type = 'commit';")
    rows = cursor.fetchall()
    assert len(rows) == 1
    assert rows[0] == ("Configure dev server port", "commit", "abcdef123456")
    conn.close()

    # Search commit message
    results = db.search_sessions("configure")
    assert len(results) == 1
    assert results[0]["session_id"] == 1
    assert len(results[0]["matching_commits"]) == 1

    # Verify query syntax error safety and fallback to traditional
    results = db.search_sessions('dev')
    assert len(results) == 1
