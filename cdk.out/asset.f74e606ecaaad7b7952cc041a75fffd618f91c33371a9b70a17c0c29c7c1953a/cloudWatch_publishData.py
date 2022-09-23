import boto3

class cloudWatchPublish():
    def __init__(self):
        self.client_cw = boto3.client('cloudwatch')
        
    
    def publishMetrics(self,namespace, name, dimension, metricValue ):
            
        ''' 
                The dimensions for the metric.

                (dict) --

                A dimension is a name/value pair that is part of the identity of a metric.
                You can assign up to 10 dimensions to a metric. Because dimensions are part of the unique identifier for a metric,
                whenever you add a unique name/value pair to one of your metrics, you are creating a new variation of that metric.

                Name (string) --

                The name of the dimension. Dimension names must contain only ASCII characters 
                and must include at least one non-whitespace character.

                Value (string) --

                The value of the dimension. Dimension values must contain only ASCII characters 
                and must include at least one non-whitespace character.
        '''   
        
        return self.client_cw.put_metric_data(
            
            Namespace = namespace,
            
            MetricData = [{
                'MetricName' : name,
                
                'Dimensions': dimension,
                
                'Values': [metricValue]
             }])
             
    def create_alarm(self,name, alarm_description, metricname, namespace, dimensions, threshold, sns_topic_arn, period):
        
        return self.client_cw.put_metric_alarm(
            AlarmName = name,
            AlarmDescription = alarm_description,
            ActionsEnabled=True,
            AlarmActions=[sns_topic_arn],
            MetricName = metricname,
            Namespace = namespace,  
            Statistic = 'Average', 
            Dimensions = dimensions,
            Period = period,         
            EvaluationPeriods = 1,  
            Threshold = threshold,  
            ComparisonOperator='GreaterThanOrEqualToThreshold',
            )