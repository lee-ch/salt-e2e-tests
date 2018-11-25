// Author: Lee Christensen - DevOps Engineer @ Adobe
// Salt State test suite
// Property of Adobe
pipeline {
    agent { label 'docker' }
    stages {
        stage('Build Environment') {
            steps {
                script {
                    def workspace = pwd()
                }
                // run our state test (runs state.highstate)
                wrap([$class: 'AnsiColorBuildWrapper', 'colorMapName': 'xterm']) {
                    sh "docker run --rm --name salt-masterless-centos7 --mount type=bind,source=${workspace}/srv/tests,target=/srv/tests salt-masterless:centos7 sh -c 'python /srv/tests/staterun.py'"
                }
            }
        }
    }
}
