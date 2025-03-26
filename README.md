# AI-Driven Container Anomaly Detection

This project implements an AI-driven monitoring system to detect container performance anomalies using AWS SageMaker, Splunk, and Dynatrace.

## Project Overview

The system automatically collects container metrics from Splunk, trains an AI model using AWS SageMaker to predict anomalies, and automates anomaly alerts and scaling events using AWS Lambda. The entire process runs automatically every 5 minutes without manual intervention.

## Architecture

- **Data Collection**: Container metrics are collected using Splunk
- **AI Model**: Anomaly detection model trained using AWS SageMaker
- **Automation**: AWS Lambda functions for alerting and scaling
- **Monitoring**: Dynatrace integration for additional metrics
- **Security**: HashiCorp Vault for secure credential management
- **Configuration**: YAML-based configuration with Vault integration
- **Logging**: Structured logging with metrics collection
- **Scheduling**: AWS EventBridge for automated execution

## Project Structure

```
.
├── src/
│   ├── data_collection/     # Splunk data collection scripts
│   │   └── splunk_collector.py  # Collects container metrics from Splunk
│   ├── model/              # SageMaker model training code
│   │   └── train.py        # Trains and deploys the anomaly detection model
│   ├── lambda/             # AWS Lambda functions
│   │   ├── anomaly_handler.py  # Handles anomaly detection and scaling
│   │   └── deploy.py       # Deploys Lambda function to AWS
│   └── utils/              # Utility functions
│       ├── vault_config.py # HashiCorp Vault configuration
│       └── config_manager.py # YAML configuration management
├── config/                 # Configuration files
│   └── config.yaml        # Main configuration file
├── tests/                  # Test files
├── requirements.txt        # Python dependencies
└── README.md              # Project documentation
```

## Prerequisites

- Python 3.8+
- AWS Account with the following services enabled:
  - AWS SageMaker
  - AWS Lambda
  - AWS ECS
  - AWS CloudWatch
  - AWS SNS
  - AWS S3
  - AWS IAM
  - AWS EventBridge
- Splunk Enterprise with container metrics data
- Dynatrace account for additional monitoring
- Docker (for container testing)
- HashiCorp Vault server

## Detailed Setup Steps

### 1. HashiCorp Vault Setup

1. Install HashiCorp Vault:
   ```bash
   # For macOS
   brew install vault
   
   # For Linux
   curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo apt-key add -
   sudo apt-add-repository "deb [arch=amd64] https://apt.releases.hashicorp.com $(lsb_release -cs) main"
   sudo apt-get update && sudo apt-get install vault
   ```

2. Start Vault server in development mode:
   ```bash
   vault server -dev
   ```

3. Set up environment variables for Vault:
   ```bash
   export VAULT_ADDR='http://127.0.0.1:8200'
   export VAULT_TOKEN='your-dev-token'
   ```

4. Enable KV secrets engine:
   ```bash
   vault secrets enable -version=2 kv
   ```

5. Store secrets in Vault:
   ```bash
   # AWS Credentials
   vault kv put secret/container-anomaly-detection/aws/iam role-arn="your-lambda-role-arn"
   vault kv put secret/container-anomaly-detection/aws/s3 bucket-name="your-bucket-name"
   vault kv put secret/container-anomaly-detection/aws/ecs cluster-name="your-cluster-name"
   vault kv put secret/container-anomaly-detection/aws/sns topic-arn="your-sns-topic-arn"
   vault kv put secret/container-anomaly-detection/aws/sagemaker endpoint="your-endpoint-name"
   
   # Splunk Credentials
   vault kv put secret/container-anomaly-detection/splunk/host "your-splunk-host"
   vault kv put secret/container-anomaly-detection/splunk/username "your-username"
   vault kv put secret/container-anomaly-detection/splunk/password "your-password"
   
   # Dynatrace Credentials
   vault kv put secret/container-anomaly-detection/dynatrace/api-token "your-api-token"
   vault kv put secret/container-anomaly-detection/dynatrace/environment-id "your-environment-id"
   ```

### 2. AWS Setup

1. Create an AWS account if you don't have one
2. Set up AWS CLI and configure credentials:
   ```bash
   aws configure
   ```
3. Create required IAM roles:
   - SageMaker execution role
   - Lambda execution role
   - ECS task execution role
4. Create an S3 bucket for model storage
5. Create an SNS topic for notifications
6. Set up an ECS cluster and service

### 3. Splunk Setup

1. Install and configure Splunk Enterprise
2. Set up container metrics collection:
   - Configure container monitoring
   - Set up data inputs
   - Create indexes for container metrics
3. Create a Splunk user with appropriate permissions

### 4. Dynatrace Setup

1. Create a Dynatrace account
2. Set up container monitoring
3. Generate API token for integration

### 5. Local Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/gaurav-cicd/ai-driven-container-anomaly-detection.git
   cd ai-driven-container-anomaly-detection
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure Vault environment variables:
   ```bash
   export VAULT_URL="http://127.0.0.1:8200"
   export VAULT_TOKEN="your-dev-token"
   export VAULT_SECRET_PATH="secret/container-anomaly-detection"
   ```

5. Configure the application:
   ```bash
   # Copy the example config
   cp config/config.yaml.example config/config.yaml
   
   # Edit the config file with your settings
   # Note: Secrets should be referenced using vault:// prefix
   ```

## Automated Execution

The system runs automatically every 5 minutes using AWS EventBridge. Here's how it works:

1. **Initial Deployment**:
   ```bash
   # Deploy Lambda function and EventBridge rule
   python src/lambda/deploy.py
   ```

2. **Automated Workflow**:
   - Every 5 minutes, EventBridge triggers the Lambda function
   - The Lambda function:
     1. Collects container metrics from Splunk
     2. Saves metrics to S3 for historical tracking
     3. Detects anomalies using the SageMaker model
     4. If anomalies are found:
        - Scales containers automatically
        - Sends alerts via SNS
     5. Logs all activities to CloudWatch

3. **Monitoring**:
   - CloudWatch Logs for Lambda execution
   - SNS notifications for alerts
   - S3 for metric history
   - AWS Console for Lambda and EventBridge status

## Testing

1. Run unit tests:
   ```bash
   pytest tests/
   ```

2. Test data collection:
   ```bash
   python src/data_collection/splunk_collector.py --test
   ```

3. Test model locally:
   ```bash
   python src/model/train.py --test
   ```

## Troubleshooting

Common issues and solutions:

1. **Vault Connection Issues**
   - Verify Vault server is running
   - Check VAULT_URL and VAULT_TOKEN environment variables
   - Ensure proper permissions for secret access
   - Check Vault logs for authentication errors

2. **Configuration Issues**
   - Verify config.yaml file exists and is properly formatted
   - Check Vault references in configuration
   - Ensure all required configuration values are present
   - Validate configuration using config_manager.py

3. **Splunk Connection Issues**
   - Verify credentials in Vault
   - Check Splunk service status
   - Verify network connectivity
   - Review Splunk logs for connection errors

4. **AWS Authentication Errors**
   - Check AWS credentials in Vault
   - Verify IAM permissions
   - Ensure correct region is set
   - Review AWS CloudTrail logs

5. **Model Training Failures**
   - Check data quality
   - Verify S3 bucket permissions
   - Review SageMaker logs
   - Validate model parameters in config

6. **Lambda Execution Issues**
   - Check CloudWatch logs
   - Verify Vault access from Lambda
   - Review IAM permissions
   - Check Lambda timeout settings

7. **EventBridge Issues**
   - Verify rule status in AWS Console
   - Check Lambda permissions
   - Review CloudWatch metrics
   - Validate schedule expression

## Contributing

1. Fork the repository
2. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add your feature"
   ```
4. Push to the branch:
   ```bash
   git push origin feature/your-feature-name
   ```
5. Create a Pull Request

## License

MIT License

## Support

For support, please:
1. Check the troubleshooting guide
2. Review existing issues
3. Create a new issue with detailed information
4. Contact the maintainers

## Acknowledgments

- AWS SageMaker team
- Splunk community
- Dynatrace support
- HashiCorp Vault team
- Contributors and maintainers
