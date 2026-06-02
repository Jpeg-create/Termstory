import os
from typing import List

def get_history_files() -> List[str]:
    """Return a list of existing shell history file paths"""
    history_files = []
    
    # Check default paths for zsh and bash
    zsh_hist = os.path.expanduser("~/.zsh_history")
    bash_hist = os.path.expanduser("~/.bash_history")
    
    if os.path.exists(zsh_hist):
        history_files.append(zsh_hist)
    if os.path.exists(bash_hist):
        history_files.append(bash_hist)
        
    return history_files

def get_db_path() -> str:
    """Return the path to the sqlite database, creating parent directories if needed"""
    db_dir = os.path.expanduser("~/.termstory")
    os.makedirs(db_dir, exist_ok=True)
    return os.path.join(db_dir, "termstory.db")
