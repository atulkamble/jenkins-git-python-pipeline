from flask import Flask

app = Flask(__name__)


@app.route("/")
def index():
    return "Hello from Jenkins pipeline project!"


@app.route("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
