#!/usr/bin/env python3
"""Night School completion tracker.

Tracks which topics have been completed, skipped, or are in progress.
Reads from the queue.md file and cross-references with the docs/night-school/ directory.

Usage:
  python night_school_tracker.py status          # Show completion stats
  python night_school_tracker.py completed        # List completed topics
  python night_school_tracker.py pending          # List pending topics
  python night_school_tracker.py mark <topic>      # Mark a topic as completed
  python night_school_tracker.py skip <topic> <reason>  # Skip a topic with reason
"""

import sys
import json
import re
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent
QUEUE_FILE = BASE_DIR / 'docs' / 'night-school' / 'queue.md'
SCHOOL_DIR = BASE_DIR / 'docs' / 'night-school'
TRACKER_FILE = BASE_DIR / 'memory' / 'night-school-tracker.json'


def load_tracker():
    """Load the tracker JSON file."""
    if TRACKER_FILE.exists():
        with open(TRACKER_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'topics': {}, 'stats': {'completed': 0, 'skipped': 0, 'pending': 0}}


def save_tracker(data):
    """Save the tracker JSON file."""
    TRACKER_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(TRACKER_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def scan_playbooks():
    """Scan the night-school directory for completed playbook folders."""
    completed = []
    if SCHOOL_DIR.exists():
        for item in SCHOOL_DIR.iterdir():
            if item.is_dir() and not item.name.startswith('_'):
                playbook = item / 'playbook.md'
                if playbook.exists():
                    # Get last modified date
                    mtime = datetime.fromtimestamp(playbook.stat().st_mtime)
                    completed.append({
                        'topic': item.name,
                        'completed_date': mtime.strftime('%Y-%m-%d'),
                        'playbook_path': str(playbook.relative_to(BASE_DIR))
                    })
    return completed


def cmd_status():
    """Show completion stats."""
    tracker = load_tracker()
    playbooks = scan_playbooks()

    # Count from queue
    queue_content = QUEUE_FILE.read_text(encoding='utf-8') if QUEUE_FILE.exists() else ''
    unchecked = len(re.findall(r'^- \[ \]', queue_content, re.MULTILINE))
    checked = len(re.findall(r'^- \[x\]', queue_content, re.MULTILINE))

    # Count from tracker
    completed_count = len([t for t in tracker['topics'].values() if t.get('status') == 'completed'])
    skipped_count = len([t for t in tracker['topics'].values() if t.get('status') == 'skipped'])
    pending_count = len([t for t in tracker['topics'].values() if t.get('status') == 'pending'])

    # Add playbooks that aren't tracked yet
    untracked_playbooks = [p for p in playbooks if p['topic'] not in tracker['topics']]

    print(f"## Night School Status")
    print(f"  Queue unchecked: {unchecked}")
    print(f"  Queue checked: {checked}")
    print(f"  Playbook folders: {len(playbooks)}")
    print(f"  Tracked completed: {completed_count}")
    print(f"  Tracked skipped: {skipped_count}")
    print(f"  Tracked pending: {pending_count}")
    print(f"  Untracked playbooks: {len(untracked_playbooks)}")

    if untracked_playbooks:
        print(f"\n  Untracked playbooks (auto-marking as completed):")
        for p in untracked_playbooks:
            print(f"    - {p['topic']} (dated {p['completed_date']})")
            tracker['topics'][p['topic']] = {
                'status': 'completed',
                'date': p['completed_date'],
                'playbook': p['playbook_path']
            }
        save_tracker(tracker)


def cmd_completed():
    """List completed topics."""
    tracker = load_tracker()
    playbooks = scan_playbooks()

    # Merge
    all_completed = {p['topic']: p for p in playbooks}
    for topic, info in tracker['topics'].items():
        if info.get('status') == 'completed' and topic not in all_completed:
            all_completed[topic] = {'topic': topic, 'completed_date': info.get('date', 'unknown')}

    print(f"Completed ({len(all_completed)} topics):")
    for topic, info in sorted(all_completed.items()):
        date = info.get('completed_date', '?')
        print(f"  [{date}] {topic}")


def cmd_pending():
    """List pending topics from the queue."""
    if not QUEUE_FILE.exists():
        print("Queue file not found.")
        return

    content = QUEUE_FILE.read_text(encoding='utf-8')
    unchecked = re.findall(r'^- \[ \] (.+)$', content, re.MULTILINE)

    print(f"Pending ({len(unchecked)} topics):")
    for topic in unchecked:
        print(f"  - {topic}")


def cmd_mark(topic):
    """Mark a topic as completed."""
    tracker = load_tracker()
    tracker['topics'][topic] = {
        'status': 'completed',
        'date': datetime.now().strftime('%Y-%m-%d'),
        'playbook': f'docs/night-school/{topic}/playbook.md'
    }
    save_tracker(tracker)
    print(f"Marked '{topic}' as completed.")


def cmd_skip(topic, reason):
    """Skip a topic with a reason."""
    tracker = load_tracker()
    tracker['topics'][topic] = {
        'status': 'skipped',
        'date': datetime.now().strftime('%Y-%m-%d'),
        'reason': reason
    }
    save_tracker(tracker)
    print(f"Marked '{topic}' as skipped: {reason}")


def main():
    if len(sys.argv) < 2:
        print("Usage: night_school_tracker.py [status|completed|pending|mark|skip]")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == 'status':
        cmd_status()
    elif cmd == 'completed':
        cmd_completed()
    elif cmd == 'pending':
        cmd_pending()
    elif cmd == 'mark':
        if len(sys.argv) < 3:
            print("Usage: night_school_tracker.py mark <topic>")
            sys.exit(1)
        cmd_mark(sys.argv[2])
    elif cmd == 'skip':
        if len(sys.argv) < 4:
            print("Usage: night_school_tracker.py skip <topic> <reason>")
            sys.exit(1)
        cmd_skip(sys.argv[2], ' '.join(sys.argv[3:]))
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


if __name__ == '__main__':
    main()