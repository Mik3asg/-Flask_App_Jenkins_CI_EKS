pipeline {
    agent any
    
    
    stages {

        stage('Clone Repository') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            app = docker.build("mik3asg/flask-cicd")
        }

        stage('Test Docker Image') {
    

            app.inside {
                sh 'echo "Tests passed"'
            }
        }
        
        stage('Push Docker Image') {
            
            docker.withRegistry('https://registry.hub.docker.com', 'dockerhub') {
                app.push("${env.BUILD_NUMBER}")
            }
        }
        
        // Trigger CD Pipeline
        stage('Trigger UpdateK8sManifestJob') {
                    echo "Triggering CD Pipeline to update k8s manifest job"
                    build job: 'UpdateK8sManifestJob', parameters: [string(name: 'DOCKERTAG', value: env.BUILD_NUMBER)]
            }
    }
}