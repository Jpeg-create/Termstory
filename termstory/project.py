import os
import re
from typing import List, Optional, Dict
from termstory.models import Session, Project

import shlex

def extract_cd_path(cmd_str: str) -> Optional[str]:
    """Extract directory path from a cd command"""
    try:
        tokens = shlex.split(cmd_str)
    except Exception:
        tokens = cmd_str.strip().split()
        
    if not tokens or tokens[0] != 'cd':
        return None
        
    # Filter out cd flags (like -P, -L, --, etc.)
    path_args = [t for t in tokens[1:] if not t.startswith('-')]
    if not path_args:
        # cd with no arguments defaults to ~ (home)
        return "~"
        
    # Take the first argument
    return path_args[0]

def humanize_project_name(path: str) -> str:
    """Humanize directory name (e.g. incubator-hugegraph -> Apache HugeGraph)"""
    if path == "~" or path == os.path.expanduser("~") or path == "/":
        return "Home"
        
    # Remove trailing slash
    normalized_path = path.rstrip('/')
    base_name = os.path.basename(normalized_path)
    if not base_name:
        return "Root"
        
    # Replace hyphens and underscores with spaces
    name = base_name.replace('-', ' ').replace('_', ' ')
    
    # Specific heuristics and capitalization replacements
    word_replacements = {
        "hugegraph": "HugeGraph",
        "incubator": "Apache",
        "k8s": "Kubernetes",
        "tf": "Terraform",
        "db": "Database",
        "cli": "CLI",
    }
    
    prefixes_to_strip = {"my", "project", "learning", "test"}
    
    words = name.split()
    while words and words[0].lower() in prefixes_to_strip:
        words.pop(0)
        
    processed_words = []
    for word in words:
        word_lower = word.lower()
        if word_lower in word_replacements:
            processed_words.append(word_replacements[word_lower])
        else:
            # Capitalize first letter
            processed_words.append(word.capitalize())
            
    if not processed_words:
        return base_name.capitalize()
        
    return " ".join(processed_words)

def disambiguate_project_names(projects: List[Project]) -> Dict[int, str]:
    """Return a mapping of project_id -> display_name. If name clashes exist, 
    appends the abbreviated parent directory path hint."""
    from collections import defaultdict
    by_name = defaultdict(list)
    for p in projects:
        if p.id is not None:
            by_name[p.name].append(p)
            
    display_names = {}
    for name, projs in by_name.items():
        if len(projs) == 1:
            display_names[projs[0].id] = projs[0].name
        else:
            for p in projs:
                parent_dir = os.path.dirname(p.path)
                home = os.path.expanduser("~")
                if parent_dir.startswith(home):
                    parent_dir = parent_dir.replace(home, "~", 1)
                display_names[p.id] = f"{p.name} ({parent_dir})"
    return display_names

def find_project_root(path: str) -> str:
    """Find the root project directory for a given path by looking for repository/project markers, 
    stopping at home or root directories."""
    # Expand and make absolute
    abs_path = os.path.abspath(os.path.expanduser(path))
    home = os.path.abspath(os.path.expanduser("~"))
    
    # If the path is home or root, just return it
    if abs_path == home or abs_path == "/":
        return abs_path
        
    current = abs_path
    
    # Marker files/directories indicating a project root
    project_markers = {
        # Repositories
        ".git", ".hg", ".svn",
        # Project files
        "package.json", "pom.xml", "build.gradle", "Cargo.toml", 
        "requirements.txt", "setup.py", "Makefile", "go.mod", 
        "CMakeLists.txt", "pyproject.toml"
    }
    
    while current and current != home and current != "/":
        try:
            # Check if any marker exists in the current directory
            files = os.listdir(current)
            if any(marker in files for marker in project_markers):
                return current
        except Exception:
            pass
            
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
        
    # Fallback logic if no project markers were found:
    # Check if the path is inside a common project workspace folder (e.g., ~/Projects/...)
    rel_to_home = os.path.relpath(abs_path, home)
    parts = rel_to_home.split(os.sep)
    if len(parts) >= 2 and parts[0].lower() in {"projects", "workspace", "workspace_py", "repos", "git", "code", "dev", "development"}:
        return os.path.join(home, parts[0], parts[1])
        
    return abs_path

def detect_projects(sessions: List[Session]) -> List[Project]:
    """Detect projects from cd commands in sessions, humanize names, and update links in sessions/commands"""
    projects_dict = {}
    project_id_counter = 1
    
    # Sort sessions by start_time to keep timelines linear
    sorted_sessions = sorted(sessions, key=lambda s: s.start_time)
    
    for session in sorted_sessions:
        # Find cd commands
        cd_commands = []
        for cmd in session.commands:
            cmd_stripped = cmd.command.strip()
            # Must start with cd followed by space/tab/EOF
            if cmd_stripped == "cd" or cmd_stripped.startswith("cd ") or cmd_stripped.startswith("cd\t"):
                cd_commands.append(cmd)
                
        if cd_commands:
            # Look at the last cd command in the session
            last_cd = cd_commands[-1]
            path = extract_cd_path(last_cd.command)
            if path:
                # Resolve the project root path
                project_root = find_project_root(path)
                
                if project_root not in projects_dict:
                    # Convert absolute project root back to a user-friendly path (using ~ if possible)
                    home = os.path.expanduser("~")
                    display_path = project_root
                    if project_root.startswith(home):
                        display_path = project_root.replace(home, "~", 1)
                        
                    name = humanize_project_name(project_root)
                    project = Project(
                        id=project_id_counter,
                        name=name,
                        path=display_path,
                        first_seen=session.start_time,
                        last_seen=session.end_time,
                        session_count=1,
                        total_time=session.duration_seconds
                    )
                    projects_dict[project_root] = project
                    project_id_counter += 1
                else:
                    project = projects_dict[project_root]
                    project.first_seen = min(project.first_seen, session.start_time)
                    project.last_seen = max(project.last_seen, session.end_time)
                    project.session_count += 1
                    project.total_time += session.duration_seconds
                    
                # Link session and commands to project
                session.project_id = project.id
                for cmd in session.commands:
                    cmd.project_id = project.id
        else:
            session.project_id = None
            for cmd in session.commands:
                cmd.project_id = None
                
    return list(projects_dict.values())
