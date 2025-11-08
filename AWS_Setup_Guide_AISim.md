# AWS Setup Guide for AISim Automated Ad System

**Quick Setup**: 10-15 minutes  
**Status**: AWS CLI Installed ✅  
**Next**: Get credentials and configure

---

## 🔑 Step 1: Get Your AWS Access Keys

### Option A: Using IAM User (Recommended for Development)

1. **Go to IAM Console**:
   - Click here: https://console.aws.amazon.com/iam/
   - Or in AWS Console: Search for "IAM" in the search bar

2. **Create a New User**:
   - Click **"Users"** in the left sidebar
   - Click **"Create user"** button
   - Username: `aisim-automation` (or your preferred name)
   - Click **"Next"**

3. **Set Permissions**:
   - Select **"Attach policies directly"**
   - Search and select these policies:
     - ✅ `AdministratorAccess` (for full access - development)
     - OR select specific policies:
       - `AmazonDynamoDBFullAccess`
       - `AmazonS3FullAccess`
       - `AWSLambda_FullAccess`
       - `CloudWatchFullAccess`
       - `AmazonBedrockFullAccess`
       - `ReadOnlyAccess` (for Cost Explorer)
   - Click **"Next"**
   - Click **"Create user"**

4. **Create Access Key**:
   - Click on the user you just created
   - Go to **"Security credentials"** tab
   - Scroll down to **"Access keys"**
   - Click **"Create access key"**
   - Choose use case: **"Command Line Interface (CLI)"**
   - Check the confirmation box
   - Click **"Next"**
   - Description (optional): "AISim Automation System"
   - Click **"Create access key"**

5. **SAVE YOUR CREDENTIALS**:
   ```
   Access Key ID: AKIA... (20 characters)
   Secret Access Key: .... (40 characters)
   ```
   
   **⚠️ IMPORTANT**: The secret key is only shown ONCE!
   - Click **"Download .csv file"** to save them
   - Or copy both values to a secure location

---

## ⚙️ Step 2: Configure AWS CLI

Once you have your credentials, run this command in terminal:

```bash
aws configure
```

You'll be prompted to enter:

```
AWS Access Key ID [None]: PASTE_YOUR_ACCESS_KEY_HERE
AWS Secret Access Key [None]: PASTE_YOUR_SECRET_KEY_HERE
Default region name [None]: us-east-1
Default output format [None]: json
```

**Recommended Region**: `us-east-1` (most services available)

---

## ✅ Step 3: Verify Configuration

Test your AWS connection:

```bash
# Check configuration
aws configure list

# Test connection
aws sts get-caller-identity

# List S3 buckets (if any)
aws s3 ls

# Check available regions
aws ec2 describe-regions --output table
```

If successful, you'll see your account information!

---

## 🚀 Step 4: Configure n8n with AWS

Your AWS credentials are now stored in `~/.aws/credentials`

n8n and AWS MCP servers will automatically use these credentials!

---

## 📋 Quick Links

| Task | Direct Link |
|------|-------------|
| AWS Console | https://console.aws.amazon.com/ |
| IAM Users | https://console.aws.amazon.com/iam/home#/users |
| Create Access Key | https://console.aws.amazon.com/iam/home#/security_credentials |
| Cost Explorer | https://console.aws.amazon.com/cost-management/home |
| DynamoDB | https://console.aws.amazon.com/dynamodb/ |
| Lambda | https://console.aws.amazon.com/lambda/ |
| S3 | https://console.aws.amazon.com/s3/ |
| Bedrock | https://console.aws.amazon.com/bedrock/ |

---

## 🎯 What You Can Do After Setup

### In Cursor (with AWS MCP):
```
"List all my S3 buckets"
"Create a DynamoDB table for ad campaigns"
"Show me my AWS costs for this month"
"What Lambda functions do I have?"
```

### In n8n (with AWS nodes):
- Connect to DynamoDB
- Store files in S3
- Invoke Lambda functions
- Query CloudWatch logs
- Use Bedrock AI
- Access Cost Explorer

---

## 🔒 Security Best Practices

### 1. **Use IAM Roles in Production**
For production, use IAM roles instead of access keys where possible.

### 2. **Enable MFA**
Add multi-factor authentication to your AWS account:
- Go to IAM → Users → Your user
- Security credentials tab
- Assign MFA device

### 3. **Rotate Keys Regularly**
Set a reminder to rotate access keys every 90 days.

### 4. **Use Least Privilege**
Only grant permissions you actually need.

### 5. **Enable CloudTrail**
Track all API calls for auditing:
- Go to CloudTrail
- Create trail
- Enable for all regions

---

## 🐛 Troubleshooting

### "Unable to locate credentials"
```bash
# Check if credentials file exists
cat ~/.aws/credentials

# Check configuration
aws configure list

# Reconfigure if needed
aws configure
```

### "Access Denied" errors
- Check IAM permissions
- Verify policies are attached
- Ensure keys are active (not deleted)

### "Region not available"
Some services aren't in all regions. Use:
- `us-east-1` (most services)
- `us-west-2` (alternative)

---

## 💡 Recommended Initial Setup

### Create These Resources:

#### 1. S3 Buckets
```bash
# For ad creatives
aws s3 mb s3://aisim-ad-creatives

# For data lake
aws s3 mb s3://aisim-data-lake

# For backups
aws s3 mb s3://aisim-backups
```

#### 2. DynamoDB Tables
```bash
# Campaign metrics
aws dynamodb create-table \
  --table-name aisim-campaign-metrics \
  --attribute-definitions AttributeName=campaignId,AttributeType=S \
  --key-schema AttributeName=campaignId,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST

# User sessions
aws dynamodb create-table \
  --table-name aisim-user-sessions \
  --attribute-definitions AttributeName=sessionId,AttributeType=S \
  --key-schema AttributeName=sessionId,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST
```

---

## 🎊 Next Steps

After AWS is configured:

1. ✅ **Test AWS MCP in Cursor**
   - Restart Cursor
   - Try: "List my AWS S3 buckets"

2. ✅ **Configure n8n AWS Nodes**
   - AWS credentials auto-detected
   - Add DynamoDB, S3, Lambda nodes
   - Build your first workflow

3. ✅ **Set Up Cost Monitoring**
   - Enable Cost Explorer
   - Create budget alerts
   - Set up cost anomaly detection

4. ✅ **Enable Bedrock**
   - Go to Bedrock console
   - Request model access
   - Enable Claude 3 models

---

**Ready to configure!** Let me know when you have your Access Key ID and Secret Access Key! 🚀








