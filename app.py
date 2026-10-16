"""
🏴 Beginner CTF — Ethical Hacking Class
========================================
Team-based CTF with registration, leaderboard, and QR code access.

Run:   python3 app.py
Visit: http://localhost:8080
"""

from flask import (
    Flask, render_template, request, jsonify, make_response,
    session, redirect, url_for
)
import hashlib
import os
import base64
import socket
import json
import time
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)

# ──────────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────────
MAX_TEAMS = 10
PORT = 8080

# ──────────────────────────────────────────────
# In-memory storage
# ──────────────────────────────────────────────
teams = {}  # { team_id: { "name": str, "solved": [str], "registered_at": float } }
team_counter = 0

# ──────────────────────────────────────────────
# All flags  (students must discover these)
# ──────────────────────────────────────────────
FLAGS = {
    "challenge1": "FLAG{html_source_is_your_friend}",
    "challenge2": "FLAG{base64_is_not_encryption}",
    "challenge3": "FLAG{julius_would_be_proud}",
    "challenge4": "FLAG{robots_txt_is_public}",
    "challenge5": "FLAG{cookies_are_delicious}",
    "challenge6": "FLAG{check_your_headers}",
    "challenge7": "FLAG{password123_is_terrible}",
    "challenge8": "FLAG{hex_is_just_base16}",
}

CHALLENGES = [
    {
        "id": "challenge1",
        "title": "🔍 Inspector Gadget",
        "category": "Web",
        "points": 100,
        "difficulty": "⭐",
        "description": "Every web page has secrets hiding in plain sight. Can you inspect what's really going on?",
        "hint": "Right-click → View Page Source (or press Ctrl+U / Cmd+Option+U)",
    },
    {
        "id": "challenge2",
        "title": "🔤 Decode Me",
        "category": "Encoding",
        "points": 100,
        "difficulty": "⭐",
        "description": "Someone encoded a secret message. It ends with '=' so it's probably not random...",
        "hint": "This encoding uses 64 characters. There's a well-known tool for it.",
    },
    {
        "id": "challenge3",
        "title": "🏛️ Caesar's Secret",
        "category": "Crypto",
        "points": 150,
        "difficulty": "⭐⭐",
        "description": "Julius Caesar used a simple cipher to protect his messages. Can you crack this one?",
        "hint": "ROT13 is a special case of the Caesar cipher. Try rotating each letter by 13.",
    },
    {
        "id": "challenge4",
        "title": "🤖 Robot Secrets",
        "category": "Web",
        "points": 100,
        "difficulty": "⭐",
        "description": "Web crawlers follow rules. But what if those rules reveal hidden paths?",
        "hint": "Check /robots.txt — it tells search engines where NOT to look.",
    },
    {
        "id": "challenge5",
        "title": "🍪 Cookie Monster",
        "category": "Web",
        "points": 150,
        "difficulty": "⭐⭐",
        "description": "Mmm, cookies! Websites store little treats in your browser. Can you find the secret one?",
        "hint": "Open DevTools → Application/Storage → Cookies. Or use document.cookie in the console.",
    },
    {
        "id": "challenge6",
        "title": "📨 Header Hunter",
        "category": "Web",
        "points": 150,
        "difficulty": "⭐⭐",
        "description": "HTTP responses carry more than just the page. There's hidden info in the headers!",
        "hint": "Open DevTools → Network tab → click the request → look at Response Headers.",
    },
    {
        "id": "challenge7",
        "title": "🔓 Hash Cracker",
        "category": "Crypto",
        "points": 200,
        "difficulty": "⭐⭐",
        "description": "We found a leaked password hash. Can you figure out the original password?",
        "hint": "It's an MD5 hash. Try common passwords, or use an online hash lookup tool like CrackStation.",
    },
    {
        "id": "challenge8",
        "title": "🧮 Hex Dump",
        "category": "Encoding",
        "points": 100,
        "difficulty": "⭐",
        "description": "This message was converted to hexadecimal. Can you convert it back to text?",
        "hint": "Each pair of hex digits = one ASCII character. Use CyberChef or Python: bytes.fromhex()",
    },
]

MAX_POINTS = sum(c["points"] for c in CHALLENGES)


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

def get_local_ip():
    """Get the machine's local network IP."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def get_server_url():
    """Return the accessible URL based on incoming request or auto-detected network IP."""
    if request:
        try:
            host = request.host
            if host and not host.startswith("127.0.0.1") and not host.startswith("localhost"):
                scheme = request.headers.get("X-Forwarded-Proto", request.scheme)
                if "lhr.life" in host:
                    scheme = "https"
                return f"{scheme}://{host}"
        except Exception:
            pass
    ip = get_local_ip()
    return f"http://{ip}:{PORT}"


def get_current_team():
    """Return the current team dict or None."""
    team_id = session.get("team_id")
    if team_id and team_id in teams:
        return teams[team_id]
    return None


def get_team_score(team):
    """Calculate a team's total score."""
    return sum(c["points"] for c in CHALLENGES if c["id"] in team["solved"])


def get_leaderboard():
    """Return sorted leaderboard data."""
    board = []
    for tid, team in teams.items():
        score = get_team_score(team)
        board.append({
            "id": tid,
            "name": team["name"],
            "score": score,
            "solved_count": len(team["solved"]),
            "registered_at": team["registered_at"],
        })
    # Sort by score desc, then by earliest registration (tiebreaker)
    board.sort(key=lambda t: (-t["score"], t["registered_at"]))
    # Add rank
    for i, entry in enumerate(board):
        entry["rank"] = i + 1
    return board


def get_challenge_data(challenge_id):
    """Return extra data needed for each challenge page."""

    if challenge_id == "challenge1":
        return {"flag_comment": FLAGS["challenge1"]}

    if challenge_id == "challenge2":
        encoded = base64.b64encode(FLAGS["challenge2"].encode()).decode()
        return {"encoded_string": encoded}

    if challenge_id == "challenge3":
        def rot13(text):
            result = []
            for c in text:
                if "a" <= c <= "z":
                    result.append(chr((ord(c) - ord("a") + 13) % 26 + ord("a")))
                elif "A" <= c <= "Z":
                    result.append(chr((ord(c) - ord("A") + 13) % 26 + ord("A")))
                else:
                    result.append(c)
            return "".join(result)
        return {"cipher_text": rot13(FLAGS["challenge3"])}

    if challenge_id == "challenge7":
        password = "password123"
        md5_hash = hashlib.md5(password.encode()).hexdigest()
        return {
            "hash": md5_hash,
            "hash_type": "MD5",
            "flag_template": "FLAG{<password>_is_terrible}",
        }

    if challenge_id == "challenge8":
        hex_string = FLAGS["challenge8"].encode().hex()
        return {"hex_string": hex_string}

    return {}


# ──────────────────────────────────────────────
# Routes — Registration
# ──────────────────────────────────────────────

@app.route("/")
def index():
    team = get_current_team()
    if not team:
        return redirect(url_for("register"))

    solved = team["solved"]
    total_points = get_team_score(team)
    
    # Sequential progression:
    # First unsolved challenge is active (unlocked).
    # Already solved challenges are locked (completed).
    # Challenges after the active one are locked (not yet unlocked).
    active_id = None
    for c in CHALLENGES:
        if c["id"] not in solved:
            active_id = c["id"]
            break
            
    challenges_status = []
    for c in CHALLENGES:
        is_solved = c["id"] in solved
        is_active = (c["id"] == active_id)
        # Locked if already solved OR not reached yet
        is_locked = not is_active
        challenges_status.append({
            **c,
            "is_solved": is_solved,
            "is_active": is_active,
            "is_locked": is_locked
        })

    return render_template(
        "index.html",
        challenges=challenges_status,
        solved=solved,
        active_id=active_id,
        total_points=total_points,
        max_points=MAX_POINTS,
        team_name=team["name"],
        team_count=len(teams),
        max_teams=MAX_TEAMS,
    )


@app.route("/register", methods=["GET", "POST"])
def register():
    global team_counter
    error = None

    # If already registered, go to dashboard
    if get_current_team():
        return redirect(url_for("index"))

    if request.method == "POST":
        team_name = request.form.get("team_name", "").strip()

        if not team_name:
            error = "Team name can't be empty!"
        elif len(team_name) > 30:
            error = "Team name is too long (max 30 characters)."
        elif any(t["name"].lower() == team_name.lower() for t in teams.values()):
            error = f'Team name "{team_name}" is already taken!'
        elif len(teams) >= MAX_TEAMS:
            error = f"Sorry, all {MAX_TEAMS} team slots are full!"
        else:
            team_counter += 1
            team_id = f"team_{team_counter}"
            teams[team_id] = {
                "name": team_name,
                "solved": [],
                "registered_at": time.time(),
            }
            session["team_id"] = team_id
            return redirect(url_for("index"))

    url = get_server_url()

    return render_template(
        "register.html",
        error=error,
        team_count=len(teams),
        max_teams=MAX_TEAMS,
        teams_list=list(teams.values()),
        ctf_url=url,
    )


# ──────────────────────────────────────────────
# Routes — QR Code page (for projector / sharing)
# ──────────────────────────────────────────────

@app.route("/qr")
def qr_page():
    url = get_server_url()
    return render_template("qr.html", ctf_url=url)


# ──────────────────────────────────────────────
# Routes — Leaderboard
# ──────────────────────────────────────────────

@app.route("/leaderboard")
def leaderboard():
    board = get_leaderboard()
    team = get_current_team()
    team_id = session.get("team_id")
    return render_template(
        "leaderboard.html",
        leaderboard=board,
        total_challenges=len(CHALLENGES),
        max_points=MAX_POINTS,
        current_team_id=team_id,
        team=team,
    )


@app.route("/api/leaderboard")
def api_leaderboard():
    """JSON endpoint for live leaderboard updates."""
    return jsonify(get_leaderboard())


# ──────────────────────────────────────────────
# Routes — Challenges
# ──────────────────────────────────────────────

@app.route("/challenge/<challenge_id>")
def challenge(challenge_id):
    team = get_current_team()
    if not team:
        return redirect(url_for("register"))

    # Find the current challenge
    ch_index = next((i for i, c in enumerate(CHALLENGES) if c["id"] == challenge_id), None)
    if ch_index is None:
        return "Challenge not found", 404
    ch = CHALLENGES[ch_index]

    solved = team["solved"]
    # Check if previous challenges are solved
    for prev_i in range(ch_index):
        if CHALLENGES[prev_i]["id"] not in solved:
            # Cannot access this challenge yet
            return redirect(url_for("index"))

    is_solved = (challenge_id in solved)
    
    # Next challenge if available
    next_ch = CHALLENGES[ch_index + 1] if (ch_index + 1) < len(CHALLENGES) else None

    resp = make_response(
        render_template(
            "challenge.html",
            challenge=ch,
            is_solved=is_solved,
            challenge_data=get_challenge_data(challenge_id),
            team_name=team["name"],
            total_points=get_team_score(team),
            next_challenge=next_ch,
            is_last=(next_ch is None),
        )
    )

    # Challenge 5: Set a cookie with the flag
    if challenge_id == "challenge5":
        resp.set_cookie("secret_flag", FLAGS["challenge5"])

    # Challenge 6: Set a custom response header with the flag
    if challenge_id == "challenge6":
        resp.headers["X-Secret-Flag"] = FLAGS["challenge6"]

    return resp


@app.route("/submit", methods=["POST"])
def submit():
    team = get_current_team()
    if not team:
        return jsonify({"success": False, "message": "Not registered! Please join a team first."}), 401

    data = request.get_json() or {}
    challenge_id = data.get("challenge_id", "")
    submitted_flag = data.get("flag", "").strip()

    correct_flag = FLAGS.get(challenge_id)
    if not correct_flag:
        return jsonify({"success": False, "message": "Invalid challenge."})

    # Accept exact match or case-insensitive match for student convenience
    if submitted_flag.lower() == correct_flag.lower():
        if challenge_id not in team["solved"]:
            team["solved"].append(challenge_id)
            
        points = next(c["points"] for c in CHALLENGES if c["id"] == challenge_id)
        total = get_team_score(team)
        
        # Determine next challenge ID
        ch_index = next((i for i, c in enumerate(CHALLENGES) if c["id"] == challenge_id), None)
        next_id = CHALLENGES[ch_index + 1]["id"] if (ch_index is not None and ch_index + 1 < len(CHALLENGES)) else None

        return jsonify({
            "success": True,
            "message": f"🎉 Correct! +{points} points!",
            "total_points": total,
            "next_id": next_id,
            "is_last": (next_id is None)
        })
    else:
        return jsonify({"success": False, "message": "❌ Wrong flag. Check for typos and try again!"})


# ──────────────────────────────────────────────
# Routes — robots.txt (Challenge 4)
# ──────────────────────────────────────────────

@app.route("/robots.txt")
def robots():
    content = (
        "User-agent: *\n"
        "Disallow: /super-secret-page\n"
        "# Nothing to see here... or is there?\n"
    )
    return content, 200, {"Content-Type": "text/plain"}


@app.route("/super-secret-page")
def secret_page():
    return render_template("secret.html", flag=FLAGS["challenge4"])


# ──────────────────────────────────────────────
# Routes — Leave team / Admin reset
# ──────────────────────────────────────────────

@app.route("/leave")
def leave_team():
    """Leave your team (doesn't delete the team)."""
    session.clear()
    return redirect(url_for("register"))


@app.route("/admin/reset")
def admin_reset():
    """Full reset — clears all teams and progress."""
    global teams, team_counter
    teams = {}
    team_counter = 0
    session.clear()
    return redirect(url_for("register"))


# ──────────────────────────────────────────────
if __name__ == "__main__":
    local_ip = get_local_ip()
    url = f"http://{local_ip}:{PORT}"
    print("\n" + "=" * 55)
    print("  🏴  BEGINNER CTF  —  Ethical Hacking Class")
    print("=" * 55)
    print(f"  🌐  Local:   http://localhost:{PORT}")
    print(f"  📡  Network: {url}")
    print(f"  📱  QR Page: {url}/qr")
    print(f"  🏆  Board:   {url}/leaderboard")
    print(f"  📝  {len(CHALLENGES)} challenges | {MAX_POINTS} pts | {MAX_TEAMS} team slots")
    print(f"  🔄  Admin reset: /admin/reset")
    print("=" * 55 + "\n")
    app.run(debug=True, host="0.0.0.0", port=PORT, use_reloader=False)
