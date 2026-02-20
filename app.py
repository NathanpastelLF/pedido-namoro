from datetime import datetime, timezone
import json
import os
import urllib.parse
import urllib.request
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


@app.post("/notify")
def notify():
    data = request.get_json(silent=True) or {}

    name = str(data.get("name", "")).strip()
    answer = str(data.get("answer", "")).strip()
    ok = data.get("score_ok", 0)
    err = data.get("score_err", 0)

    token = os.environ.get("TG_BOT_TOKEN", "")
    chat_id = os.environ.get("TG_CHAT_ID", "")

    if not token or not chat_id:
        return jsonify({"ok": False, "error": "Missing TG_BOT_TOKEN or TG_CHAT_ID"}), 400

    text = f"💌 Pedido de namoro\n👤 {name}\n💬 Resposta: {answer}\n🎯 Acertos: {ok} | ❌ Erros: {err}"

    url = f"https://api.telegram.org/bot{token}/sendMessage?" + urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": text
    })

    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            resp.read()
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)