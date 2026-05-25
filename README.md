# AWS Cloud-Based Music Subscription Application

## Overview

This project is a cloud-based music subscription application developed using Amazon Web Services (AWS). The application allows users to register, log in, search for music, subscribe to songs, remove subscriptions, and view subscribed music through a web interface.

The project demonstrates three backend deployment architectures:
- EC2-based backend
- ECS container-based backend
- API Gateway with AWS Lambda backend

The frontend is hosted using Amazon S3 static website hosting.

---

## AWS Services Used

- Amazon S3
- Amazon DynamoDB
- Amazon EC2
- Amazon ECS
- Amazon ECR
- AWS Lambda
- Amazon API Gateway
- IAM Roles
- Auto Scaling Group

---

## Project Structure

```text
aws-music-assignment/
│
├── backend/
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/
│   ├── login.html
│   ├── register.html
│   ├── main.html
│   ├── app.js
│   └── style.css
│
├── lambda/
│   ├── lambda_login.py
│   ├── lambda_register.py
│   ├── lambda_query_music.py
│   ├── lambda_subscribe.py
│   ├── lambda_get_subscriptions.py
│   └── lambda_remove_subscription.py
│
├── scripts/
│   ├── 01_load_login.py
│   ├── 02_load_music.py
│   └── 03_upload_images_s3.py
│
└── 2026a2_songs.json
```

---

## Application Features

- User registration
- User login
- Music search
- Music subscription
- Remove subscription
- View subscribed songs
- Artist image display using pre-signed URLs

---

# Setup Instructions

## 1. Configure AWS CLI

Configure AWS CLI using AWS Academy Learner Lab credentials.

```bash
aws configure
```

Set the correct AWS region:

```text
us-east-1
```

---

# DynamoDB and S3 Setup

## 2. Create DynamoDB Tables

Create the following DynamoDB tables:

```text
login
music
subscriptions
```

---

## 3. Load Login Data

```bash
python scripts/01_load_login.py
```

---

## 4. Load Music Dataset

```bash
python scripts/02_load_music.py
```

---

## 5. Upload Artist Images to S3

```bash
python scripts/03_upload_images_s3.py
```

This script downloads artist images and uploads them into the private S3 image bucket.

---

# Frontend Deployment

## 6. Update Backend API Endpoint

In `frontend/app.js`, update:

```javascript
const API_BASE = "YOUR_BACKEND_URL";
```

Examples:

### EC2 Backend

```javascript
const API_BASE = "http://EC2_PUBLIC_IP";
```

### ECS Backend

```javascript
const API_BASE = "http://ECS_PUBLIC_IP";
```

### API Gateway + Lambda Backend

```javascript
const API_BASE = "https://API_GATEWAY_URL/prod";
```

---

## 7. Upload Frontend to S3

Upload these files to the frontend S3 bucket:

```text
login.html
register.html
main.html
app.js
style.css
```

Enable static website hosting and configure:

```text
Index document: login.html
```

---

# EC2 Backend Deployment

## 8. Install Required Packages on EC2

```bash
sudo dnf update -y
sudo dnf install python3 python3-pip git -y
pip3 install flask flask-cors boto3 gunicorn
```

---

## 9. Run Flask Backend on EC2

Go to backend folder:

```bash
cd backend
```

Run backend using Gunicorn:

```bash
python3 -m gunicorn -w 2 --timeout 120 -b 0.0.0.0:80 app:app
```

Test backend:

```text
http://EC2_PUBLIC_IP/login
```

Expected response:

```text
405 Method Not Allowed
```

This is expected because `/login` only supports POST requests.

---

# ECS Backend Deployment

## 10. Install Docker on EC2

```bash
sudo dnf install -y dnf-plugins-core
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo dnf install docker-ce docker-ce-cli containerd.io -y
sudo systemctl enable docker
sudo systemctl start docker
```

Test Docker:

```bash
sudo docker run hello-world
```

---

## 11. Build Docker Image

```bash
cd backend
sudo docker build --network=host -t music-backend .
```

---

## 12. Test Docker Container Locally

```bash
sudo docker run -d -p 80:80 --name music-backend-container music-backend
```

Test:

```text
http://EC2_PUBLIC_IP/login
```

---

## 13. Push Docker Image to Amazon ECR

Login to ECR:

```bash
aws ecr get-login-password --region us-east-1 | sudo docker login --username AWS --password-stdin ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com
```

Tag image:

```bash
sudo docker tag music-backend:latest ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/music-backend:latest
```

Push image:

```bash
sudo docker push ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/music-backend:latest
```

---

## 14. Deploy ECS Backend

Create:
- ECS Cluster
- ECS Task Definition
- ECS Service

Use:
- Task role: `LabRole`
- Task execution role: `LabRole`
- Network mode: `default`
- Container port: `80`
- Host port: `80`

---

# Lambda + API Gateway Deployment

## 15. Lambda Function Files

The following Python files are included in the `lambda/` directory:

```text
lambda_login.py
lambda_register.py
lambda_query_music.py
lambda_subscribe.py
lambda_get_subscriptions.py
lambda_remove_subscription.py
```

---

## 16. Create Lambda Functions

Create the following Lambda functions:

| Lambda Function | Python File |
|---|---|
| music-login | lambda_login.py |
| music-register | lambda_register.py |
| music-query | lambda_query_music.py |
| music-subscribe | lambda_subscribe.py |
| music-get-subscriptions | lambda_get_subscriptions.py |
| music-remove-subscription | lambda_remove_subscription.py |

Configuration:

```text
Runtime: Python 3.12
Architecture: x86_64
```

---

## 17. Deploy Lambda Code

For each Lambda function:

1. Open AWS Lambda Console
2. Create a new function
3. Select:
   - Author from scratch
   - Python 3.12 runtime
   - LabRole execution role
4. Copy corresponding Python file content into:

```text
lambda_function.py
```

5. Click:

```text
Deploy
```

---

## 18. Configure API Gateway

Create REST API routes:

| Method | Route | Lambda Function |
|---|---|---|
| POST | /login | music-login |
| POST | /register | music-register |
| GET | /music/query | music-query |
| POST | /subscriptions | music-subscribe |
| GET | /subscriptions/{email} | music-get-subscriptions |
| DELETE | /subscriptions/{email}/{song_id} | music-remove-subscription |

Enable CORS and deploy API to:

```text
prod
```

---

# Main REST API Endpoints

```text
POST   /login
POST   /register
GET    /music/query
POST   /subscriptions
GET    /subscriptions/{email}
DELETE /subscriptions/{email}/{song_id}
```

---

# Notes

- Frontend bucket is public for static website hosting.
- Artist image bucket is private.
- Images are accessed using pre-signed URLs.
- DynamoDB stores image keys instead of actual images.
- LabRole is used for AWS service permissions.
- API Gateway and Lambda may take time to initialize in AWS Academy Learner Lab.

- Group Member

AWS Cloud System Development Assignment
