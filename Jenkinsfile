
def runTestGroup(String testFile, String reportFile) {
    withEnv([
        "TEST_FILE=${testFile}",
        "REPORT_FILE=${reportFile}"
    ]) {
        def exitCode = sh(
            script: '''
                docker run --rm \
                  -v "$WORKSPACE:/reports" \
                  my-python-image:ci \
                  python -m pytest -v "$TEST_FILE" \
                  --junitxml="/reports/$REPORT_FILE"
            ''',
            returnStatus: true
        )

        echo "${testFile} exited with code ${exitCode}"

        if (exitCode == 0) {
            if (!fileExists(reportFile)) {
                error("Successful execution but missing report: ${reportFile}")
            }
            echo "${testFile}: SUCCESS"
        } else if (exitCode == 1) {
            if (!fileExists(reportFile)) {
                error("Exit code 1 but report missing: ${reportFile}")
            }

            def reportCheck = sh(
                script: """
                    python3 - '${reportFile}' <<'PY'
import sys
import xml.etree.ElementTree as ET

try:
    root = ET.parse(sys.argv[1]).getroot()
    if root.tag == "testsuite":
        suites = [root]
    elif root.tag == "testsuites":
        suites = root.findall("testsuite")
    else:
        raise ValueError("Unexpected XML root")

    tests = sum(int(s.get("tests", 0)) for s in suites)
    failures = sum(int(s.get("failures", 0)) for s in suites)
    errors = sum(int(s.get("errors", 0)) for s in suites)

    if tests > 0 and (failures > 0 or errors > 0):
        sys.exit(0)
except (ET.ParseError, OSError, ValueError):
    pass

sys.exit(1)
PY
                """,
                returnStatus: true
            )

            if (reportCheck == 0) {
                unstable("${testFile}: Tests failed")
            } else {
                error("${testFile}: Invalid or inconsistent JUnit report")
            }
        } else {
            def reasons = [
                2: 'Pytest interrupted',
                3: 'Pytest internal error',
                4: 'Incorrect pytest usage',
                5: 'No tests collected',
                125: 'Docker failed to start container',
                126: 'Container command cannot execute',
                127: 'Container command not found'
            ]

            def reason = reasons.get(
                exitCode,
                "Unexpected execution error"
            )

            error("${testFile}: ${reason} (exit ${exitCode})")
        }
    }
}

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

        stage('Clean Old Reports') {
            steps {
                sh 'rm -f login-results.xml sample-results.xml'
            }
        }

        stage('Run Tests in Parallel') {
            parallel {
                stage('Login Tests') {
                    steps {
                        script {
                            runTestGroup(
                                'tests/test_login.py',
                                'login-results.xml'
                            )
                        }
                    }
                }

                stage('Sample Tests') {
                    steps {
                        script {
                            runTestGroup(
                                'tests/test_sample.py',
                                'sample-results.xml'
                            )
                        }
                    }
                }
            }
        }
    }

    post {
        always {
            script {
                def reports = [
                    'login-results.xml',
                    'sample-results.xml'
                ].findAll { fileExists(it) }

                if (reports) {
                    junit testResults: reports.join(','),
                          allowEmptyResults: false
                } else {
                    echo 'No JUnit reports available'
                }
            }
        }
    }
}
