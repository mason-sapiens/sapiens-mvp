#!/bin/bash
# AWS Setup Script for Sapiens MVP
# This script sets up AWS infrastructure using AWS CLI

set -e

echo "🚀 Sapiens MVP - AWS Setup"
echo "================================"

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed"
    echo "Install it: https://aws.amazon.com/cli/"
    exit 1
fi

# Check if user is logged in
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ Not logged into AWS CLI"
    echo "Run: aws configure"
    exit 1
fi

echo "✅ AWS CLI configured"

# Configuration
# Auto-detect region from AWS CLI config, or use us-west-1 as default
DETECTED_REGION=$(aws configure get region 2>/dev/null || echo "us-west-1")
REGION=${AWS_REGION:-$DETECTED_REGION}
APP_NAME="sapiens-mvp"
DB_NAME="sapiens"
DB_USERNAME="sapiens"
DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
VPC_CIDR="10.0.0.0/16"

# PostgreSQL version (can be overridden with POSTGRES_VERSION env var)
# If not specified, will use latest available version
POSTGRES_VERSION=${POSTGRES_VERSION:-}

echo ""
echo "Configuration:"
echo "  Region: $REGION"
echo "  App Name: $APP_NAME"
echo "  DB Name: $DB_NAME"
if [ -n "$POSTGRES_VERSION" ]; then
    echo "  PostgreSQL Version: $POSTGRES_VERSION (specified)"
else
    echo "  PostgreSQL Version: auto-detect latest"
fi
echo ""
echo "ℹ️  Using region: $REGION"
echo "   (To use different region: export AWS_REGION=your-region)"
echo "   (To use specific PostgreSQL version: export POSTGRES_VERSION=15.4)"
echo ""

# Get available availability zones for this region
echo "🔍 Detecting availability zones..."
AZ_LIST=$(aws ec2 describe-availability-zones \
    --region $REGION \
    --filters "Name=state,Values=available" \
    --query 'AvailabilityZones[].ZoneName' \
    --output text)

# Get first two AZs
AZ1=$(echo $AZ_LIST | awk '{print $1}')
AZ2=$(echo $AZ_LIST | awk '{print $2}')

if [ -z "$AZ1" ] || [ -z "$AZ2" ]; then
    echo "❌ Could not find 2 availability zones in $REGION"
    exit 1
fi

echo "  Using AZs: $AZ1, $AZ2"
echo ""

# Create VPC
echo "📡 Creating VPC..."
VPC_ID=$(aws ec2 create-vpc \
    --cidr-block $VPC_CIDR \
    --region $REGION \
    --tag-specifications "ResourceType=vpc,Tags=[{Key=Name,Value=$APP_NAME-vpc}]" \
    --query 'Vpc.VpcId' \
    --output text)
echo "  VPC ID: $VPC_ID"

# Enable DNS
aws ec2 modify-vpc-attribute --vpc-id $VPC_ID --enable-dns-support --region $REGION
aws ec2 modify-vpc-attribute --vpc-id $VPC_ID --enable-dns-hostnames --region $REGION

# Create Internet Gateway
echo "🌐 Creating Internet Gateway..."
IGW_ID=$(aws ec2 create-internet-gateway \
    --region $REGION \
    --tag-specifications "ResourceType=internet-gateway,Tags=[{Key=Name,Value=$APP_NAME-igw}]" \
    --query 'InternetGateway.InternetGatewayId' \
    --output text)
aws ec2 attach-internet-gateway --vpc-id $VPC_ID --internet-gateway-id $IGW_ID --region $REGION
echo "  IGW ID: $IGW_ID"

# Create Subnets (2 public, 2 private for HA)
echo "🔌 Creating Subnets..."

# Public Subnet 1
PUBLIC_SUBNET_1=$(aws ec2 create-subnet \
    --vpc-id $VPC_ID \
    --cidr-block 10.0.1.0/24 \
    --availability-zone $AZ1 \
    --region $REGION \
    --tag-specifications "ResourceType=subnet,Tags=[{Key=Name,Value=$APP_NAME-public-1}]" \
    --query 'Subnet.SubnetId' \
    --output text)
echo "  Public Subnet 1: $PUBLIC_SUBNET_1 (AZ: $AZ1)"

# Public Subnet 2
PUBLIC_SUBNET_2=$(aws ec2 create-subnet \
    --vpc-id $VPC_ID \
    --cidr-block 10.0.2.0/24 \
    --availability-zone $AZ2 \
    --region $REGION \
    --tag-specifications "ResourceType=subnet,Tags=[{Key=Name,Value=$APP_NAME-public-2}]" \
    --query 'Subnet.SubnetId' \
    --output text)
echo "  Public Subnet 2: $PUBLIC_SUBNET_2 (AZ: $AZ2)"

# Private Subnet 1 (for RDS)
PRIVATE_SUBNET_1=$(aws ec2 create-subnet \
    --vpc-id $VPC_ID \
    --cidr-block 10.0.11.0/24 \
    --availability-zone $AZ1 \
    --region $REGION \
    --tag-specifications "ResourceType=subnet,Tags=[{Key=Name,Value=$APP_NAME-private-1}]" \
    --query 'Subnet.SubnetId' \
    --output text)
echo "  Private Subnet 1: $PRIVATE_SUBNET_1 (AZ: $AZ1)"

# Private Subnet 2 (for RDS)
PRIVATE_SUBNET_2=$(aws ec2 create-subnet \
    --vpc-id $VPC_ID \
    --cidr-block 10.0.12.0/24 \
    --availability-zone $AZ2 \
    --region $REGION \
    --tag-specifications "ResourceType=subnet,Tags=[{Key=Name,Value=$APP_NAME-private-2}]" \
    --query 'Subnet.SubnetId' \
    --output text)
echo "  Private Subnet 2: $PRIVATE_SUBNET_2 (AZ: $AZ2)"

# Create Route Table
echo "🛣️  Creating Route Table..."
ROUTE_TABLE_ID=$(aws ec2 create-route-table \
    --vpc-id $VPC_ID \
    --region $REGION \
    --tag-specifications "ResourceType=route-table,Tags=[{Key=Name,Value=$APP_NAME-rt}]" \
    --query 'RouteTable.RouteTableId' \
    --output text)

# Add route to Internet Gateway
aws ec2 create-route \
    --route-table-id $ROUTE_TABLE_ID \
    --destination-cidr-block 0.0.0.0/0 \
    --gateway-id $IGW_ID \
    --region $REGION

# Associate route table with public subnets
aws ec2 associate-route-table --subnet-id $PUBLIC_SUBNET_1 --route-table-id $ROUTE_TABLE_ID --region $REGION
aws ec2 associate-route-table --subnet-id $PUBLIC_SUBNET_2 --route-table-id $ROUTE_TABLE_ID --region $REGION
echo "  Route Table ID: $ROUTE_TABLE_ID"

# Create Security Group for EC2
echo "🔒 Creating Security Groups..."
EC2_SG_ID=$(aws ec2 create-security-group \
    --group-name $APP_NAME-ec2-sg \
    --description "Security group for $APP_NAME EC2 instances" \
    --vpc-id $VPC_ID \
    --region $REGION \
    --query 'GroupId' \
    --output text)

# Allow HTTP, HTTPS, SSH
aws ec2 authorize-security-group-ingress --group-id $EC2_SG_ID --protocol tcp --port 80 --cidr 0.0.0.0/0 --region $REGION
aws ec2 authorize-security-group-ingress --group-id $EC2_SG_ID --protocol tcp --port 443 --cidr 0.0.0.0/0 --region $REGION
aws ec2 authorize-security-group-ingress --group-id $EC2_SG_ID --protocol tcp --port 22 --cidr 0.0.0.0/0 --region $REGION
aws ec2 authorize-security-group-ingress --group-id $EC2_SG_ID --protocol tcp --port 8000 --cidr 0.0.0.0/0 --region $REGION
echo "  EC2 Security Group: $EC2_SG_ID"

# Create Security Group for RDS
RDS_SG_ID=$(aws ec2 create-security-group \
    --group-name $APP_NAME-rds-sg \
    --description "Security group for $APP_NAME RDS" \
    --vpc-id $VPC_ID \
    --region $REGION \
    --query 'GroupId' \
    --output text)

# Allow PostgreSQL from EC2 security group
aws ec2 authorize-security-group-ingress \
    --group-id $RDS_SG_ID \
    --protocol tcp \
    --port 5432 \
    --source-group $EC2_SG_ID \
    --region $REGION
echo "  RDS Security Group: $RDS_SG_ID"

# Create DB Subnet Group
echo "🗄️  Creating DB Subnet Group..."
aws rds create-db-subnet-group \
    --db-subnet-group-name $APP_NAME-db-subnet \
    --db-subnet-group-description "Subnet group for $APP_NAME database" \
    --subnet-ids $PRIVATE_SUBNET_1 $PRIVATE_SUBNET_2 \
    --region $REGION

# Auto-detect latest PostgreSQL version if not specified
if [ -z "$POSTGRES_VERSION" ]; then
    echo "🔍 Detecting latest PostgreSQL version..."
    POSTGRES_VERSION=$(aws rds describe-db-engine-versions \
        --engine postgres \
        --query 'DBEngineVersions[?Status==`available`] | [-1].EngineVersion' \
        --output text \
        --region $REGION)

    if [ -z "$POSTGRES_VERSION" ]; then
        echo "⚠️  Could not detect latest version, using 15 (major version)"
        POSTGRES_VERSION="15"
    fi

    echo "  Selected PostgreSQL version: $POSTGRES_VERSION"
fi

# Create RDS PostgreSQL Instance
echo "💾 Creating RDS PostgreSQL Instance..."
echo "  PostgreSQL version: $POSTGRES_VERSION"
echo "  Instance class: db.t3.micro"
echo "  Storage: 20 GB gp3"
echo "  This may take 10-15 minutes..."
echo ""

aws rds create-db-instance \
    --db-instance-identifier $APP_NAME-db \
    --db-instance-class db.t3.micro \
    --engine postgres \
    --engine-version $POSTGRES_VERSION \
    --master-username $DB_USERNAME \
    --master-user-password "$DB_PASSWORD" \
    --allocated-storage 20 \
    --storage-type gp3 \
    --db-name $DB_NAME \
    --vpc-security-group-ids $RDS_SG_ID \
    --db-subnet-group-name $APP_NAME-db-subnet \
    --backup-retention-period 7 \
    --no-publicly-accessible \
    --region $REGION

echo "  Waiting for database to be available..."
aws rds wait db-instance-available --db-instance-identifier $APP_NAME-db --region $REGION

# Get RDS Endpoint
DB_ENDPOINT=$(aws rds describe-db-instances \
    --db-instance-identifier $APP_NAME-db \
    --region $REGION \
    --query 'DBInstances[0].Endpoint.Address' \
    --output text)

echo "✅ Database created!"
echo "  Endpoint: $DB_ENDPOINT"

# Save configuration
echo ""
echo "💾 Saving configuration..."
cat > aws_config.txt << EOF
# AWS Configuration for Sapiens MVP
Region: $REGION
VPC ID: $VPC_ID
Public Subnet 1: $PUBLIC_SUBNET_1
Public Subnet 2: $PUBLIC_SUBNET_2
Private Subnet 1: $PRIVATE_SUBNET_1
Private Subnet 2: $PRIVATE_SUBNET_2
EC2 Security Group: $EC2_SG_ID
RDS Security Group: $RDS_SG_ID
RDS Endpoint: $DB_ENDPOINT
PostgreSQL Version: $POSTGRES_VERSION
Database Name: $DB_NAME
Database Username: $DB_USERNAME
Database Password: $DB_PASSWORD

DATABASE_URL: postgresql://$DB_USERNAME:$DB_PASSWORD@$DB_ENDPOINT:5432/$DB_NAME
EOF

echo "✅ Configuration saved to aws_config.txt"
echo ""
echo "⚠️  IMPORTANT: Save the database password securely!"
echo ""
echo "📋 Next Steps:"
echo "1. Launch EC2 instance in public subnet"
echo "2. Set DATABASE_URL environment variable"
echo "3. Deploy application"
echo ""
echo "Database URL (add to .env):"
echo "DATABASE_URL=postgresql://$DB_USERNAME:$DB_PASSWORD@$DB_ENDPOINT:5432/$DB_NAME"
