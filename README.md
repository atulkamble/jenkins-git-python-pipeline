# Jenkins Git Python Pipeline

A production-ready **Jenkins Declarative Pipeline** for a Python Flask application. This pipeline pulls code from a GitHub repository, sets up a virtual environment, installs dependencies, runs tests, performs a health check, and archives logs.

---

## Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [System Setup](#system-setup)
- [Jenkins Plugin Setup](#jenkins-plugin-setup)
- [Application Code](#application-code)
- [Pipeline Stages](#pipeline-stages)
- [Jenkins Job Configuration](#jenkins-job-configuration)
- [Running the Pipeline](#running-the-pipeline)
- [Expected Output](#expected-output)
- [Troubleshooting](#troubleshooting)

---

## Overview

This project demonstrates a CI pipeline using Jenkins and Git for a Python Flask web application. The pipeline automates the full lifecycle:

```
Git Checkout → Python Setup → Virtual Env → Install Deps → Tests → Validate → Run App → Health Check → Cleanup
```

---

## Project Structure

```
jenkins-git-python-pipeline/
├── Jenkinsfile          # Jenkins Declarative Pipeline definition
├── app.py               # Flask web application
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation
```

---

## Prerequisites

| Requirement | Version |
|---|---|
| Jenkins | 2.400+ |
| Python | 3.10+ |
| pip | 23+ |
| Git | 2.x |
| curl | any |

- Jenkins installed (locally or on EC2/VM)
- Git and Pipeline plugins installed in Jenkins
- GitHub repository with SSH or HTTPS access
- Agent node has Python 3 available

---

## System Setup

### 1. Install Python pip and venv (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install python3-pip
sudo apt install python3.12-venv
```

### 2. Verify installation

```bash
python3 --version
pip --version
```

Expected output:
```
Python 3.12.x
pip 24.x from /usr/lib/python3/dist-packages/pip (python 3.12)
```

### 3. Install curl (required for health check stage)

```bash
sudo apt install curl
```

---

## Jenkins Plugin Setup

Go to **Manage Jenkins → Plugin Manager** and install:

| Plugin | Purpose |
|---|---|
| Git Plugin | Clone repositories from GitHub |
| Pipeline | Enable Declarative Pipeline support |
| Timestamper | Add timestamps to console output |
| GitHub Integration Plugin | Webhook-based auto-trigger (optional) |

---

## Application Code

### `app.py` — Flask Application

```python
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
```

### `requirements.txt`

```
flask>=3.0.0
```

---

## Pipeline Stages

The `Jenkinsfile` defines the following stages:

| # | Stage | Description |
|---|---|---|
| 1 | **Checkout** | Clones the `main` branch from GitHub |
| 2 | **Check Python Version** | Prints Python and pip versions |
| 3 | **Create Virtual Environment** | Creates a fresh `venv/` directory |
| 4 | **Install Dependencies** | Installs packages from `requirements.txt` + pytest |
| 5 | **Run Tests** | Runs `pytest tests/` if a tests directory exists |
| 6 | **Validate Python Code** | Compiles all `.py` files to catch syntax errors |
| 7 | **Run Application** | Starts Flask app in the background via `nohup` |
| 8 | **Health Check** | Polls `http://127.0.0.1:5000` up to 10 times |
| **Post** | **Cleanup** | Stops app, archives `flask-app.log`, removes `__pycache__` |

---

## Jenkins Job Configuration

### Step 1 — Create a New Pipeline Job

1. Open Jenkins Dashboard → **New Item**
2. Enter name: `jenkins-git-python-pipeline`
3. Select type: **Pipeline** → click **OK**

### Step 2 — Configure Pipeline Source

Under **Pipeline** section:

- Definition: `Pipeline script from SCM`
- SCM: `Git`
- Repository URL: `https://github.com/atulkamble/jenkins-git-python-pipeline.git`
- Branch: `*/main`
- Script Path: `Jenkinsfile`

### Step 3 — (Optional) Enable Webhook Trigger

Under **Build Triggers**:
- Check **GitHub hook trigger for GITScm polling**
- Add a webhook in your GitHub repo settings pointing to `http://<jenkins-url>/github-webhook/`

---

## Running the Pipeline

1. Click **Build Now** on the job page
2. Open **Console Output** to monitor live logs
3. Each stage will be visible in the **Stage View**

---

## Expected Output

```
[Checkout] Checking out source code...
[Check Python Version] Python 3.12.x / pip 24.x
[Create Virtual Environment] Created venv/
[Install Dependencies] Successfully installed Flask-3.x ...
[Run Tests] No tests directory found. Skipping pytest.
[Validate Python Code] Compiling ...
[Run Application] Flask application started with PID 12345
[Health Check] Application health check passed.
[Post] Flask application stopped.
[Post] Archiving artifacts: flask-app.log
flask-app pipeline completed successfully.
```

---

## Troubleshooting

| Problem | Solution |
|---|---|
| `python3: command not found` | Install Python: `sudo apt install python3` |
| `pip: command not found` | Run `sudo apt install python3-pip` |
| `venv` module missing | Run `sudo apt install python3.12-venv` |
| Health check fails | Check `flask-app.log` archived in Jenkins build artifacts |
| Port 5000 already in use | Kill existing process: `fuser -k 5000/tcp` |
| Jenkins cannot clone repo | Verify repo URL and network access from the Jenkins agent |

---

## Author

**Atul Kamble** — [github.com/atulkamble](https://github.com/atulkamble)

---

## License

This project is licensed under the terms of the [LICENSE](LICENSE) file.
