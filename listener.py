"""
RME Task Listener — polls ntfy.sh for voice commands, uses Claude CLI to update data.json
Usage: python listener.py
"""
import json, subprocess, time, requests, os

NTFY_TOPIC = "rme-task-inbox"
NTFY_URL = f"https://ntfy.sh/{NTFY_TOPIC}/json?poll=1&since=30s"
DATA_FILE = os.path.join(os.path.dirname(__file__), "data.json")
POLL_INTERVAL = 15  # seconds

def get_data():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def process_command(message):
    data = get_data()
    prompt = f"""You are a task manager. Given the current data.json and a voice command, output ONLY the updated JSON. No explanation, no markdown, just valid JSON.

Current data.json sections (not backlog):
{json.dumps({"sections": data["sections"], "grocery": data["grocery"], "notes": data["notes"]}, indent=2)}

Voice command: "{message}"

Rules:
- For adding tasks: add to the most relevant existing section, or create a new section if none fit
- Each task object MUST have: {{"text": "...", "sub": "...", "done": false}}
- Each grocery item MUST be an object: {{"text": "...", "done": false}}
- For marking done: set done=true on the matching task
- For deleting: remove the task entirely
- Preserve all existing data exactly — do not rename sections or alter unrelated items
- Return the FULL updated object with sections, grocery, and notes keys
- Output raw JSON only — no markdown, no code fences, no explanation"""

    env = os.environ.copy()
    env.pop("CLAUDECODE", None)
    result = subprocess.run(
        ["claude", "-p", prompt, "--output-format", "text", "--max-turns", "1"],
        capture_output=True, timeout=60, env=env, encoding="utf-8"
    )
    if result.returncode != 0:
        print(f"  Claude error: {result.stderr}")
        return False

    try:
        # Strip markdown code fences if present
        output = result.stdout.strip()
        if output.startswith("```"):
            output = output.split("\n", 1)[1]  # remove first line
            output = output.rsplit("```", 1)[0]  # remove closing fence
        updated = json.loads(output.strip())
        data["sections"] = updated["sections"]
        data["grocery"] = updated["grocery"]
        data["notes"] = updated.get("notes", data["notes"])
        save_data(data)
        return True
    except (json.JSONDecodeError, KeyError) as e:
        print(f"  Parse error: {e}")
        print(f"  Raw output: {result.stdout[:200]}")
        return False

def git_push():
    subprocess.run(["git", "add", "data.json"], cwd=os.path.dirname(__file__))
    subprocess.run(["git", "commit", "-m", "Task update from mobile"], cwd=os.path.dirname(__file__))
    subprocess.run(["git", "push"], cwd=os.path.dirname(__file__))

def poll():
    try:
        res = requests.get(NTFY_URL, timeout=10)
        messages = []
        for line in res.text.strip().split("\n"):
            if not line:
                continue
            msg = json.loads(line)
            if msg.get("event") == "message":
                messages.append(msg["message"])
        return messages
    except Exception as e:
        print(f"  Poll error: {e}")
        return []

if __name__ == "__main__":
    print(f"Listening on ntfy.sh/{NTFY_TOPIC} (polling every {POLL_INTERVAL}s)")
    print("Send a test message: curl -d 'add eggs to grocery list' ntfy.sh/rme-task-inbox")
    print()
    while True:
        messages = poll()
        for msg in messages:
            print(f">> {msg}")
            if process_command(msg):
                git_push()
                print("   Done — pushed to GitHub")
            else:
                print("   Failed to process")
        time.sleep(POLL_INTERVAL)
