pipeline {

	agent any
	environment {
		DOCKER_HUB=credentials('docker_hub')
	}
	stages {
		stage('Test') {
			steps {
				sh '''ls -l  && cd cos_project3 && python3 manage.py test'''
			}	
		}
                stage('Docker-build') {
                        steps {
                                sh 'cd cos_project3 && docker build . -t chljidn/recos:recos'
                        }
                }
		stage('Docker-login') {
			steps {
				sh 'echo $DOCKER_HUB_PSW | docker login -u $DOCKER_HUB_USR --password-stdin'
			}
		}
		stage('Docker-push') {
			steps {
				sh 'docker push chljidn/recos:recos'
			}
		}
		stage('Docker-rmi') {
			steps {
				sh 'docker rmi chljidn/recos:recos'
			}
		} 
	}
}

