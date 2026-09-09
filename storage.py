import os, json
from datetime import datetime

LEADERBOARD_FILE = "snake_vitals_data.json"

def init_storage():
    if not os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, 'w') as f:
            json.dump({"global_leaderboard": [], "session_runs_log": []}, f, indent=4)

def load_data():
    init_storage()
    try:
        with open(LEADERBOARD_FILE, 'r') as f: return json.load(f)
    except: return {"global_leaderboard": [], "session_runs_log": []}

def save_data(data):
    try:
        with open(LEADERBOARD_FILE, 'w') as f: json.dump(data, f, indent=4)
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
    data["global_leaderboard"] = sorted(leaderboard, key=lambda x: x["high_score"], reverse=True)
    save_data(data)

def get_top_scores(limit=8):
    return load_data()["global_leaderboard"][:limit]
