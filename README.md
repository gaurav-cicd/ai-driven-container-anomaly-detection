<<<<<<< HEAD
# ai-driven-container-anomaly-detection
This project implements an AI-driven monitoring system to detect container performance anomalies using AWS SageMaker, Splunk, and Dynatrace.
=======
# AI-Driven Container Anomaly Detection

This project implements an AI-driven monitoring system to detect container performance anomalies using AWS SageMaker, Splunk, and Dynatrace.

## Project Overview

The system collects container metrics from Splunk, trains an AI model using AWS SageMaker to predict anomalies, and automates anomaly alerts and scaling events using AWS Lambda.

## Architecture

- **Data Collection**: Container metrics are collected using Splunk
- **AI Model**: Anomaly detection model trained using AWS SageMaker
- **Automation**: AWS Lambda functions for alerting and scaling
- **Monitoring**: Dynatrace integration for additional metrics
- **Security**: HashiCorp Vault for secure credential management

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
│       └── vault_config.py # HashiCorp Vault configuration
├── config/                 # Configuration files
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
   vault kv put secret/container-anomaly-detection \
     AWS_ACCESS_KEY_ID="your-access-key" \
     AWS_SECRET_ACCESS_KEY="your-secret-key" \
     AWS_REGION="us-west-2"

   # Splunk Credentials
   vault kv put secret/container-anomaly-detection \
     SPLUNK_HOST="your-splunk-host" \
     SPLUNK_PORT="8089" \
     SPLUNK_USERNAME="your-username" \
     SPLUNK_PASSWORD="your-password"

   # Dynatrace Credentials
   vault kv put secret/container-anomaly-detection \
     DYNATRACE_API_TOKEN="your-api-token" \
     DYNATRACE_ENVIRONMENT_ID="your-environment-id"
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
   git clone https://github.com/yourusername/ai-driven-container-anomaly-detection.git
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

## Usage Steps

### 1. Data Collection

1. Ensure Vault is running and accessible
2. Run the data collector:
   ```bash
   python src/data_collection/splunk_collector.py
   ```
3. Verify collected metrics in `data/` directory

### 2. Model Training

1. Ensure you have collected enough training data
2. Train the model:
   ```bash
   python src/model/train.py
   ```
3. Verify model deployment in AWS SageMaker console

### 3. Lambda Deployment

1. Ensure Vault is accessible from Lambda
2. Deploy the Lambda function:
   ```bash
   python src/lambda/deploy.py
   ```
3. Verify deployment in AWS Lambda console

### 4. Monitoring and Maintenance

1. Monitor CloudWatch logs for Lambda execution
2. Check SNS notifications for anomaly alerts
3. Review ECS service scaling events
4. Monitor model performance and retrain as needed

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

2. **Splunk Connection Issues**
   - Verify credentials in Vault
   - Check Splunk service status
   - Verify network connectivity

3. **AWS Authentication Errors**
   - Check AWS credentials in Vault
   - Verify IAM permissions
   - Ensure correct region is set

4. **Model Training Failures**
   - Check data quality
   - Verify S3 bucket permissions
   - Review SageMaker logs

5. **Lambda Execution Issues**
   - Check CloudWatch logs
   - Verify Vault access from Lambda
   - Review IAM permissions

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
>>>>>>> 9049cfc (initial commit)
