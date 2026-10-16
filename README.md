# 🏴 Beginner CTF — Ethical Hacking Class

A simple, self-contained Capture The Flag platform with **8 beginner-friendly challenges** across Web, Encoding, and Crypto categories.

## 🚀 Quick Start

```bash
# Install Flask (only dependency)
pip install flask

# Run the CTF server
python app.py

# Open in browser
# http://localhost:5000
```

## 📝 Challenges Overview

| #  | Challenge          | Category | Points | Difficulty | Skill Taught                      |
|----|-------------------|----------|--------|------------|-----------------------------------|
| 1  | Inspector Gadget  | Web      | 100    | ⭐          | Viewing HTML source code          |
| 2  | Decode Me         | Encoding | 100    | ⭐          | Base64 decoding                   |
| 3  | Caesar's Secret   | Crypto   | 150    | ⭐⭐        | ROT13 / Caesar cipher             |
| 4  | Robot Secrets     | Web      | 100    | ⭐          | robots.txt reconnaissance         |
| 5  | Cookie Monster    | Web      | 150    | ⭐⭐        | Browser cookies / DevTools        |
| 6  | Header Hunter     | Web      | 150    | ⭐⭐        | HTTP response headers             |
| 7  | Hash Cracker      | Crypto   | 200    | ⭐⭐        | MD5 hash cracking                 |
| 8  | Hex Dump          | Encoding | 100    | ⭐          | Hexadecimal to ASCII conversion   |

**Total: 1050 points**

## 🎯 How It Works

1. Students visit the dashboard and pick a challenge
2. Each challenge teaches a different security concept
3. Students discover the flag (format: `FLAG{...}`)
4. Submit the flag on the challenge page to earn points
5. Progress is tracked per browser session

## 🔄 Reset Progress

Visit `/reset` or click the reset link on the dashboard.

---

## 🔑 ANSWER KEY (Instructor Only!)

> ⚠️ **DO NOT share this with students!**

| Challenge         | Flag                                  | How to Solve                                                 |
|-------------------|---------------------------------------|--------------------------------------------------------------|
| Inspector Gadget  | `FLAG{html_source_is_your_friend}`    | View page source (Ctrl+U) → find HTML comment               |
| Decode Me         | `FLAG{base64_is_not_encryption}`      | Base64 decode the string (e.g., `echo <str> \| base64 -d`)  |
| Caesar's Secret   | `FLAG{julius_would_be_proud}`         | Apply ROT13 to the cipher text                               |
| Robot Secrets     | `FLAG{robots_txt_is_public}`          | Visit `/robots.txt` → follow link to `/super-secret-page`   |
| Cookie Monster    | `FLAG{cookies_are_delicious}`         | DevTools → Application → Cookies → `secret_flag`            |
| Header Hunter     | `FLAG{check_your_headers}`            | DevTools → Network → Response Headers → `X-Secret-Flag`     |
| Hash Cracker      | `FLAG{password123_is_terrible}`       | MD5 of "password123" → CrackStation or hashcat              |
| Hex Dump          | `FLAG{hex_is_just_base16}`            | Convert hex to ASCII: `bytes.fromhex(hex_str)`              |

---

## 🛠️ Customization

- Edit `FLAGS` dict in `app.py` to change flags
- Edit `CHALLENGES` list to modify descriptions, hints, or points
- Edit `static/style.css` to change the theme
- Add new challenges by adding to both `FLAGS`, `CHALLENGES`, and `get_challenge_data()`

## 📋 Requirements

- Python 3.7+
- Flask (`pip install flask`)
- A modern web browser

That's it! No database, no complex setup. Everything runs in memory.
