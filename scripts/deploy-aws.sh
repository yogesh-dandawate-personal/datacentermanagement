#!/bin/bash

# AWS ECS Deployment Script for iNetZero

set -e

echo "🚀 AWS ECS Deployment Script"
echo "=============================="
echo ""

# Configuration
AWS_REGION=${AWS_REGION:-"us-east-1"}
AWS_ACCOUNT_ID=${AWS_ACCOUNT_ID:-""}
ECR_REPO_FRONTEND="inetze ro-frontend"
ECR_REPO_BACKEND="inetze ro-backend"
IMAGE_TAG="latest"

# Verify AWS CLI
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Please install it:"
    echo "   brew install awscli"
    exit 1
fi

# Get AWS Account ID if not provided
if [ -z "$AWS_ACCOUNT_ID" ]; then
    echo "Getting AWS Account ID..."
    AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    echo "✅ Account ID: $AWS_ACCOUNT_ID"
fi

ECR_REGISTRY="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"

echo ""
echo "📋 Configuration:"
echo "  Region: $AWS_REGION"
echo "  Account: $AWS_ACCOUNT_ID"
echo "  Registry: $ECR_REGISTRY"
echo ""

# Step 1: Create ECR Repositories
echo "Step 1: Creating ECR Repositories..."
for repo in $ECR_REPO_FRONTEND $ECR_REPO_BACKEND; do
    if aws ecr describe-repositories --repository-names $repo --region $AWS_REGION 2>/dev/null | grep -q $repo; then
        echo "  ✅ Repository '$repo' already exists"
    else
        echo "  📝 Creating repository '$repo'..."
        aws ecr create-repository --repository-name $repo --region $AWS_REGION
        echo "  ✅ Created"
    fi
done

# Step 2: Login to ECR
echo ""
echo "Step 2: Logging in to ECR..."
aws ecr get-login-password --region $AWS_REGION | \
    docker login --username AWS --password-stdin $ECR_REGISTRY
echo "✅ Logged in"

# Step 3: Build and Push Frontend
echo ""
echo "Step 3: Building and pushing Frontend..."
echo "  Building Docker image..."
docker build -t $ECR_REPO_FRONTEND:$IMAGE_TAG ./frontend

echo "  Tagging image..."
docker tag $ECR_REPO_FRONTEND:$IMAGE_TAG \
    $ECR_REGISTRY/$ECR_REPO_FRONTEND:$IMAGE_TAG

echo "  Pushing to ECR..."
docker push $ECR_REGISTRY/$ECR_REPO_FRONTEND:$IMAGE_TAG
echo "✅ Frontend pushed"

# Step 4: Build and Push Backend
echo ""
echo "Step 4: Building and pushing Backend..."
echo "  Building Docker image..."
docker build -t $ECR_REPO_BACKEND:$IMAGE_TAG ./backend

echo "  Tagging image..."
docker tag $ECR_REPO_BACKEND:$IMAGE_TAG \
    $ECR_REGISTRY/$ECR_REPO_BACKEND:$IMAGE_TAG

echo "  Pushing to ECR..."
docker push $ECR_REGISTRY/$ECR_REPO_BACKEND:$IMAGE_TAG
echo "✅ Backend pushed"

# Step 5: Summary
echo ""
echo "=============================="
echo "✅ Deployment Complete!"
echo "=============================="
echo ""
echo "📋 ECR Images:"
echo "  Frontend: $ECR_REGISTRY/$ECR_REPO_FRONTEND:$IMAGE_TAG"
echo "  Backend:  $ECR_REGISTRY/$ECR_REPO_BACKEND:$IMAGE_TAG"
echo ""
echo "📚 Next Steps:"
echo "  1. Create ECS cluster: aws ecs create-cluster --cluster-name inetze ro-cluster"
echo "  2. Create task definitions (use AWS console or CloudFormation)"
echo "  3. Create services and load balancers"
echo "  4. Configure auto-scaling"
echo ""
echo "📖 Docs: https://docs.aws.amazon.com/ecs"
echo ""
