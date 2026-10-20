pipeline {
    agent any

    stages {
        stage('Verify Docker') {
            steps {
                sh 'docker --version'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t my-python-image:ci .'
            }
        }

        stage('Run Pytest in Docker') {
            steps {
                sh '''
                    docker run --rm \
                      -v "$WORKSPACE:/reports" \
                      my-python-image:ci \
                      python -m pytest -v --junitxml=/reports/results.xml
                '''
            }
        }
    }

    post {
        always {
            junit 'results.xml'
        }
    }
}
