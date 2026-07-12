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
                echo 'Starting Flask application with Gunicorn (production)...'

                sh '''
                    WORKERS=$(( 2 * $(nproc) + 1 ))

                    nohup "$VENV_DIR/bin/gunicorn" \
                        --workers "$WORKERS" \
                        --bind 0.0.0.0:"$APP_PORT" \
                        --timeout 120 \
                        --access-logfile flask-app.log \
                        --error-logfile flask-app.log \
                        --log-level info \
                        --pid flask-app.pid \
                        app:app > gunicorn-boot.log 2>&1 &

                    sleep 3
                    echo "Gunicorn started with $WORKERS workers on port $APP_PORT"
                    echo "PID file: $(cat flask-app.pid 2>/dev/null || echo \'not yet written\')"
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

        stage('Expose to Internet') {
            steps {
                echo 'Opening firewall port and fetching public IP...'

                sh '''
                    # Open port in UFW firewall (Ubuntu/Debian)
                    if command -v ufw > /dev/null 2>&1; then
                        ufw allow "$APP_PORT"/tcp || true
                        echo "UFW: port $APP_PORT opened."
                    else
                        echo "UFW not found — skipping firewall rule (open port $APP_PORT manually if needed)."
                    fi

                    # Open port in firewalld (RHEL/CentOS)
                    if command -v firewall-cmd > /dev/null 2>&1; then
                        firewall-cmd --permanent --add-port="$APP_PORT"/tcp || true
                        firewall-cmd --reload || true
                        echo "firewalld: port $APP_PORT opened."
                    fi

                    # Resolve public IP
                    PUBLIC_IP=$(curl --silent --max-time 5 https://api.ipify.org \
                        || curl --silent --max-time 5 https://ifconfig.me \
                        || curl --silent --max-time 5 https://icanhazip.com \
                        || echo "UNKNOWN")

                    echo "$PUBLIC_IP" > public-ip.txt
                    echo "Public IP resolved: $PUBLIC_IP"
                '''
            }
        }

        stage('Keep Running') {
            steps {
                echo 'Keeping Flask application running after pipeline completes...'

                sh '''
                    APP_PID=$(cat flask-app.pid 2>/dev/null || echo "")
                    PUBLIC_IP=$(cat public-ip.txt 2>/dev/null || echo "UNKNOWN")

                    if [ -n "$APP_PID" ] && kill -0 "$APP_PID" 2>/dev/null
                    then
                        # Disown the process so it survives beyond this build
                        disown "$APP_PID" 2>/dev/null || true

                        echo "========================================================"
                        echo "  Flask app is RUNNING and publicly accessible"
                        echo "========================================================"
                        echo "  PID          : $APP_PID"
                        echo "  Local URL    : http://127.0.0.1:$APP_PORT"
                        echo "  Public URL   : http://$PUBLIC_IP:$APP_PORT"
                        echo "  Health URL   : http://$PUBLIC_IP:$APP_PORT/health"
                        echo "  Log file     : $(pwd)/flask-app.log"
                        echo "  Stop app     : kill $APP_PID"
                        echo "--------------------------------------------------------"
                        echo "  NOTE: Ensure your cloud security group / NSG allows"
                        echo "  inbound TCP traffic on port $APP_PORT from 0.0.0.0/0"
                        echo "========================================================"
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

            archiveArtifacts artifacts: 'flask-app.log, gunicorn-boot.log, public-ip.txt',
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
