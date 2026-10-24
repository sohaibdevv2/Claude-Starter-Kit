#!/usr/bin/env python3
"""Extract user-assistant pairs from Claude Code session JSONL for reflection analysis.

Usage:
    python3 extract-learnings.py                      # latest session
    python3 extract-learnings.py --file <path.jsonl>  # specific file
    python3 extract-learnings.py --since 2026-02-27   # all sessions since date
    python3 extract-learnings.py --max-pairs 50       # limit output (default 50)

Output: Markdown with candidate pairs for Claude to analyze during /reflect.
Stdlib only — no external dependencies.
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

PROJECTS_DIR = Path.home() / ".claude" / "projects"
MAX_ASSISTANT_CHARS = 500
MAX_USER_CHARS = 1000

# Messages that are pure commands / acknowledgements — not worth analyzing
SKIP_PATTERNS = [
    "yes", "ok", "okay", "no", "y", "n", "sure", "go ahead", "do it",
    "commit and push", "push it", "looks good", "lgtm", "approved",
    "continue", "proceed", "next", "done", "thanks", "thank you",
]

CONTINUATION_MARKERS = [
    "This session is being continued",
    "continuation of a previous conversation",
    "context from a previous conversation",
]


def find_session_files(since=None):
    """Find all session JSONL files across all project directories."""
    files = []
    if not PROJECTS_DIR.exists():
        return files
    for project_dir in PROJECTS_DIR.iterdir():
        if not project_dir.is_dir():
            continue
        for jsonl in project_dir.glob("*.jsonl"):
            if "subagents" in str(jsonl):
                continue
            stat = jsonl.stat()
            mtime = datetime.fromtimestamp(stat.st_mtime)
            if since and mtime.date() < since:
                continue
            files.append((jsonl, mtime))
    files.sort(key=lambda x: x[1], reverse=True)
    return files


def find_latest_session():
    """Return the most recently modified session JSONL."""
    files = find_session_files()
    if not files:
        return None
    return files[0][0]


def is_skip_message(text):
    """Check if message is a pure command/acknowledgement."""
    normalized = text.strip().lower().rstrip(".!?")
    return normalized in SKIP_PATTERNS


def is_continuation(text):
    """Check if message is a session continuation marker."""
    return any(marker in text for marker in CONTINUATION_MARKERS)


def extract_text_content(message):
    """Extract plain text from a message's content field."""
    content = message.get("content", "")
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict):
                if block.get("type") == "text":
                    parts.append(block.get("text", ""))
                elif block.get("type") == "tool_result":
                    tc = block.get("content", "")
                    if isinstance(tc, str) and "user doesn't want to proceed" in tc.lower():
                        if "the user said:" in tc.lower():
                            idx = tc.lower().index("the user said:")
                            parts.append("[TOOL REJECTED] " + tc[idx + 14:].strip())
                        else:
                            parts.append("[TOOL REJECTED]")
                    elif block.get("is_error"):
                        parts.append("[TOOL ERROR]")
            elif isinstance(block, str):
                parts.append(block)
        return "\n".join(parts).strip()
    return ""


def has_tool_rejection(message):
    """Check if a user message contains a tool rejection with feedback."""
    content = message.get("content", "")
    if not isinstance(content, list):
        return False
    for block in content:
        if isinstance(block, dict) and block.get("type") == "tool_result":
            tc = str(block.get("content", ""))
            if "user doesn't want to proceed" in tc.lower() and "the user said:" in tc.lower():
                return True
    return False


def has_ask_user_answer(message):
    """Check if a user message contains an AskUserQuestion answer with real content."""
    content = message.get("content", "")
    if not isinstance(content, list):
        return False
    for block in content:
        if isinstance(block, dict) and block.get("type") == "tool_result":
            tc = block.get("content", "")
            if isinstance(tc, str) and len(tc) > 50 and not block.get("is_error"):
                if any(kw in tc.lower() for kw in ["selected", "chose", "answer", "option"]):
                    return True
            elif isinstance(tc, list):
                text = " ".join(b.get("text", "") for b in tc if isinstance(b, dict))
                if len(text) > 50:
                    return True
    return False


def classify_signal(user_text, has_rejection, has_answer):
    """Hint at signal type for Claude's analysis."""
    lower = user_text.lower()
    if has_rejection:
        return "tool_rejection"
    if has_answer:
        return "question_answer"
    if any(w in lower for w in ["no,", "not ", "don't", "shouldn't", "wrong", "instead", "actually"]):
        return "correction"
    if any(w in lower for w in ["always", "never", "prefer", "remember", "from now on"]):
        return "preference"
    if any(w in lower for w in ["why", "how come", "what if", "could you"]):
        return "question"
    return "context"


def extract_pairs(jsonl_path, max_pairs=50):
    """Stream JSONL and extract candidate user-assistant pairs."""
    pairs = []
    prev_assistant_text = None
    session_id = None
    first_ts = None
    last_ts = None

    with open(jsonl_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue

            msg_type = obj.get("type", "")
            timestamp = obj.get("timestamp", "")

            if not session_id and obj.get("sessionId"):
                session_id = obj["sessionId"]
            if timestamp:
                if not first_ts:
                    first_ts = timestamp
                last_ts = timestamp

            if msg_type == "assistant":
                text = extract_text_content(obj.get("message", {}))
                if text:
                    prev_assistant_text = text

            elif msg_type == "user":
                message = obj.get("message", {})
                user_text = extract_text_content(message)
                rejection = has_tool_rejection(message)
                answer = has_ask_user_answer(message)

                if len(user_text) < 20 and not rejection:
                    continue
                if not rejection and not answer:
                    if is_skip_message(user_text):
                        continue
                    if is_continuation(user_text):
                        continue

                if prev_assistant_text is None and not rejection:
                    continue

                signal = classify_signal(user_text, rejection, answer)

                pairs.append({
                    "timestamp": timestamp,
                    "assistant_text": (prev_assistant_text or "")[:MAX_ASSISTANT_CHARS],
                    "user_text": user_text[:MAX_USER_CHARS],
                    "signal": signal,
                })

                if len(pairs) >= max_pairs:
                    break

    return {
        "session_id": session_id or jsonl_path.stem,
        "file": str(jsonl_path),
        "first_ts": first_ts,
        "last_ts": last_ts,
        "pairs": pairs,
    }


def format_output(results):
    """Format extraction results as markdown."""
    lines = ["# Session Learnings Extract\n"]

    for result in results:
        ts_start = result["first_ts"][:16].replace("T", " ") if result["first_ts"] else "?"
        ts_end = result["last_ts"][:16].replace("T", " ") if result["last_ts"] else "?"

        lines.append(f"## Session: `{result['session_id']}`")
        lines.append(f"- **File:** `{result['file']}`")
        lines.append(f"- **Date range:** {ts_start} -> {ts_end}")
        lines.append(f"- **Candidate pairs:** {len(result['pairs'])}")
        lines.append("")

        for i, pair in enumerate(result["pairs"], 1):
            ts = pair["timestamp"][:19].replace("T", " ") if pair["timestamp"] else "?"
            lines.append(f"### Pair {i} ({ts})")
            lines.append(f"**Signal hint:** `{pair['signal']}`")
            asst = pair['assistant_text'].replace('\n', ' ').strip()
            user = pair['user_text'].replace('\n', ' ').strip()
            lines.append(f"**Claude said:** {asst}")
            lines.append(f"**User said:** {user}")
            lines.append("---")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Extract session learnings for /reflect")
    parser.add_argument("--file", type=str, help="Specific JSONL file to analyze")
    parser.add_argument("--since", type=str, help="Analyze sessions since date (YYYY-MM-DD)")
    parser.add_argument("--max-pairs", type=int, default=50, help="Max pairs per session (default 50)")
    args = parser.parse_args()

    if args.file:
        path = Path(args.file)
        if not path.exists():
            print(f"Error: File not found: {args.file}", file=sys.stderr)
            sys.exit(1)
        files = [(path, datetime.now())]
    elif args.since:
        try:
            since_date = datetime.strptime(args.since, "%Y-%m-%d").date()
        except ValueError:
            print(f"Error: Invalid date format: {args.since}. Use YYYY-MM-DD.", file=sys.stderr)
            sys.exit(1)
        files = find_session_files(since=since_date)
    else:
        latest = find_latest_session()
        if latest:
            files = [(latest, datetime.now())]
        else:
            files = []

    if not files:
        print("No session files found.", file=sys.stderr)
        if args.since:
            print(f"No sessions found since {args.since}.", file=sys.stderr)
        else:
            print(f"Searched in: {PROJECTS_DIR}", file=sys.stderr)
        sys.exit(0)

    results = []
    for jsonl_path, _ in files:
        result = extract_pairs(jsonl_path, max_pairs=args.max_pairs)
        if result["pairs"]:
            results.append(result)

    if not results:
        print("No candidate pairs found in session(s). Nothing to reflect on.", file=sys.stderr)
        sys.exit(0)

    print(format_output(results))


if __name__ == "__main__":
    main()
