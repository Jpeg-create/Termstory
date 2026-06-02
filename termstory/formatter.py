from collections import Counter
from datetime import datetime
from typing import List, Dict
from termstory.models import Session, Project, format_duration

DISPLAY_NAMES = {
    "git": "Git",
    "docker": "Docker",
    "npm": "NPM/Yarn/PNPM",
    "python": "Python",
    "maven": "Maven",
    "vim": "Editor (Vim/Nano/etc)",
}

def classify_command(cmd_text: str) -> str:
    """Classify the command type based on the executable name"""
    tokens = cmd_text.strip().split()
    if not tokens:
        return "other"
        
    first_token = tokens[0].lower()
    
    # Check for docker compose specifically since it is two tokens
    if len(tokens) > 1 and first_token == "docker" and tokens[1].lower() == "compose":
        return "docker"
        
    classifications = {
        "git": ["git", "gh"],
        "docker": ["docker", "docker-compose"],
        "npm": ["npm", "yarn", "pnpm", "npx"],
        "python": ["python", "python3", "pip", "pip3", "pytest", "poetry"],
        "maven": ["mvn", "maven"],
        "vim": ["vim", "vi", "nano", "emacs"],
    }
    
    for category, triggers in classifications.items():
        if first_token in triggers:
            return category
            
    return first_token

def format_time(timestamp: int) -> str:
    """Format Unix timestamp to 12-hour local time format without leading zeroes, e.g. '9:00 AM'"""
    dt = datetime.fromtimestamp(timestamp)
    time_str = dt.strftime("%I:%M %p")
    if time_str.startswith("0"):
        time_str = time_str[1:]
    return time_str

def format_today_output(sessions: List[Session], projects: List[Project]) -> str:
    """Format today's sessions, command aggregates, and project details as a clean UI card"""
    if not sessions:
        return "No sessions recorded today."
        
    today_str = datetime.now().strftime("%A, %B %d, %Y")
    
    # Map project IDs for easy retrieval
    project_map = {p.id: p for p in projects if p.id is not None}
    
    # Group sessions by project
    from collections import defaultdict
    sessions_by_project = defaultdict(list)
    for s in sessions:
        sessions_by_project[s.project_id].append(s)
        
    # Generate Header
    header_title = f"📋 Today ({today_str})"
    border = "─" * (len(header_title) + 2)
    output = []
    output.append(f"╭{border}╮")
    output.append(f"│ {header_title} │")
    output.append(f"╰{border}╯\n")
    
    # Sort projects, showing defined projects first, and General last
    project_ids = list(sessions_by_project.keys())
    
    def project_sort_key(p_id):
        if p_id is None:
            return (1, "")
        p = project_map.get(p_id)
        name = p.name if p else ""
        return (0, name)
        
    project_ids.sort(key=project_sort_key)
    
    for p_id in project_ids:
        proj_sessions = sessions_by_project[p_id]
        # Sort sessions linearly
        proj_sessions.sort(key=lambda s: s.start_time)
        
        proj_name = "General / No Project"
        if p_id is not None and p_id in project_map:
            proj_name = project_map[p_id].name
            
        session_word = "session" if len(proj_sessions) == 1 else "sessions"
        output.append(f"📁 Project: {proj_name} ({len(proj_sessions)} {session_word})")
        
        # Calculate time spent on this project today
        total_time_seconds = sum(s.duration_seconds for s in proj_sessions)
        output.append(f"⏱️  Total Time: {format_duration(total_time_seconds)}")
        
        # Command classification counts
        cmd_counts = Counter()
        for s in proj_sessions:
            for cmd in s.commands:
                category = classify_command(cmd.command)
                cmd_counts[category] += 1
                
        if cmd_counts:
            output.append("\n📝 Commands:")
            for category, count in cmd_counts.most_common(5):
                display_cat = DISPLAY_NAMES.get(category, category)
                # Left align category name for clean columns
                output.append(f"  {display_cat:<20} {count} times")
                
        output.append("\n📅 Sessions:")
        for s in proj_sessions:
            start_str = format_time(s.start_time)
            end_str = format_time(s.end_time)
            dur_str = format_duration(s.duration_seconds)
            output.append(f"  {start_str} - {end_str} ({dur_str})")
            
        output.append("\n" + "─" * 40 + "\n")
        
    # Trim the final separator lines
    if output and output[-1] == "\n" + "─" * 40 + "\n":
        output.pop()
        
    return "\n".join(output).strip()
