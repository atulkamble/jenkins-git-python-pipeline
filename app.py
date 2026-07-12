import os
import platform
import sys
from datetime import datetime
from flask import Flask, render_template, jsonify

app = Flask(__name__)

START_TIME = datetime.utcnow()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/health")
def health():
    uptime = str(datetime.utcnow() - START_TIME).split(".")[0]
    return jsonify({
        "status": "ok",
        "uptime": uptime,
        "python": sys.version.split()[0],
        "platform": platform.system(),
        "timestamp": datetime.utcnow().isoformat() + "Z",
    })


if __name__ == "__main__":
    # Development only — use Gunicorn in production
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
