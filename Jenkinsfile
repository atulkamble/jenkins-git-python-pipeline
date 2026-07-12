pipeline {
    agent any

    environment {
        // Define environment variables here
        APP_NAME = 'flask-app'
        VENV_DIR = 'venv'
        MY_VAR = 'some_value'
    }

    options {
         timestamps() // Add timestamps to the console output
         disableConcurrentBuilds() // Prevent concurrent builds of the same job
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm 
                // Add checkout steps here
                git branch: 'main', url: 'https://github.com/atulkamble/jenkins-git-python-pipeline.git'
            }
        }
        stage('Check Python Version') {
            steps {
                echo 'Checking Python version...'
                python --version 
                pip --version   
            }
        }
        stage('Create Virtual Environment') {
            steps {
                echo 'Creating virtual environment...'
                python -m venv $VENV_DIR    
            }
        }

        stage('Install Dependencies') {
            steps {
                echo 'Installing dependencies...'
                sh '''
                    source $VENV_DIR/bin/activate
                    pip install -r requirements.txt
                '''
            }
        }
    }

    post {
        always {
            echo 'This will always run after the stages.'
        }
        success {
            echo 'This will run only if the pipeline succeeds.'
        }
        failure {
            echo 'This will run only if the pipeline fails.'
        }
    }
}