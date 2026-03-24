## Dockerfile

You can **copy and paste it directly** into a file named `Dockerfile`.

```dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip install --no-cache-dir -e .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]

```

## Kubernetes Deployment Manifest (`manifests/deployment.yaml`)


```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: llmops-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: llmops-app
  template:
    metadata:
      labels:
        app: llmops-app
    spec:
      containers:
        - name: llmops-app
          image: dataguru97/seo-testing:v1
          ports:
            - containerPort: 8501
```

**Notes:**

* Update `replicas` to the number of pods you want to run (for example, `1`, `2`, or more).
* Replace `image: dataguru97/seo-testing:v1` with **your own Docker image name and tag**.

---

## Kubernetes Service Manifest (`manifests/service.yaml`)


```yaml
apiVersion: v1
kind: Service
metadata:
  name: llmops-service
spec:
  selector:
    app: llmops-app
  ports:
    - port: 80
      targetPort: 8501
  type: NodePort
```

## Jenkins Pipeline Structure (Jenkinsfile)


```groovy
pipeline {
    agent any

    stages {

        stage('Checkout Github') {
            steps {
                echo 'Checking out code from GitHub...'
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    echo 'Building Docker image...'
                }
            }
        }

        stage('Push Image to DockerHub') {
            steps {
                script {
                    echo 'Pushing Docker image to DockerHub...'
                }
            }
        }

        stage('Update Deployment YAML with New Tag') {
            steps {
                script {
                }
            }
        }

        stage('Commit Updated YAML') {
            steps {
                script {
                    withCredentials([
                        usernamePassword(
                            credentialsId: 'github-token',
                            usernameVariable: 'GIT_USER',
                            passwordVariable: 'GIT_PASS'
                        )
                    ]) {

                    }
                }
            }
        }

        stage('Install Kubectl & ArgoCD CLI Setup') {
            steps {
            }
        }

        stage('Apply Kubernetes & Sync App with ArgoCD') {
            steps {
                script {
                }
            }
        }

    }
}
```

## GCP Cloud Setup

---

### 1. Create a VM Instance on Google Cloud

1. Go to **Compute Engine → VM Instances**
2. Click **Create Instance**

**Basic Configuration**

* **Name:** `Whatever you want to name`
* **Machine Type:**

  * Series: **E2**
  * Preset: **Standard**
  * Memory: **16 GB RAM**
* **Boot Disk:**

  * Size: **256 GB**
  * Image: **Ubuntu 24.04 LTS**
* **Networking:**

  * Enable **HTTP** and **HTTPS** traffic and **Port Forwarding** turned on

Click **Create** to launch the instance.

---

### 2. Connect to the VM

* Use the **SSH** button in the Google Cloud Console to connect to the VM directly from the browser.

---

### 3. Configure the VM Instance

#### Clone the GitHub Repository

```bash
git clone https://github.com/data-guru0/TESTING-9.git ( Whatver your Github repo link )
ls
cd TESTING-9
ls
```

You should now see the project files inside the VM.

---

### 4. Install Docker

1. Open a browser and search for **“Install Docker on Ubuntu”**
2. Open the **official Docker documentation** (`docs.docker.com`)
3. Copy and paste the **first command block** into the VM terminal
4. Copy and paste the **second command block**
5. Test the Docker installation:

```bash
docker run hello-world
```

---

### 5. Run Docker Without `sudo`

From the same Docker documentation page, scroll to **Post-installation steps for Linux** and run **all four commands** one by one.

The last command is used to verify Docker works without `sudo`.

---

### 6. Enable Docker to Start on Boot

From the section **Configure Docker to start on boot**, run:

```bash
sudo systemctl enable docker.service
sudo systemctl enable containerd.service
```

---

### 7. Verify Docker Setup

```bash
systemctl status docker
docker ps
docker ps -a
```

Expected results:

* Docker service shows **active (running)**
* No running containers
* `hello-world` container appears in exited state

---

### 8. Configure Minikube Inside the VM

#### Install Minikube

1. Search for **Install Minikube**
2. Open the official website: `minikube.sigs.k8s.io`
3. Select:

   * **OS:** Linux
   * **Architecture:** x86
   * **Installation Type:** Binary

Copy and run the installation commands provided on the website.

---

#### Start the Minikube Cluster

```bash
minikube start
```

Minikube uses **Docker internally**, which is why Docker was installed first.

---


---

### 9. Verify Kubernetes & Minikube Setup

```bash
minikube status
minikubr kubectl get nodes
minikube kubectl cluster-info
docker ps
```

Expected results:

* All Minikube components are running
* A single `minikube` node is visible
* Kubernetes cluster information is accessible
* Minikube container is running in Docker

---

This completes the **GCP Cloud Setup**.

## Jenkins Setup

---

### 1. Run Jenkins in Docker (DIND Mode)

#### Check Existing Docker Networks

Ensure Jenkins runs on the **same Docker network as Minikube**.

```bash
docker network ls
```

---

#### Run Jenkins Container

```bash
docker run -d --name jenkins \
  -p 8080:8080 \
  -p 50000:50000 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v $(which docker):/usr/bin/docker \
  -u root \
  -e DOCKER_GID=$(getent group docker | cut -d: -f3) \
  --network minikube \
  jenkins/jenkins:lts
```

---

### 2. Verify Jenkins Container

```bash
docker ps
docker logs jenkins
```

* Jenkins container should be running
* Copy the **initial admin password** from the logs

---

### 3. Access Jenkins Web UI

1. Go to your **GCP VM dashboard**
2. Copy the **External IP**
3. Open the following URL in your browser:

```
http://<EXTERNAL_IP>:8080
```

---

### 4. Configure GCP Firewall (If Needed)

If Jenkins does not load, create a firewall rule:

* **Name:** `allow-jenkins`
* **Description:** Allow all traffic (for Jenkins demo)
* **Logs:** Off
* **Network:** default
* **Direction:** Ingress
* **Action:** Allow
* **Targets:** All instances
* **Source IP ranges:** `0.0.0.0/0`
* **Allowed protocols and ports:** All

---

### 5. Jenkins Initial Setup

1. Paste the **initial admin password**
2. Click **Install Suggested Plugins**
3. Create an **Admin User**
4. Skip the **agent security warning** (for now)

---

### 6. Install Required Jenkins Plugins

Navigate to:

**Manage Jenkins → Plugins**

Install the following plugins:

* Docker
* Docker Pipeline
* Kubernetes

Restart Jenkins after installation:

```bash
docker restart jenkins
```

Log in again once Jenkins restarts.

---


✅ **Jenkins is now fully set up and ready to use!**



## GitHub Integration

---

### GitHub Link with Local PC and VM

#### Generate GitHub Personal Access Token

1. Go to:
   **GitHub → Settings → Developer Settings → Personal access tokens**
2. Click **Generate new token**
3. Select **Classic Token**
4. Grant the following permissions:

* `admin:org`
* `admin:org_hook`
* `admin:public_key`
* `admin:repo_hook`
* `repo`
* `workflow`

Copy the generated token and **store it securely**. You will not be able to view it again. So keep that tab open!!

---

#### Configure Git on Local PC / VM

Set your Git identity (run on both local machine and VM if required):

```bash
git config --global user.email "gyrogodnon@gmail.com"   ## pass your email here
git config --global user.name "data-guru0"              ## pass your Github username here
```

---

#### Push Code Using GitHub Token

```bash
git add .
git commit -m "commit"
git push origin main
```

When prompted for credentials:

* **Username:** `data-guru0`
* **Password:** Paste the **GitHub Personal Access Token**
  *(Note: the token will not be visible while pasting)*

---

---

### GitHub Integration with Jenkins

#### Add GitHub Credentials to Jenkins

1. Go to:
   **Manage Jenkins → Credentials → Global → Add Credentials**
2. Fill in the details:

   * **Kind:** Username with password
   * **Username:** Your GitHub username
   * **Password:** GitHub Personal Access Token
   * **ID:** `github-token`
   * **Description:** `github-token`
3. Click **Save**

---

#### Create a New Jenkins Pipeline Job

1. Go to **Jenkins Dashboard → New Item**
2. Enter the job name: **`gitops`**  ## Whatver name you want to give
3. Select **Pipeline** and click **OK**
4. Scroll to the **Pipeline** section and configure:

   * **Definition:** Pipeline from SCM
   * **SCM:** Git
   * **Repository URL:** Your GitHub repository URL
   * **Credentials:** Select `github-token`
   * **Branch:** `main`

Save the job configuration.

#### Open Jenkins Pipeline Syntax 

1. Go to **checkout** drop down
2. Again give your repository url , branch name and token.
3. Generate the Syntax
4. Copy that Syntax.
5. Paste that in the Jenkinsfile in VS Code in the first stage **Checkout** stage
6. Push code to Github.

---

#### Final Jenkins Test

1. Go back to the **Jenkins Dashboard**
2. Open the **gitops** pipeline
3. Click **Build Now**

If the build completes successfully ✅, **GitHub is now fully integrated with Jenkins**.

---


## Build and Push Docker Image to DockerHub

---

### Configure Docker Tool in Jenkins

1. Go to **Jenkins Dashboard → Manage Jenkins → Tools**
2. Scroll down to **Docker Installations**
3. Click **Add Docker**
4. Configure the tool:

   * **Name:** `Docker`
   * ✅ **Install automatically**
   * **Install from:** `docker.com`
5. Click **Apply** and **Save**

---

### Sync Code b/w Local PC and VM ( good practice optional here )

```bash
git pull origin main
```

---

### Create DockerHub Repository

1. Go to **[https://hub.docker.com](https://hub.docker.com)**
2. Create a new repository
   Example: `dataguru97/testing-9`

---

### Generate DockerHub Access Token

1. Go to **DockerHub → Account Settings → Security**
2. Click **New Access Token**
3. Provide:

   * A meaningful **name**
   * **Read/Write** permission
4. Copy and securely store the generated token ( Keep this tab open )

---

### Add DockerHub Credentials to Jenkins

1. Go to **Jenkins → Manage Jenkins → Credentials → Global → Add Credentials**
2. Fill in the details:

   * **Kind:** Username with password
   * **Username:** DockerHub username (e.g., `dataguru97`)
   * **Password:** DockerHub access token
   * **ID:** `dockerhub-token`
   * **Description:** `DockerHub Access Token`
3. Click **Save**

---

### Update Jenkinsfile in VS Code

1. Add an **environment block** at the top of the Jenkins pipeline and paste the following there:
```bash
environment {
        DOCKER_HUB_REPO = "dataguru97/seo-testing"    
        DOCKER_HUB_CREDENTIALS_ID = "dockerhub-token"
        IMAGE_TAG = "v${BUILD_NUMBER}"
    }
```
- **DOCKER_HUB_REPO** --> Your DockerHub repo name
- **DOCKER_HUB_CREDENTIALS_ID** --> ID name of your Jenkins credentials
- **Keep image tag as it is**  --> It will help us in creating different versions of our applications each time it is runned.


2. Update the following stages:

   * **Build Docker Image**

```bash
dockerImage = docker.build("${DOCKER_HUB_REPO}:${IMAGE_TAG}")
```

   * **Push Image to DockerHub**

```bash
docker.withRegistry('https://registry.hub.docker.com' , "${DOCKER_HUB_CREDENTIALS_ID}") {
                        dockerImage.push("${IMAGE_TAG}")
```
* **Update Deployment YAML with New Tag**
```bash
sh """
    sed -i 's|image: dataguru97/seo-testing:.*|image: dataguru97/seo-testing:${IMAGE_TAG}|' manifests/deployment.yaml
    """
```
* **Commit Updated YAML**
```bash
sh '''
    git config user.name "data-guru0"
    git config user.email "gyrogodnon@gmail.com"
    git add manifests/deployment.yaml
    git commit -m "Update image tag to ${IMAGE_TAG}" || echo "No changes to commit"
    git push https://${GIT_USER}:${GIT_PASS}@github.com/data-guru0/YT-SEO-Gen-Testing.git HEAD:main
    '''
```
- Here Your Github user name and emil should be used
- Also **@github.com/data-guru0/YT-SEO-Gen-Testing.git** Change this with your repo name.
---

### Push Changes to GitHub

```bash
git add .
git commit -m "Add Docker build and push stages"
git push origin main
```

---

### Trigger Jenkins Pipeline

1. Go to **Jenkins Dashboard**
2. Open your pipeline job (**gitops**)
3. Click **Build Now**

---

### Verification

If the pipeline succeeds ✅, your Docker image will be available on DockerHub repo and also see the updated YAML file on Github ( Do check that out )

---


## ArgoCD Setup

---

### Step 1: Check Existing Kubernetes Namespaces

```bash
kubectl get namespace
```

---

### Step 2: Create a Namespace for ArgoCD

```bash
kubectl create ns argocd
kubectl get namespace
```

Verify that the `argocd` namespace is created successfully.

---

### Step 3: Install ArgoCD

Apply the official ArgoCD installation manifest:

```bash
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

---

### Step 4: Validate ArgoCD Components

```bash
kubectl get all -n argocd
```

✅ Proceed only when all resources are in **Running** or **Completed** state.
⛔ Do not continue if any pod is in `Pending` or `CrashLoopBackOff`.

---

### Step 5: Check ArgoCD Service Type

```bash
kubectl get svc -n argocd
```

By default, `argocd-server` is of type **ClusterIP**, which is not accessible externally.

---

### Step 6: Change ArgoCD Service to NodePort

Edit the service:

```bash
kubectl edit svc argocd-server -n argocd
```

* Find:

  ```yaml
  type: ClusterIP
  ```
* Replace with:

  ```yaml
  type: NodePort
  ```
Go to insert mode by pressing i key
Save and exit (`:wq!` in Vim).

Verify again:

```bash
kubectl get svc -n argocd
```

You should now see a **NodePort** (e.g., `31704`).

---

### Step 7: Access ArgoCD UI

Run port-forwarding:

```bash
kubectl port-forward --address 0.0.0.0 service/argocd-server 31704:80 -n argocd
```

Open your browser:

```
http://<VM_PUBLIC_IP>:31704
```

You will reach the ArgoCD login page.
Open another terminal now ...

---

### Step 8: Get ArgoCD Admin Password

```bash
kubectl get secret -n argocd argocd-initial-admin-secret \
-o jsonpath="{.data.password}" | base64 -d
```

* **Username:** `admin`
* **Password:** Output from the command above

Log in to the ArgoCD UI 🎉

---


### Step 9: Locate Kubernetes Config File

```bash
cd ~
ls -la
ls -la .kube/
cat .kube/config
```

Copy the entire content of `.kube/config` for backup and editing.

---

### Step 10: Convert Certificate Files to Base64

Run the following commands one by one:

```bash
cat /home/gyrogodnon/.minikube/ca.crt | base64 -w 0; echo
cat /home/gyrogodnon/.minikube/profiles/minikube/client.crt | base64 -w 0; echo
cat /home/gyrogodnon/.minikube/profiles/minikube/client.key | base64 -w 0; echo
```


Change **gyrogodnon** with your own VM name
Replace:

* `certificate-authority-data`
* `client-certificate-data`
* `client-key-data`

inside your kubeconfig file with these Base64 values.
Do this all on NotePad
After done Copy all content at once..

---

### Step 11: Save Edited kubeconfig File

- Open GiT Bash 

```bash
cd ~/Downloads
vi config
```

Paste the edited kubeconfig content and save:

```text
Esc → :wq! → Enter
```

---

### Step 12: Add kubeconfig as Jenkins Secret

1. Go to **Jenkins Dashboard → Manage Jenkins → Credentials**
2. Select **Global → Add Credentials**
3. Configure:

   * **Kind:** Secret file
   * **File:** Upload edited kubeconfig
   * **ID:** `kubeconfig`
   * **Description:** `kubeconfig`
4. Click **Save**

---
---

## Jenkins ↔ ArgoCD Automation

### Step 13: Install kubectl & ArgoCD CLI in Jenkins Container

Inside your Jenkinsfile, use the provided installation snippet to install:

* `kubectl`
* `argocd` CLI in **Install Kubectl & ArgoCD CLI Setup** stage

 ```bash
     sh '''
        echo 'installing Kubectl & ArgoCD cli...'
        curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
        chmod +x kubectl
        mv kubectl /usr/local/bin/kubectl
        curl -sSL -o /usr/local/bin/argocd https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64
        chmod +x /usr/local/bin/argocd
        '''
```

---

### Step 14: Connect GitHub Repository to ArgoCD

In ArgoCD UI:

* Go to **Settings → Repositories**
* Click **Connect Repo (HTTPS)**

Fill in:

* **Type:** git
* **Project:** default
* **Repo URL:** `https://github.com/data-guru0/GitOPS-testing.git`  ( Your Github repo URL)
* **Username & Token:** (recommended)  username and token you generated in Github

You should see a success message.

---

### Step 15: Create ArgoCD Application

In ArgoCD UI:

* Go to **Applications → New App**

Fill in:

* **Name:** `gitopsapp` (or any name)
* **Project:** default
* **Sync Policy:** Automatic
* Enable **Self Heal** and **Sync Pipeline Resources**
* **Repository:** Select connected repo
* **Revision:** `main`
* **Path:** `manifests`
* **Cluster URL:** Select cluster
* **Namespace:** `argocd`

Click **Create**

You should see **Synced** and **Healthy** status.

---

### Step 16: Login to ArgoCD from Jenkins Pipeline ( Apply Kubernetes & Sync App with ArgoCD ) stage

Inside the pipeline stage **Apply Kubernetes & Sync App with ArgoCD**

```bash

        kubeconfig(credentialsId: 'kubeconfig', serverUrl: 'https://192.168.49.2:8443') {
            sh '''
                argocd login 34.31.74.198:31704 --username admin --password $(kubectl get secret -n argocd argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d) --insecure

                argocd app sync ytseo
                     '''
         }
```
- Replace **https://192.168.49.2:8443** with Cluster IP
- To get clutster IP:

### Get the Clutser Info in VM


     ```bash
     kubectl cluster-info
     ```

     (example: `https://192.168.49.2:8443`)


- Replace `34.31.74.198:31704` with your VM’s IP and ArgoCd Port where argocd is running basically ( Copy URl with Port )
- Replace `ytseo` with your application name in argoCD.

- Push changes to GitHub and trigger the Jenkins pipeline.

---


### Step 17: Verify Deployment

```bash
kubectl get deploy -n argocd
kubectl get pods -n argocd
```

Ensure all pods are running.

---

### Step 18 : Enable External Access to view the app

```bash
kubectl port-forward svc/my-service -n argocd \
--address 0.0.0.0 9090:80
```

Change **my-service** to whatver name is written in your service.yaml
---

### Step 19: Access Application in Browser

```
http://<VM_EXTERNAL_IP>:9090
```

🎉 Your application is now live and fully managed using **GitOps with ArgoCD + Jenkins**.

---

## Webhooks Setup and Complete Automation

This section enables **fully automated CI/CD** by triggering the Jenkins pipeline **automatically on every GitHub push** using webhooks.

---

### Step 1: Add Webhook in GitHub Repository

1. Go to your **GitHub Repository → Settings → Webhooks**
2. Click **Add webhook**
3. Fill in the details:

* **Payload URL:**

  ```
  http://<JENKINS_PUBLIC_IP>:8080/github-webhook/
  ```

  Replace `<JENKINS_PUBLIC_IP>` with your Jenkins VM public IP.
  * example :http://34.72.5.170:8080/github-webhook/

* **Content type:** `application/json`

* **Secret:** Leave blank

* **SSL verification:** Enable only if Jenkins is using HTTPS

4. Under **Which events would you like to trigger this webhook?**

   * Select **Just the push event**

5. Click **Add webhook**

This ensures the pipeline triggers on **every push to the repository**.

---

### Step 2: Configure Jenkins to Receive Webhook

1. Open **Jenkins Dashboard**
2. Go to your **Pipeline Job**
3. Click **Configure**
4. Scroll to **Build Triggers**
5. Enable:

   * ✅ **GitHub hook trigger for GITScm polling**
6. Click **Apply** and **Save**

Your Jenkins job is now ready to receive webhook events.

---

### Step 3: Test Webhook Automation

1. Open **VS Code**
2. Make a small change in the `Jenkinsfile`
   (for example, add or modify an `echo` statement)
3. Commit and push the changes:

```bash
git add .
git commit -m "Test webhook trigger"
git push origin main
```

4. Go to the **Jenkins Dashboard**

✅ You should see the pipeline **automatically triggered** without clicking **Build Now**.

---

🎉 **Automation Complete!**
Your GitHub → Jenkins → Docker → Kubernetes → ArgoCD pipeline is now **fully automated using webhooks**.






