@Library('jenkins-library@0.39.3') _

pipeline {
  agent any
  parameters {
    booleanParam(defaultValue: false, description: 'override manifest version', name: 'OVERRIDE_MANIFEST')
  }
  options {
    disableConcurrentBuilds()
    skipDefaultCheckout true
    buildDiscarder logRotator(artifactDaysToKeepStr: '', artifactNumToKeepStr: '', daysToKeepStr: '10', numToKeepStr: '10')
  }

  stages {
    stage('Clean WS and checkout SCM') {
      steps {
        deleteDir()
        checkout scm
        script {
          utils.abortPseudoBuild()
        }
      }
    }
    stage('Increment Version') {
      steps {
        script {
          if (versions.isReleaseBuild()) {
            versions.increment('python')
          }
          version = versions.getVersion('python')
        }
      }
    }
    stage('Build') {
      agent {
        docker {
          image 'python:3.7.0'
          args "-u root -v ${workspace}:/workspace"
        }
      }
      steps {
        sh 'rm -rf /workspace/dist/'
        sh 'python3 -m venv /tmp/venv'
        sh '/tmp/venv/bin/pip install PyYAML==5.1 wheel==0.33.4'
        sh "export APP_VERSION=${version}; cd /workspace && /tmp/venv/bin/python3 /workspace/setup.py bdist_wheel"
        sh 'cp /workspace/requirements.txt /workspace/dist/'
      }
    }
    stage('Publish') {
      steps {
        script {
          wheelFile = "meta_hackathon_finance-${version}-py3-none-any.whl"
          artifacts.publishEngati("dist/${wheelFile}", "meta-hackathon-finance/${version}")
          artifacts.publishEngati("dist/requirements.txt", "meta-hackathon-finance/${version}")
        }
      }
    }
    stage('Push to Git') {
      steps {
        script {
          if (versions.isReleaseBuild()) {
            sshagent(['jenkins-coviam']) {
              sh "git push origin HEAD:$BRANCH_NAME --tags"
            }
            manifest.publish(
              'meta_hackathon_finance',
              'git@gitlab.engati.ops:engati/engati-infrastructure/deployment-ansible.git',
              'envs/qa',
              versions.getVersion('python'),
              params.OVERRIDE_MANIFEST
            )
          }
        }
      }
    }
  }
  post {
    always {
      script {
        displayName = "#${BUILD_NUMBER}: ${versions.getVersion('python')}"
        currentBuild.displayName = "${displayName}"
        sh "sudo chown -R jenkins: ${workspace}"
        displayName = "#${BUILD_NUMBER}: ${versions.getVersion('python')}"
        currentBuild.displayName = "${displayName}"
        notification.buildStatus("#tech-builds")
      }
      cleanWs()
    }
  }
}
