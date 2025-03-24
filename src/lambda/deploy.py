import os
import boto3
import zipfile
from datetime import datetime

def create_lambda_package():
    """Create a ZIP package for the Lambda function."""
    package_dir = "lambda_package"
    os.makedirs(package_dir, exist_ok=True)
    
    # Copy the Lambda function code
    with open("src/lambda/anomaly_handler.py", "r") as source:
        with open(f"{package_dir}/lambda_function.py", "w") as target:
            target.write(source.read())
    
    # Create ZIP file
    zip_path = "lambda_function.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(package_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, package_dir)
                zipf.write(file_path, arcname)
    
    return zip_path

def deploy_lambda():
    """Deploy the Lambda function to AWS."""
    lambda_client = boto3.client('lambda')
    function_name = "container-anomaly-detector"
    
    # Create Lambda package
    zip_path = create_lambda_package()
    
    try:
        # Check if function exists
        try:
            lambda_client.get_function(FunctionName=function_name)
            print(f"Updating existing function: {function_name}")
            
            # Update function code
            with open(zip_path, 'rb') as file_data:
                bytes_content = file_data.read()
                lambda_client.update_function_code(
                    FunctionName=function_name,
                    ZipFile=bytes_content
                )
        except lambda_client.exceptions.ResourceNotFoundException:
            print(f"Creating new function: {function_name}")
            
            # Create new function
            with open(zip_path, 'rb') as file_data:
                bytes_content = file_data.read()
                lambda_client.create_function(
                    FunctionName=function_name,
                    Runtime='python3.8',
                    Handler='lambda_function.lambda_handler',
                    Role=os.getenv('LAMBDA_ROLE_ARN'),
                    Code={'ZipFile': bytes_content},
                    Timeout=300,
                    MemorySize=256,
                    Environment={
                        'Variables': {
                            'MODEL_NAME': 'container-anomaly-detector',
                            'ECS_CLUSTER_NAME': os.getenv('ECS_CLUSTER_NAME'),
                            'ECS_SERVICE_NAME': os.getenv('ECS_SERVICE_NAME'),
                            'SNS_TOPIC_ARN': os.getenv('SNS_TOPIC_ARN')
                        }
                    }
                )
        
        # Create CloudWatch Events rule
        events_client = boto3.client('events')
        rule_name = f"{function_name}-rule"
        
        try:
            events_client.put_rule(
                Name=rule_name,
                ScheduleExpression='rate(5 minutes)',
                State='ENABLED',
                Description='Trigger container anomaly detection every 5 minutes'
            )
            
            # Add permission for CloudWatch Events to invoke Lambda
            lambda_client.add_permission(
                FunctionName=function_name,
                StatementId=f"{rule_name}-permission",
                Action='lambda:InvokeFunction',
                Principal='events.amazonaws.com',
                SourceArn=f"arn:aws:events:{os.getenv('AWS_REGION')}:{os.getenv('AWS_ACCOUNT_ID')}:rule/{rule_name}"
            )
            
            # Add Lambda as target for the rule
            events_client.put_targets(
                Rule=rule_name,
                Targets=[{
                    'Id': f"{function_name}-target",
                    'Arn': f"arn:aws:lambda:{os.getenv('AWS_REGION')}:{os.getenv('AWS_ACCOUNT_ID')}:function:{function_name}"
                }]
            )
            
        except events_client.exceptions.ResourceAlreadyExistsException:
            print(f"Rule {rule_name} already exists")
        
        print(f"Successfully deployed Lambda function: {function_name}")
        
    except Exception as e:
        print(f"Error deploying Lambda function: {str(e)}")
        raise
    
    finally:
        # Clean up
        if os.path.exists(zip_path):
            os.remove(zip_path)
        if os.path.exists("lambda_package"):
            import shutil
            shutil.rmtree("lambda_package")

if __name__ == "__main__":
    deploy_lambda() 