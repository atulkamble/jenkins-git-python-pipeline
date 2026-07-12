import os
from flask import Flask

app = Flask(__name__)


@app.route("/")
def index():
    return "Hello from Jenkins pipeline project!"


@app.route("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    # Development only — use Gunicorn in production
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
