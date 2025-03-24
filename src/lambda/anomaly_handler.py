import json
import boto3
import os
from datetime import datetime

class AnomalyHandler:
    def __init__(self):
        self.sagemaker = boto3.client('sagemaker-runtime')
        self.ecs = boto3.client('ecs')
        self.sns = boto3.client('sns')
        self.model_name = "container-anomaly-detector"
        self.cluster_name = os.getenv('ECS_CLUSTER_NAME')
        self.service_name = os.getenv('ECS_SERVICE_NAME')
        self.sns_topic_arn = os.getenv('SNS_TOPIC_ARN')
        
    def get_container_metrics(self):
        """Get current container metrics from CloudWatch."""
        cloudwatch = boto3.client('cloudwatch')
        end_time = datetime.now()
        start_time = end_time.replace(minute=end_time.minute - 5)
        
        metrics = cloudwatch.get_metric_data(
            MetricDataQueries=[
                {
                    'Id': 'cpu',
                    'MetricStat': {
                        'Metric': {
                            'Namespace': 'ECS/ContainerInsights',
                            'MetricName': 'CPUUtilization',
                            'Dimensions': [
                                {'Name': 'ClusterName', 'Value': self.cluster_name},
                                {'Name': 'ServiceName', 'Value': self.service_name}
                            ]
                        },
                        'Period': 300,
                        'Stat': 'Average'
                    },
                    'StartTime': start_time,
                    'EndTime': end_time
                },
                {
                    'Id': 'memory',
                    'MetricStat': {
                        'Metric': {
                            'Namespace': 'ECS/ContainerInsights',
                            'MetricName': 'MemoryUtilization',
                            'Dimensions': [
                                {'Name': 'ClusterName', 'Value': self.cluster_name},
                                {'Name': 'ServiceName', 'Value': self.service_name}
                            ]
                        },
                        'Period': 300,
                        'Stat': 'Average'
                    },
                    'StartTime': start_time,
                    'EndTime': end_time
                }
            ]
        )
        
        return metrics['MetricDataResults']
    
    def detect_anomaly(self, metrics):
        """Detect anomalies using the SageMaker endpoint."""
        # Prepare input data
        input_data = {
            'avg_cpu': metrics[0]['Values'][0]['Value'],
            'avg_memory': metrics[1]['Values'][0]['Value'],
            'avg_disk': 0.0  # Default value, can be updated based on actual metrics
        }
        
        # Call SageMaker endpoint
        response = self.sagemaker.invoke_endpoint(
            EndpointName=self.model_name,
            ContentType='application/json',
            Body=json.dumps(input_data)
        )
        
        result = json.loads(response['Body'].read().decode())
        return result['prediction'] == -1  # -1 indicates anomaly
    
    def scale_service(self, scale_up=True):
        """Scale the ECS service up or down."""
        service = self.ecs.describe_services(
            cluster=self.cluster_name,
            services=[self.service_name]
        )
        
        current_count = service['services'][0]['desiredCount']
        new_count = current_count + 1 if scale_up else max(1, current_count - 1)
        
        self.ecs.update_service(
            cluster=self.cluster_name,
            service=self.service_name,
            desiredCount=new_count
        )
        
        return new_count
    
    def send_notification(self, anomaly_detected, metrics):
        """Send notification via SNS."""
        message = {
            'timestamp': datetime.now().isoformat(),
            'anomaly_detected': anomaly_detected,
            'metrics': {
                'cpu': metrics[0]['Values'][0]['Value'],
                'memory': metrics[1]['Values'][0]['Value']
            },
            'cluster': self.cluster_name,
            'service': self.service_name
        }
        
        self.sns.publish(
            TopicArn=self.sns_topic_arn,
            Message=json.dumps(message)
        )

def lambda_handler(event, context):
    handler = AnomalyHandler()
    
    try:
        # Get current metrics
        metrics = handler.get_container_metrics()
        
        # Detect anomalies
        anomaly_detected = handler.detect_anomaly(metrics)
        
        if anomaly_detected:
            # Scale up the service
            new_count = handler.scale_service(scale_up=True)
            
            # Send notification
            handler.send_notification(True, metrics)
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': f'Anomaly detected. Scaled service to {new_count} instances.',
                    'metrics': metrics
                })
            }
        else:
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'No anomalies detected.',
                    'metrics': metrics
                })
            }
            
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        } 