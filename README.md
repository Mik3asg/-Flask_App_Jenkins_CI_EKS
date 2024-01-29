# Flask Application Deployment into EKS using Jenkins and Argo CD

## Overview
This project showcases an end-to-end DevOps pipeline for deploying a basic Flask application using Jenkins Pipeline and GitOps (with ArgoCD) on an Amazon Elastic Kubernetes Service (EKS) cluster. It utilizes two Git repositories:

[GitHub Repository for Continous Integration hosting our basic Flask application code](https://github.com/Mik3asg/Flask_App_Jenkins_CI_EKS.git)  
[GitHub Repository for GitOps and Update of K8s Manifest](https://github.com/Mik3asg/Flask_App_Jenkins_GitOps_EKS.git)



## Pre-requisites/Assumptions:
- AWS Account created
- AWS CLI installed
- kubectl installed
- DockerHub Account created
- Application code hosted on GIT Repository

## Architecture/Design Overview

## Installation and Setup

1. **Spin up an AWS EC2 instance for a Jenkins server:**
    - Specs:
        - Instance Type: `t3.small`
        - OS: `Ubuntu`
        - Storage: `15 GiB gp2`
        - SG Inbound rules: `TCP/22, TCP/8080`
    - SSH into your EC2 instance to install Jenkins and Docker packages. 
    - Leverage `user-data` section within EC2 to include the following bash script for installing Java, Jenkins and Docker packages:

        ```bash
        #!/bin/bash

        # Update and upgrade the system
        sudo apt update && sudo apt upgrade -y

        # Install Java
        sudo apt install -y openjdk-11-jre

        # Install Jenkins
        curl -fsSL https://pkg.jenkins.io/debian/jenkins.io-2023.key | sudo gpg --dearmor -o /usr/share/keyrings/jenkins-keyring.gpg
        echo deb [signed-by=/usr/share/keyrings/jenkins-keyring.gpg] https://pkg.jenkins.io/debian binary/ | sudo tee /etc/apt/sources.list.d/jenkins.list > /dev/null
        sudo apt-get update
        sudo apt-get install -y jenkins

        # Install Docker
        sudo apt install -y docker.io

        # Grant Jenkins user permission to Docker daemon
        sudo usermod -aG docker jenkins
        sudo systemctl enable docker
        sudo systemctl restart docker
        ```

    - Check status of dependencies by running the following commands:
        - ```java -version```
        - ```sudo systemctl status jenkins```
        - ```sudo systemctl status docker ```


2. **Configure your Jenkins Server in UI:**
    - Install the required Plugins: `Manage Jenkins > Plugins > Available Plugins`. Select (Docker, Docker Pipeline, GitHub integration)
    - Restart Jenkins server
    - Configure Credentials: `Manage Jenkins > Credentials > Global > Add Credentials`
        - for GitHub (`id=github, username=your_username, password=token_generated_in_GitHub`)
        - for DockerHub (`id=dockerhub, username=your_username, password=your_dockerhub_pwd`)
    - Create 2 Jenkins Jobs:
        - For CI Pipeline: 
            - `New Item > Name=BuildAppJob > Pipeline`
                - Build Triggers=`GitHub hook trigger for GITScm polling`
                - Navigate to the GitHub repository settings and enable the Webhook by following these steps:
                    - `Settings > Webhook > Payload URL = http://jenkins_server_public_ip:8080/github-weebhook/`)
                 - `Content type=application/json`. 
                 - Confirm Add webhook
                - Pipeline Definition=`Pipeline script from SCM`
                    - SCM=`GIT`
                    - Script Path = `Jenkinsfile`
                    - Repository URL=`https://github.com/Mik3asg/Flask_App_Jenkins_CI_EKS.git`
                    - Credentials=`none` 
                    - Branch Specifier=`*/main`
        - For CD Pipeline: 
            - `New Item > Name=UpdateK8sManifestJob > Pipeline`
                - Select `This project is parameterized`
                - String Parameter: Name=`DOCKERTAG`, Default Value=`latest`
                - Pipeline Definition=`Pipeline script from SCM`
                    - SCM=`GIT`
                    - Script Path:`Jenkinsfile`
                    - Repo URL=`https://github.com/Mik3asg/Flask_App_Jenkins_GitOps_EKS.git`
                    - Credentials=``none`` # public repo
                    - Branch Specifier=`*/main`

3. **Provision an AWS EKS Cluster**
    ```bash
    eksctl create cluster --name <demo-eks> --region us-east-1 --nodegroup-name <my-nodes> --node-type t3.small --managed --nodes 2 # <demo-eks> and <my-nodes> define your own values
    ```
    Check the status of EKS Cluster (if up and running)
    ```bash
    eksctl get cluster --name demo-eks --region us-east-1  
    ```

4. **Installation and Configuration Argo CD**
    - Via CLI:
        - Follow steps provided in the official [Argo CD Documentation](https://argo-cd.readthedocs.io/en/stable/getting_started/) to:
            - Install Argo CD via CLI
            - Connect to the API server from local machine and access to UI using `https://localhost:8080`
                > **Note:** Keep the `kubectl port-forwarding` terminal open to avoid disrupting access to the UI. Open a new terminal if you need CLI access.

            - Retrieve Password for UI access 
    - In UI:
        - Define a Project Name
        - Select Cluster=`https://kubernetes.default.svc`
        - Define Namespace=`default`
        - REPO URL: `<Github_repo_hosting_CD_Pipeline>`
        - Path:``./`` 

5. **Commit a new code change and test app deployment**
    - Check status in Jenkins UI of both Jobs: ```BuildAppJob``` for CI Pipeline and ```UpdateK8sManifestJob``` for CD Pipeline
    - Check status of pods: ``kubectl get pods``
    - Check status in Argo CD UI

    ![Argo CD](https://i.imgur.com/l1MlaPK.png)


    - Retrieve load balancer endpoint by running ``kubectl get svc``, then paste into web browser to access the application

## Clean-up
Delete AWS EKS Cluster
```bash
eksctl delete cluster --name demo-eks --region us-east-1
```
`Terminate` the running EC2 instance for Jenkins server in AWS Console Management


