pipeline {
    agent any

    environment {
        APP_NAME = 'flask-app'
        VENV_DIR = 'venv'
        APP_PORT = '5000'
    }

    options {
        timestamps()
        disableConcurrentBuilds()
        timeout(time: 15, unit: 'MINUTES')
    }

    stages {

        stage('Checkout') {
            steps {
                echo 'Checking out source code...'

                git branch: 'main',
                    url: 'https://github.com/atulkamble/jenkins-git-python-pipeline.git'
            }
        }

        stage('Check Python Version') {
            steps {
                echo 'Checking Python and pip versions...'

                sh '''
                    python3 --version
                    python3 -m pip --version
                '''
            }
        }

        stage('Create Virtual Environment') {
            steps {
                echo 'Creating Python virtual environment...'

                sh '''
                    rm -rf "$VENV_DIR"
                    python3 -m venv "$VENV_DIR"
                '''
            }
        }

        stage('Install Dependencies') {
            steps {
                echo 'Installing application dependencies...'

                sh '''
                    "$VENV_DIR/bin/python" -m pip install --upgrade pip
                    "$VENV_DIR/bin/python" -m pip install -r requirements.txt
                    "$VENV_DIR/bin/python" -m pip install pytest
                '''
            }
        }

        stage('Run Tests') {
            steps {
                echo 'Running application tests...'

                sh '''
                    if [ -d "tests" ]; then
                        "$VENV_DIR/bin/python" -m pytest tests/ -v
                    else
                        echo "No tests directory found. Skipping pytest."
                    fi
                '''
            }
        }

        stage('Validate Python Code') {
            steps {
                echo 'Validating Python syntax...'

                sh '''
                    "$VENV_DIR/bin/python" -m compileall .
                '''
            }
        }

        stage('Run Application') {
            steps {
                echo 'Starting Flask application for smoke testing...'

                sh '''
                    nohup "$VENV_DIR/bin/python" app.py > flask-app.log 2>&1 &
                    echo $! > flask-app.pid

                    echo "Flask application started with PID $(cat flask-app.pid)"
                '''
            }
        }

        stage('Health Check') {
            steps {
                echo 'Checking Flask application availability...'

                sh '''
                    HEALTH_CHECK_PASSED=false

                    for attempt in 1 2 3 4 5 6 7 8 9 10
                    do
                        if curl --fail --silent "http://127.0.0.1:$APP_PORT" > /dev/null
                        then
                            echo "Application health check passed."
                            HEALTH_CHECK_PASSED=true
                            break
                        fi

                        echo "Waiting for the application: attempt $attempt of 10"
                        sleep 3
                    done

                    if [ "$HEALTH_CHECK_PASSED" != "true" ]
                    then
                        echo "Application health check failed."
                        cat flask-app.log || true
                        exit 1
                    fi
                '''
            }
        }

        stage('Keep Running') {
            steps {
                echo 'Keeping Flask application running after pipeline completes...'

                sh '''
                    APP_PID=$(cat flask-app.pid 2>/dev/null || echo "")

                    if [ -n "$APP_PID" ] && kill -0 "$APP_PID" 2>/dev/null
                    then
                        # Disown the process so it survives beyond this build
                        disown "$APP_PID" 2>/dev/null || true

                        echo "----------------------------------------------------"
                        echo "Flask app is RUNNING with PID: $APP_PID"
                        echo "Access URL : http://127.0.0.1:$APP_PORT"
                        echo "Health URL : http://127.0.0.1:$APP_PORT/health"
                        echo "Log file   : $(pwd)/flask-app.log"
                        echo "Stop app   : kill $APP_PID"
                        echo "----------------------------------------------------"
                    else
                        echo "ERROR: Flask application is not running. Check flask-app.log."
                        cat flask-app.log || true
                        exit 1
                    fi
                '''
            }
        }
    }

    post {
        always {
            echo 'Pipeline post-actions: archiving logs...'

            sh '''
                if [ -f flask-app.pid ]
                then
                    APP_PID=$(cat flask-app.pid)
                    if kill -0 "$APP_PID" 2>/dev/null
                    then
                        echo "Flask app is still running with PID $APP_PID (keep-running mode)."
                    else
                        echo "Flask app is not running."
                    fi
                    rm -f flask-app.pid
                fi
            '''

            archiveArtifacts artifacts: 'flask-app.log',
                             allowEmptyArchive: true
        }

        success {
            echo "${APP_NAME} pipeline completed successfully."
        }

        failure {
            echo "${APP_NAME} pipeline failed. Check the Jenkins console output and flask-app.log."
        }

        cleanup {
            echo 'Cleaning temporary Python files...'

            sh '''
                find . -type d -name "__pycache__" \
                    -exec rm -rf {} + 2>/dev/null || true

                find . -type f -name "*.pyc" \
                    -delete 2>/dev/null || true
            '''
        }
    }
}
