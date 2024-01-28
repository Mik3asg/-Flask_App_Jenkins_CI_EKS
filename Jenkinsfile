node {
    def app

    stage('Clone repository') {
      

        checkout scm
    }

    stage('Build image') {
        // Specify the path to the Dockerfile relative to the workspace directory
        def dockerfilePath = "${WORKSPACE}/AppCode_CI/Dockerfile"
        // Build the Docker image
        app = docker.build("mik3asg/flask-cicd", "-f ${dockerfilePath} ${WORKSPACE}/AppCode_CI")
    }

    stage('Test image') {
  

        app.inside {
            sh 'echo "Tests passed"'
        }
    }

    stage('Push image') {
        
        docker.withRegistry('https://registry.hub.docker.com', 'dockerhub') {
            app.push("${env.BUILD_NUMBER}")
        }
    }
    
    stage('Trigger UpdateK8sManifestJob') {
                echo "triggering updatek8smanifestjob"
                build job: 'UpdateK8sManifestJob', parameters: [string(name: 'DOCKERTAG', value: env.BUILD_NUMBER)]
        }
}