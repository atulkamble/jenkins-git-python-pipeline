pipeline {
    agent any

    environment {
        APP_NAME        = 'flask-app'
        VENV_DIR        = 'venv'
        APP_PORT        = '5000'

        // Docker
        DOCKER_IMAGE    = 'atulkamble/flask-pipeline-app'
        DOCKER_TAG      = "build-${BUILD_NUMBER}"
        DOCKER_LATEST   = 'latest'
        DOCKER_REGISTRY = 'https://index.docker.io/v1/'
        DOCKER_CREDS_ID = 'docker-creds'   // Jenkins credential ID
        CONTAINER_NAME  = 'flask-pipeline-app'
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

        stage('Docker Build') {
            steps {
                echo 'Building Docker image...'

                sh '''
                    docker build \
                        --tag "$DOCKER_IMAGE:$DOCKER_TAG" \
                        --tag "$DOCKER_IMAGE:$DOCKER_LATEST" \
                        --label "build.number=$BUILD_NUMBER" \
                        --label "build.url=$BUILD_URL" \
                        --file Dockerfile \
                        .

                    echo "========================================================"
                    echo "  Docker image built successfully"
                    echo "  Image : $DOCKER_IMAGE:$DOCKER_TAG"
                    echo "  Also  : $DOCKER_IMAGE:$DOCKER_LATEST"
                    echo "========================================================"
                    docker images "$DOCKER_IMAGE"
                '''
            }
        }

        stage('Docker Test') {
            steps {
                echo 'Running container smoke test...'

                sh '''
                    # Stop any leftover test container
                    docker rm -f flask-test 2>/dev/null || true

                    # Start test container on a different port to avoid conflict
                    docker run -d \
                        --name flask-test \
                        --publish 5001:5000 \
                        "$DOCKER_IMAGE:$DOCKER_TAG"

                    echo "Test container started. Waiting for app to be ready..."
                    sleep 5

                    TEST_PASSED=false
                    for attempt in 1 2 3 4 5
                    do
                        if curl --fail --silent "http://127.0.0.1:5001/" > /dev/null
                        then
                            echo "Container smoke test passed on attempt $attempt."
                            TEST_PASSED=true
                            break
                        fi
                        echo "Attempt $attempt failed, retrying..."
                        sleep 3
                    done

                    # Print container logs before removing
                    docker logs flask-test || true

                    # Remove test container
                    docker rm -f flask-test || true

                    if [ "$TEST_PASSED" != "true" ]
                    then
                        echo "ERROR: Docker container smoke test failed."
                        exit 1
                    fi
                '''
            }
        }

        stage('Docker Push') {
            steps {
                echo 'Pushing Docker image to Docker Hub...'

                withCredentials([usernamePassword(
                    credentialsId: "${DOCKER_CREDS_ID}",
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh '''
                        echo "$DOCKER_PASS" | docker login "$DOCKER_REGISTRY" \
                            --username "$DOCKER_USER" --password-stdin

                        docker push "$DOCKER_IMAGE:$DOCKER_TAG"
                        docker push "$DOCKER_IMAGE:$DOCKER_LATEST"

                        echo "========================================================"
                        echo "  Pushed: $DOCKER_IMAGE:$DOCKER_TAG"
                        echo "  Pushed: $DOCKER_IMAGE:$DOCKER_LATEST"
                        echo "  Hub URL: https://hub.docker.com/r/$DOCKER_IMAGE"
                        echo "========================================================"

                        docker logout
                    '''
                }
            }
        }

        stage('Docker Run') {
            steps {
                echo 'Starting production container...'

                sh '''
                    # Stop and remove any previous production container
                    docker stop "$CONTAINER_NAME" 2>/dev/null || true
                    docker rm   "$CONTAINER_NAME" 2>/dev/null || true

                    # Run the production container
                    docker run -d \
                        --name "$CONTAINER_NAME" \
                        --publish "$APP_PORT":5000 \
                        --restart unless-stopped \
                        --log-driver json-file \
                        --log-opt max-size=10m \
                        --log-opt max-file=3 \
                        "$DOCKER_IMAGE:$DOCKER_TAG"

                    echo "Container $CONTAINER_NAME started."
                    docker ps --filter "name=$CONTAINER_NAME" --format "table {{.ID}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"
                '''
            }
        }

        stage('Run Application') {
            when {
                expression {
                    // Fallback: only run Gunicorn directly if Docker is not available
                    sh(script: 'command -v docker', returnStatus: true) != 0
                }
            }
            steps {
                echo 'Docker not available — starting Flask application with Gunicorn (fallback)...'

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
                    # UFW — attempt without sudo; print manual command if it fails
                    if command -v ufw > /dev/null 2>&1; then
                        if ufw allow "$APP_PORT"/tcp 2>/dev/null; then
                            ufw --force enable 2>/dev/null || true
                            echo "UFW: port $APP_PORT opened."
                        else
                            echo "UFW requires sudo. Run manually on the server:"
                            echo "  sudo ufw allow $APP_PORT/tcp && sudo ufw --force enable"
                        fi
                    else
                        echo "UFW not found — skipping UFW rule."
                    fi

                    # firewalld (RHEL/CentOS) — attempt without sudo
                    if command -v firewall-cmd > /dev/null 2>&1; then
                        if firewall-cmd --permanent --add-port="$APP_PORT"/tcp 2>/dev/null; then
                            firewall-cmd --reload 2>/dev/null || true
                            echo "firewalld: port $APP_PORT opened."
                        else
                            echo "firewalld requires sudo. Run manually on the server:"
                            echo "  sudo firewall-cmd --permanent --add-port=$APP_PORT/tcp && sudo firewall-cmd --reload"
                        fi
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

        stage('Diagnose Network') {
            steps {
                echo 'Verifying app is reachable on all interfaces...'

                sh '''
                    PUBLIC_IP=$(cat public-ip.txt 2>/dev/null || echo "UNKNOWN")

                    echo "========================================================"
                    echo "  NETWORK DIAGNOSTICS"
                    echo "========================================================"

                    echo ""
                    echo "--- Listening sockets on port $APP_PORT ---"
                    ss -tlnp "sport = :$APP_PORT" 2>/dev/null \
                        || netstat -tlnp 2>/dev/null | grep ":$APP_PORT" \
                        || echo "ss/netstat not available"

                    echo ""
                    echo "--- Local connectivity test ---"
                    curl --silent --max-time 5 --write-out "HTTP %{http_code}" \
                        "http://127.0.0.1:$APP_PORT/" || echo "FAILED"

                    echo ""
                    echo "--- Health endpoint test ---"
                    curl --silent --max-time 5 --write-out "HTTP %{http_code}" \
                        "http://127.0.0.1:$APP_PORT/health" || echo "FAILED"

                    echo ""
                    echo "--- UFW status ---"
                    ufw status 2>/dev/null || echo "UFW not available or requires sudo"

                    echo ""
                    echo "========================================================"
                    echo "  ACTION REQUIRED - Open inbound port $APP_PORT in your"
                    echo "  cloud provider security group / firewall:"
                    echo ""
                    echo "  OS Firewall (run on server as root):"
                    echo "    sudo ufw allow $APP_PORT/tcp"
                    echo ""
                    echo "  AWS EC2 (Security Group):"
                    echo "    Inbound rule: TCP $APP_PORT  Source: 0.0.0.0/0"
                    echo ""
                    echo "  Azure VM (NSG):"
                    echo "    az network nsg rule create"
                    echo "      --resource-group YOUR_RG --nsg-name YOUR_NSG"
                    echo "      --name Allow-$APP_PORT --priority 1001"
                    echo "      --protocol Tcp --destination-port-ranges $APP_PORT"
                    echo "      --access Allow --direction Inbound"
                    echo ""
                    echo "  GCP (Firewall Rule):"
                    echo "    gcloud compute firewall-rules create allow-$APP_PORT"
                    echo "      --allow tcp:$APP_PORT --source-ranges 0.0.0.0/0"
                    echo ""
                    echo "  Public URL: http://$PUBLIC_IP:$APP_PORT"
                    echo "========================================================"
                '''
            }
        }

        stage('Keep Running') {
            steps {
                echo 'Keeping container running after pipeline completes...'

                sh '''
                    PUBLIC_IP=$(cat public-ip.txt 2>/dev/null || echo "UNKNOWN")

                    if docker inspect "$CONTAINER_NAME" > /dev/null 2>&1
                    then
                        CONTAINER_STATUS=$(docker inspect \
                            --format "{{.State.Status}}" "$CONTAINER_NAME")

                        echo "========================================================"
                        echo "  Docker container is $CONTAINER_STATUS"
                        echo "========================================================"
                        echo "  Container  : $CONTAINER_NAME"
                        echo "  Image      : $DOCKER_IMAGE:$DOCKER_TAG"
                        echo "  Local URL  : http://127.0.0.1:$APP_PORT"
                        echo "  Public URL : http://$PUBLIC_IP:$APP_PORT"
                        echo "  Health URL : http://$PUBLIC_IP:$APP_PORT/health"
                        echo "  Docker Hub : https://hub.docker.com/r/$DOCKER_IMAGE"
                        echo "--------------------------------------------------------"
                        echo "  Manage:"
                        echo "    Logs  : docker logs -f $CONTAINER_NAME"
                        echo "    Stop  : docker stop $CONTAINER_NAME"
                        echo "    Stats : docker stats $CONTAINER_NAME"
                        echo "========================================================"

                        if [ "$CONTAINER_STATUS" != "running" ]
                        then
                            echo "ERROR: Container is not in running state."
                            docker logs "$CONTAINER_NAME" || true
                            exit 1
                        fi
                    else
                        # Fallback: check Gunicorn PID
                        APP_PID=$(cat flask-app.pid 2>/dev/null || echo "")
                        if [ -n "$APP_PID" ] && kill -0 "$APP_PID" 2>/dev/null
                        then
                            disown "$APP_PID" 2>/dev/null || true
                            echo "Gunicorn fallback running with PID $APP_PID"
                            echo "Public URL : http://$PUBLIC_IP:$APP_PORT"
                        else
                            echo "ERROR: Neither Docker container nor Gunicorn is running."
                            exit 1
                        fi
                    fi
                '''
            }
        }
    }

    post {
        always {
            echo 'Pipeline post-actions: collecting logs and artifacts...'

            sh '''
                # Collect Docker container logs
                if docker inspect "$CONTAINER_NAME" > /dev/null 2>&1
                then
                    docker logs "$CONTAINER_NAME" > flask-app.log 2>&1 || true
                    echo "Docker container $CONTAINER_NAME is still running (keep-running mode)."
                fi

                # Gunicorn PID cleanup (fallback mode)
                if [ -f flask-app.pid ]
                then
                    APP_PID=$(cat flask-app.pid)
                    if kill -0 "$APP_PID" 2>/dev/null
                    then
                        echo "Gunicorn is still running with PID $APP_PID."
                    fi
                    rm -f flask-app.pid
                fi
            '''

            archiveArtifacts artifacts: 'flask-app.log, gunicorn-boot.log, public-ip.txt',
                             allowEmptyArchive: true
        }

        success {
            echo "${APP_NAME} pipeline completed successfully."
            sh '''
                echo "Docker image : $DOCKER_IMAGE:$DOCKER_TAG"
                echo "Container    : $CONTAINER_NAME"
                docker ps --filter "name=$CONTAINER_NAME" \
                    --format "table {{.ID}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}" || true
            '''
        }

        failure {
            echo "${APP_NAME} pipeline failed."
            sh '''
                echo "--- Docker container logs (if any) ---"
                docker logs "$CONTAINER_NAME" --tail 50 2>/dev/null || true
                echo "--- Gunicorn boot log (if any) ---"
                cat gunicorn-boot.log 2>/dev/null || true
            '''
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
