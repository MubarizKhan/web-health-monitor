import datetime
import boto3
import sys
# import constants as constants
import os
import urllib3
from cloudWatch_publishData import cloudWatchPublish

  # client = boto3.client('cloudwatch')
s3_client = boto3.client('s3')
s3_client.download_file(os.environ['bucketName'],'s3_res.py', '/tmp/s3_res.py')
sys.path.insert(1,'/tmp')
    

def lambda_handler(event,context):
    
    '''
    When Lambda invokes your function handler, the Lambda runtime passes two arguments to the function handler:URL_AVAIL_NAMESPACE
    The first argument is the event object. An event is a JSON-formatted document that contains data for a Lambda function to process. 
    The event object contains information from the invoking service. When you invoke a function, you determine the structure and contents of the event. 
    When an AWS service invokes your function, the service defines the event structure.
    
    The second argument is the context object. A context object is passed to your function by Lambda at runtime. 
    This object provides methods and properties that provide information about the invocation, function, and runtime environment.
    
    This function is using two user-defined functions which are syslogbility & calc_latency,
    what this basically does is iterate over the list which contains url_strings{constants.py},
    and pass each index of the list to the calc_latency & calc_availability and adds the result along with the name of the url 
    to a dictionary and appends that dictionary to a list. 
    
    returns list of dictionaries.
    '''
    print('Testing')
    # cw_client=boto3.client('cloudwatch')

    cw_obj = cloudWatchPublish()
  
    import s3_res
    l = []
    dim_l = []
    
    
    #  l = []
        # table = dynamodb.Table('my-table')
        # https://dynobase.dev/dynamodb-python-with-boto3/#:~:text=To%20get%20all%20items%20from,the%20results%20in%20a%20loop
    dynamodb = boto3.resource('dynamodb')
    bucktToTableName =  os.environ['bktTotable']
    
    table = dynamodb.Table(bucktToTableName)
    response = table.scan()
    data = response['Items']
        
        # data is a list of dictionaries
    for i in data:
        l.append(i["url"])
    
    for i in l:
        values = dict()
        print(i, type(i))
        avail_val = calc_availability(i)
        latency_val = calc_latency(i)
        
        
        
        
        # dimensions = [{'Name':i, 'URL': latency_val},]
        dimensions = [{'Name':'URL', 'Value': i},]
        # dimensions = [{'MAKURL': i}]                
        
        
        # for availability
        metric_avail_name = s3_res.URL_AVAIL_NAMESPACE + "_" + i
        metric_lat_name = s3_res.URL_LAT_NAMESPACE + "_" + i
        
        # cw_obj.publishMetrics(namespace = s3_res.URL_NAMESPACE, metricValue = avail_val, name = metric_avail_name, dimension = dimension)
        cw_obj.publishMetrics(namespace = s3_res.URL_NAMESPACE, 
        name = s3_res.URL_AVAIL_NAMESPACE,
        dimension = dimensions,
        metricValue = avail_val)
        
        
        #for latency
        cw_obj.publishMetrics(namespace = s3_res.URL_NAMESPACE, 
        name = s3_res.URL_LAT_NAMESPACE,
        dimension = dimensions,
        metricValue = latency_val)
        
         # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% CREATING OUR ALARMS %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
          
           
        cw_obj.create_alarm(str(i)+ "MAK-Latency Alarm", 
                                "MAKLatency Alarm for"+ str(i), 
                                s3_res.URL_LAT_NAMESPACE, 
                                s3_res.URL_NAMESPACE, 
                                dimensions, 
                                s3_res.THRESHOLD_2,
                                os.environ['topic_arn'],
                                period = s3_res.sec_lim)
        '''    
            
        avail_alarm = cw_client.put_metric_alarm(
            AlarmName = i+"Latency Alarm " ,
            AlarmDescription = "Latency Alarm for " + i,
            ActionsEnabled=True,
            AlarmActions=[os.environ['topic_arn']],
            MetricName = lat_metric,
            Namespace = s3_res.URL_AVAIL_NAMESPACE,  
            Dimensions = dimensions,
            Period = s3_res.sec_lim,        
            EvaluationPeriods = 1, 
            Threshold = s3_res.THRESHOLD_1,  
            ComparisonOperator='GreaterThanThreshold',
            )
        '''
                
        # avail_alarm = cloudwatch.Alarm(self,
        #         id='avail_alarm'+'_'+iterant, 
        #         metric=avail_metric, 
        #         threshold = s3_res.THRESHOLD_1,
        #         evaluation_periods = 1,
        #         comparison_operator=cloudwatch.ComparisonOperator.LESS_THAN_THRESHOLD
        #         )
                
        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% Binding OUR ALARMS w/ Topics  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                
            # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_cloudwatch_actions/SnsAction.html
        # lat_alarm.add_alarm_action(cw_actions.SnsAction(os.environ['topic_arn']))
        # avail_alarm.add_alarm_action(cw_actions.SnsAction(os.environ['topic_arn']))
        
        
        
        
        values.update({"url_name":i,"availability":avail_val,"Latency":latency_val}) #, "DIM":dimension, "name": metric_avail_name, "s3_res.URL_NAMESPACE":s3_res.URL_NAMESPACE})
        # l.append(values)
        dim_l.append(values)
    # Creating metrics for Dynamo Entried
        
    # return l
    return l,dim_l
    
    
def calc_availability(url):
    '''
        This function accepts an url as an argument to the function,
        it uses that certain url to calculate the availability of that
        particular web resource.
        The HTTP 200 OK success status response code indicates that the request has succeeded
    
    '''
    http = urllib3.PoolManager()
    response = http.request("GET",url)
    if response.status==200:
        return 1.0 #if connection is a success will return True
    else:
        return 0.0
        
def calc_latency(url):
    '''
        This function accepts an url as an argument to the function,
        it uses that certain url to calculate the latency of that
        particular web resource.

    '''
    
    http = urllib3.PoolManager()
    start = datetime.datetime.now()
    response = http.request("GET", url)
    end = datetime.datetime.now()
    delta = end - start
    latencySec = round(delta.microseconds * 0.000001,6)
    return latencySec