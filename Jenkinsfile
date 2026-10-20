
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
                script {
                    // Prevent reuse of a report from an older build
                    sh 'rm -f results.xml'

                    // Capture the exit code instead of immediately failing
                    def exitCode = sh(
                        script: '''
                            docker run --rm \
                              -v "$WORKSPACE:/reports" \
                              my-python-image:ci \
                              python -m pytest -v --junitxml=/reports/results.xml
                        ''',
                        returnStatus: true
                    )

                    echo "Test execution exit code: ${exitCode}"

                    if (exitCode == 0) {
                        if (!fileExists('results.xml')) {
                            error('Tests returned success but JUnit report is missing')
                        }
                        echo 'SUCCESS: All tests passed'

                    } else if (exitCode == 1) {
                        if (!fileExists('results.xml')) {
                            error('Exit code 1 without JUnit report: execution failure')
                        }

                        // Confirm XML is readable and contains a test failure
                        def reportStatus = sh(
                            script: '''
                                python3 - <<'PY'
import xml.etree.ElementTree as ET

try:
    root = ET.parse("results.xml").getroot()
    suites = ([root] if root.tag == "testsuite"
              else root.findall("testsuite"))

    tests = sum(int(s.get("tests", 0)) for s in suites)
    failures = sum(int(s.get("failures", 0)) for s in suites)
    errors = sum(int(s.get("errors", 0)) for s in suites)

    if tests > 0 and (failures > 0 or errors > 0):
        raise SystemExit(0)
except (ET.ParseError, OSError, ValueError):
    pass

raise SystemExit(1)
PY
                            ''',
                            returnStatus: true
                        )

                        if (reportStatus == 0) {
                            unstable('Pytest reported failed or errored tests')
                        } else {
                            error('Exit code 1 without valid failing test results')
                        }

                    } else if (exitCode == 2) {
                        error('Pytest execution interrupted (exit code 2)')

                    } else if (exitCode == 3) {
                        error('Pytest internal error (exit code 3)')

                    } else if (exitCode == 4) {
                        error('Incorrect pytest usage (exit code 4)')

                    } else if (exitCode == 5) {
                        error('No tests collected (exit code 5)')

                    } else if (exitCode == 125) {
                        error('Docker failed to start the container (exit code 125)')

                    } else if (exitCode == 126) {
                        error('Container command cannot execute (exit code 126)')

                    } else if (exitCode == 127) {
                        error('Container command not found (exit code 127)')

                    } else {
                        error("Unexpected execution failure: exit code ${exitCode}")
                    }
                }
            }
        }
    }

    post {
        always {
            script {
                if (fileExists('results.xml')) {
                    junit 'results.xml'
                } else {
                    echo 'No JUnit report available to publish'
                }
            }
        }
    }
}
