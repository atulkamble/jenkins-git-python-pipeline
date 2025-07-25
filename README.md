**Jenkins Pipeline using Git** with complete code and step-by-step instructions for setup. This example covers a **Declarative Pipeline** that pulls code from a GitHub repository and performs a simple build (you can later add Docker/Kubernetes/Terraform steps).

---

### ✅ Use Case

Clone a GitHub repository → build using shell command → archive artifacts.

---

## 🧱 Prerequisites

1. Jenkins installed (locally or on EC2)
2. Jenkins user has Git and Pipeline plugin installed
3. GitHub repository (your project)
4. Jenkins job with GitHub access (SSH or HTTPS)

---

## 🔧 Step 1: Install Required Jenkins Plugins

Go to **Manage Jenkins → Plugins Manager** and install:

* Git Plugin
* Pipeline
* GitHub Integration Plugin (optional)

---

## 📝 Step 2: Create GitHub Repo (Example Structure)

Example project structure:

```
my-app/
├── Jenkinsfile
├── app.py
└── requirements.txt
```

Sample `app.py`:

```python
print("Hello from Jenkins pipeline project")
```

Sample `requirements.txt`:

```
flask
```

---

## 🔁 Step 3: Jenkinsfile Code

Create a `Jenkinsfile` at the root of your GitHub repo:

```groovy
pipeline {
    agent any

    environment {
        PROJECT_DIR = "my-app"
    }

    stages {
        stage('Clone Repository') {
            steps {
                git branch: 'main', url: 'https://github.com/yourusername/your-repo.git'
            }
        }

        stage('Install Dependencies') {
            steps {
                sh 'pip install -r requirements.txt'
            }
        }

        stage('Run App') {
            steps {
                sh 'python app.py'
            }
        }

        stage('Archive Artifacts') {
            steps {
                archiveArtifacts artifacts: '**/*.py', fingerprint: true
            }
        }
    }
}
```

---

## ⚙️ Step 4: Create Jenkins Pipeline Job

1. **Jenkins Dashboard → New Item**
2. Name: `my-git-pipeline`
3. Type: **Pipeline**
4. Under Pipeline → Choose **Pipeline script from SCM**

   * SCM: Git
   * Repo URL: `https://github.com/yourusername/your-repo.git`
   * Branch: `*/main`
   * Script Path: `Jenkinsfile`

---

## ▶️ Step 5: Build the Job

* Click **Build Now**
* Go to **Console Output** to view logs
* You should see code cloned, dependencies installed, and app executed

---

## ✅ Output

```
Running: git clone ...
+ pip install -r requirements.txt
+ python app.py
Hello from Jenkins pipeline project
```

---
