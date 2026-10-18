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
                sh 'docker run --rm my-python-image:ci'
            }
        }
    }
}
