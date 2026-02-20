from datetime import datetime, timezone
import json
from pathlib import Path

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)
DATA_FILE = Path("submissions.jsonl")


@app.get("/")
def home():
    return render_template("index.html")


@app.post("/save")
def save():
    payload = request.get_json(silent=True) or {}
    record = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "name": str(payload.get("name", "")).strip(),
        "step2_choice": str(payload.get("step2_choice", "")).strip(),
        "accepted": bool(payload.get("accepted", False)),
        "answers": payload.get("answers", {}),
    }
    with DATA_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
