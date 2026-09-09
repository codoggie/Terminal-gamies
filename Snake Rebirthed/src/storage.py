import os, json, sys
from datetime import datetime

LEADERBOARD_FILE = "snake_vitals_data.json"
GLOBAL_CLOUD_API = "https://kvdb.io"

try:
    import urllib.request
    HAS_NETWORK = True
except ImportError:
    HAS_NETWORK = False

def init_storage():
    if not os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, 'w') as f:
            json.dump({"global_leaderboard": [], "session_runs_log": [], "developer_profiles": {"saved_exp_factor": 1.0, "saved_combo_factor": 1.0}}, f, indent=4)

def load_data():
    init_storage()
    local_data = {"global_leaderboard": [], "session_runs_log": [], "developer_profiles": {"saved_exp_factor": 1.0, "saved_combo_factor": 1.0}}
    try:
        with open(LEADERBOARD_FILE, 'r') as f: local_data = json.load(f)
    except: pass
    if HAS_NETWORK:
        try:
            req = urllib.request.Request(GLOBAL_CLOUD_API, method="GET")
            with urllib.request.urlopen(req, timeout=1.5) as response:
                cloud_board = json.loads(response.read().decode('utf-8'))
                if isinstance(cloud_board, list):
                    local_data["global_leaderboard"] = cloud_board
        except: pass
    return local_data

def save_data(data):
    try:
        with open(LEADERBOARD_FILE, 'w') as f: json.dump(data, f, indent=4)
    except: pass

    if HAS_NETWORK and "global_leaderboard" in data:
        try:
            req = urllib.request.Request(
                GLOBAL_CLOUD_API,
                data=json.dumps(data["global_leaderboard"]).encode('utf-8'),
                headers={'Content-Type': 'application/json'},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=1.5) as response: pass
        except: pass

def register_run(username, score, max_level, execution_time):
    data = load_data()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data["session_runs_log"].append({"username": username, "score": score, "level": max_level, "seconds": execution_time, "date": timestamp})
    leaderboard = data["global_leaderboard"]
    p_rec = next((i for i in leaderboard if i["username"].lower() == username.lower()), None)
    if p_rec:
        if score > p_rec["high_score"]:
            p_rec["high_score"], p_rec["max_level"], p_rec["last_updated"] = score, max_level, timestamp
    else:
        leaderboard.append({"username": username, "high_score": score, "max_level": max_level, "last_updated": timestamp})
    data["global_leaderboard"] = sorted(leaderboard, key=lambda x: x["high_score"], reverse=True)[:10]
    save_data(data)

def get_top_scores(limit=8): return load_data()["global_leaderboard"][:limit]
def load_cheat_modifiers(): return load_data().get("developer_profiles", {"saved_exp_factor": 1.0, "saved_combo_factor": 1.0})
def save_cheat_modifiers(exp_f, combo_f):
    data = load_data()
    data["developer_profiles"] = {"saved_exp_factor": exp_f, "saved_combo_factor": combo_f}
    save_data(data)
