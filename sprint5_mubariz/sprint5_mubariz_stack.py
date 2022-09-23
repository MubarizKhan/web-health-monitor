from aws_cdk import (
    # Duration,
    # aws_sqs as sqs,
    Stack,
    aws_lambda as lambda_,
    RemovalPolicy,
    Duration,
    aws_events as events_,
    aws_events_targets as targets_,
    aws_s3 as s3,
    aws_s3_deployment as s3deploy,
    # aws_sqs as sqs,
    aws_sns_subscriptions as sns_subs_,
    aws_sns as sns_,
    aws_cloudwatch_actions as cw_actions,
    aws_dynamodb as dynamodb,
    aws_iam as iam_,
    aws_cloudwatch as cloudwatch,
    aws_cloudwatch_actions as cw_actions,
    aws_codedeploy as codedeploy,
    aws_apigateway as gateway,
    # aws_apigateway.Cors,
    
)
from constructs import Construct
from s3_resources import s3_res
import os
import boto3
# from gateway import Cors  as cors_
# from gateway import CorsOptions as corO_
# from corO import OPTIONS

class Sprint5MubarizStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        # def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
            # policy = "CloudWatchFullAccess"
            # role = self.create_lambda_role(policy)
        role = self.lambda_role()  # Saving roles for lambda in iam_role
    
            
        dynamo_db = self.create_table("mubariz_table","Timestamp","Subject") 
        db_create_lambda = self.create_lambda('dynamo_lambda', './resources', 'dynamo_lambda.db_lambda_handler',role)
        db_create_lambda.apply_removal_policy(RemovalPolicy.DESTROY)
        
        #granting our dynamodblambda full access to our resources. 
        dynamo_db.grant_full_access(db_create_lambda)

        
        #creating the lambda function for measuring our web health, and passing it the role to access our resources.
        WebHealthLambda = self.create_lambda('webHealthLambda', './resources', 'webHealthLambda.lambda_handler',role)
        WebHealthLambda.apply_removal_policy(RemovalPolicy.DESTROY)
        
        #creating parameters for rule to run, it binds our lambda function with the schedule for periodic invocation.
        #defining the schedule for our lambda function
        lambda_schedule = events_.Schedule.rate(Duration.minutes(1))
        lambda_target = targets_.LambdaFunction(WebHealthLambda) #creating the target for the lambda function.
        
        
        '''
            write parameters for rule function.
        
        '''
        
        rule = events_.Rule(self, "webHealthInvocation", 
            description="Periodic Lambda", 
            schedule = lambda_schedule,
            enabled = True,
            targets = [lambda_target])

      
        #defining our s3 bucket.
                                
        mak_bucket = s3.Bucket(self, "mubariz-skipq-bucket-id",
                                # bucket_name = 'mubariz-s3-bucket',
                                removal_policy = RemovalPolicy.DESTROY,
                                auto_delete_objects = True, 
                                public_read_access=True)
        
                                # SkipQVoyager
        #initializing s3 bucket with file having web urls
        s3deploy.BucketDeployment(self, "voyager_skipq", sources = [s3deploy.Source.asset('./s3_resources', exclude = ['**', '!s3_res.py'])],
                                    destination_bucket = mak_bucket)
                                    
 
 
        #extracting names of 
        bucketName = mak_bucket.bucket_name
        tableName = dynamo_db.table_name
        # Adding Environment Variables
        WebHealthLambda.add_environment('bucketName', bucketName)
        db_create_lambda.add_environment('tableName', tableName)
        
            # creating an sns topic and then adding an email subscription to the sns topic
                   
            # alarm is being binded by topic, which triggers email subscription and dblambdahandler 
       
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_sns.html
        my_topic = sns_.Topic(self, "makTopic")
        my_topicARN = my_topic.topic_arn  #we will send this topic as envVAr to WHL as action in the alarm
        
        my_topic.add_subscription(
        sns_subs_.EmailSubscription("mubariz.khan.skipq@gmail.com"))
            
        my_topic.add_subscription(
        sns_subs_.LambdaSubscription(db_create_lambda))
                                    
                                    
        for iterant in s3_res.URL_TO_MONITOR:  
            
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
    
            dimension = {'URL': iterant}                
            
            
        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% CREATING OUR METRICS %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

            # creating metrics using cloudwatch.metric to access urls{to monitor}, namespace
            # avail_metric = cloudwatch.Metric(namespace=s3_res.URL_NAMESPACE, 
            #                                 metric_name =s3_res.URL_AVAIL_NAMESPACE, 
            #                                 dimensions_map = dimension,
            #                                 period=Duration.minutes(1))
                                            
                                                      
                                            
                            
                                            
            # lat_metric = cloudwatch.Metric(namespace=s3_res.URL_NAMESPACE,
            #                                 metric_name =s3_res.URL_LAT_NAMESPACE,
            #                                 dimensions_map = dimension,
            #                                 period=Duration.minutes(1))
        
        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% CREATING OUR ALARMS %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
          
            
            # lat_alarm = cloudwatch.Alarm(self, 
            #     id='latency_alarm'+'_'+iterant, 
            #     metric=lat_metric, 
            #     threshold = s3_res.THRESHOLD_2,
            #     evaluation_periods = 1,
            #     comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD
            #     )
                
            # avail_alarm = cloudwatch.Alarm(self,
            #     id='avail_alarm'+'_'+iterant, 
            #     metric=avail_metric, 
            #     threshold = s3_res.THRESHOLD_1,
            #     evaluation_periods = 1,
            #     comparison_operator=cloudwatch.ComparisonOperator.LESS_THAN_THRESHOLD
            #     )
                
        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% Binding OUR ALARMS w/ Topics  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                
            # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_cloudwatch_actions/SnsAction.html
            # lat_alarm.add_alarm_action(cw_actions.SnsAction(my_topic))
            # avail_alarm.add_alarm_action(cw_actions.SnsAction(my_topic))
            
            
            # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_dynamodb.html
            
            
            # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_sns_subscriptions.html -> 
            # {down}
            # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_sns_subscriptions/LambdaSubscription.html
                
            # create table here in stack as it is a resource
            # time_atm will be our primary key

            #we'll suscribe the lambda to this topic
            
         #memory and durations k alarms likhnay hain 
        
        '''    
        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% creating our failure dimensions  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
            
        #Failure dimensions for web health lambda
            
        WHL_failure_dimensions = {'FunctionName' : WebHealthLambda.function_name}
        WHL_failure_invo_dimensions = {'FunctionName' : WebHealthLambda.function_name}


                #Failure dimensions for dynamo lambda        
        dynamo_failureDimensions = {'FunctionName' : db_create_lambda.function_name}
        dynamo_failure_invoDimensions = {'FunctionName' : db_create_lambda.function_name}
            
        
        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% creating metrics of lambda duration & invocation    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% by call metric.invocations & metric.duration which  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% return a metric regarding invocation or duration on %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% basis of the function call. %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        
        
        invo_dynamo_metric = db_create_lambda.metric_invocations(
            dimensions_map = dynamo_failure_invoDimensions,
            period=Duration.minutes(5))
        
        dur_dynamo_metric = db_create_lambda.metric_duration(
            dimensions_map = dynamo_failureDimensions,
            period=Duration.minutes(5))
     
        invo_whl_metric = WebHealthLambda.metric_invocations(
            dimensions_map = WHL_failure_invo_dimensions,
            period=Duration.minutes(5))
                                            
        dur_whl_metric = WebHealthLambda.metric_duration(
            dimensions_map = WHL_failure_dimensions,
            period=Duration.minutes(5))
            
            
    # Duration & Invocation ALarms for Web Health Metric  
        
        failure_alarm = cloudwatch.Alarm(self, 
                        id='WHLfirst_failure_alarm_duration', 
                        metric=dur_whl_metric, 
                        evaluation_periods = 1,
                        threshold = 10000,#Duration.millis(2000),
                        #If latency's spikes to a certain value, note that value and apply an alarm on based of that value
                        comparison_operator = cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD #
                )
                
                
        failure_invo_alarm =cloudwatch.Alarm(self, 
                            id='WHLfirst_failure_alarm_invo', 
                            metric=invo_whl_metric, 
                            evaluation_periods = 1,
                            threshold = 1100,#Duration.millis(2000),
                            #If latency's spikes to a certain value, note that value and apply an alarm on based of that value
                            comparison_operator = cloudwatch.ComparisonOperator.LESS_THAN_THRESHOLD 
                                            
                )
                
                
            #Duration & Invocation Alarms for Dyanmo Lambda 
            
           
        Dynamofailure_invo_alarm = cloudwatch.Alarm(self, 
                id='Dynamo_failure_alarm_invo', 
                metric=invo_dynamo_metric, 
                evaluation_periods = 1,
                threshold = 1000,#Duration.millis(2000),
                comparison_operator = cloudwatch.ComparisonOperator.LESS_THAN_THRESHOLD #If latency's spikes to a certain value, note that value and apply an alarm on based of that value
                                            
                )
        # Dynamofailure_invo_alarm  
        Dynamofailure_duration_alarm = cloudwatch.Alarm(self, 
                id='Dynamo_failure_alarm_dur', 
                metric=dur_dynamo_metric, 
                evaluation_periods = 1,
                threshold = 10000,#Duration.millis(2000),
                comparison_operator = cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD #If latency's spikes to a certain value, note that value and apply an alarm on based of that value
                                            
                )
            
            
        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% creating Alias for Rollback  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
            
        
               # alias (Alias) – Lambda Alias to shift traffic. 
            #Updating the version of the alias will trigger a CodeDeploy deployment.
             #   [disable-awslint:ref-via-interface] since we need to modify the alias CFN resource update policy
                
        
        whl_alias = lambda_.Alias(self, "makLambdaAlias1",
                    alias_name="makcurrent_whl1",
                    version= WebHealthLambda.current_version #Returns a lambda.Version which represents the current version of this Lambda function. A new version will be created every time the function’s configuration changes.
                    )
                    
        dynamo_alias = lambda_.Alias(self, "makDynamoLambdaAlias1",
                    alias_name="makcurrent_dynamo1",
                    version= db_create_lambda.current_version #Returns a lambda.Version which represents the current version of this Lambda function. A new version will be created every time the function’s configuration changes.
                    )
                    
        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% Deployment Group  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        
            
        codedeploy.LambdaDeploymentGroup(self, "whl_mak_id1",
                alias=whl_alias,
                deployment_config=codedeploy.LambdaDeploymentConfig.LINEAR_10_PERCENT_EVERY_1_MINUTE,
                alarms=[failure_alarm, failure_invo_alarm
                ]
            )
            
            
        codedeploy.LambdaDeploymentGroup(self, "dynamofailure_mak_id1",
                                  alias=dynamo_alias,
                                  deployment_config=codedeploy.LambdaDeploymentConfig.LINEAR_10_PERCENT_EVERY_1_MINUTE,
                                  alarms=[Dynamofailure_invo_alarm,Dynamofailure_duration_alarm 

                ]
            )
      # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% Binding Failure Alarms with  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% Simple Notification Service  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% To Genrate Emails            %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
           
        #Binding Failure Alarms with SNS
           
        Dynamofailure_invo_alarm.add_alarm_action(cw_actions.SnsAction(my_topic))
        Dynamofailure_duration_alarm.add_alarm_action(cw_actions.SnsAction(my_topic))
        failure_alarm.add_alarm_action(cw_actions.SnsAction(my_topic))
        failure_invo_alarm.add_alarm_action(cw_actions.SnsAction(my_topic))    
    
        '''                 
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% Definining API  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        
                                    
    
                                    
    # Creating a table which'll shift data from s3 bucket to table and then we'll perform CRUD 
    # operations on that table based the API
    #create lambda to shift data from bucket to DB?
    
        bucket_to_db = self.create_dbtable("mak_bucket_to_table",'url') 
        bktToDBHandler = self.create_lambda('makBucketToDB', './resources', 'BucketToDB.bucket_to_dbHandler',role)
        bktToDBHandler.apply_removal_policy(RemovalPolicy.DESTROY)
        bucket_to_db.grant_full_access(bktToDBHandler)
        
        bktToDBHandler.add_environment('bucketName', bucketName)
        bktToDBHandler.add_environment('bktTotable', bucket_to_db.table_name)
        WebHealthLambda.add_environment('bktTotable', bucket_to_db.table_name)
        WebHealthLambda.add_environment('topic_arn', my_topicARN)
        
    #define api with endpoint  as lambda and then invoke table in that lambda 
    # perform CRUD operation according to request sent to API
    #define resources in stack but when will each operation occur,
    #like what will be the user that'll be interacting with the API to tell it 
    # to perform Create, Read, Update, Delete?

        
    #dynamo lambda for writing alarm logs to table
        
        ApiHandler = self.create_lambda("ApiHandler", "./resources", "apiHandler.api_Handler", role)
        ApiHandler.add_environment('bucketName', bucketName)
        ApiHandler.add_environment('bktTotable', bucket_to_db.table_name)
        bucket_to_db.grant_full_access(ApiHandler)
        
                                
        # mak_api.
        # instantiating API Gateway
        apirole = self.api_lambda_role()
        self.create_makapi('mak-CrudApi', ApiHandler)#, True, apirole)
        
        dblambda_schedule = events_.Schedule.rate(Duration.minutes(1))
        dblambda_target = targets_.LambdaFunction(bktToDBHandler) #creating the target for the lambda function.
        
        
        '''
            write parameters for rule function.
        
        '''
        
        rule = events_.Rule(self, "DBLambdaInvocation", 
            description="Periodic DB Lambda", 
            schedule = dblambda_schedule,
            enabled = True,
            targets = [dblambda_target])

        
        

        
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% USER DEFINED HELPER FUNCTIONS %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


        '''
            api = defined here
            items = api.root.add_resource("items")
            items.add_method("GET")
    
        
            [*]--------api
            The rest API that this resource is part of.
            The reason we need the RestApi object itself and not just the ID is because the model is being tracked
            by the top-level RestApi object for the purpose of calculating it’s hash to determine the ID of the deployment.
            This allows us to automatically update the deployment when the model of the REST API changes.
            RETURNS IAPI
            
            api.root.addMethod(‘ANY’, redirectToHomePage); 
            Type:Represents the root resource (“/”) of this API. Use it to define the API model
            // “ANY /” api.root.addResource(‘friends’).addMethod(‘GET’, getFriendsHandler); // “GET /friends”
            
            add_resource(path_part, *, default_cors_preflight_options=None, default_integration=None, default_method_options=None)
        
        '''
        
    def create_makapi(self,id_=None, handler_=None):#,cloud_watch_role=True,role=None):


        # creating a lambda-backed API Gateway
        api = gateway.LambdaRestApi(self, 
                                id = id_, 
                                handler=handler_,
                                cloud_watch_role=True
                                )
                                
        '''
            allow_origins (Sequence[str]) – Specifies the list of origins that are allowed to make requests to this resource. 
            If you wish to allow all origins, specify Cors.ALL_ORIGINS or [ * ].
            Responses will include the Access-Control-Allow-Origin response header. 
            If Cors.ALL_ORIGINS is specified, the Vary: Origin response header will also be included.
        '''

        # adding resource <health> and methods for it
        health = api.root.add_resource("health")
        # health.add_cors_preflight(
        #                         allow_origins=['*'],
        #                         allow_methods=["ANY"])
        
        
        health.add_method("GET", gateway.LambdaIntegration(handler_)) # GET /items

        # adding resource <urls> and methods for it
        url = api.root.add_resource("url")
        # url.add_method("GET", gateway.LambdaIntegration(handler_))
        # url.add_cors_preflight(
        #                         allow_origins=['*'],
        #                         allow_methods=["ANY"])

        url.add_method("GET", gateway.LambdaIntegration(handler_))#,credentials_role=role))       # GET /url
        url.add_method("PUT", gateway.LambdaIntegration(handler_))#,credentials_role=role))      # POST /url
        url.add_method("PATCH", gateway.LambdaIntegration(handler_))#,credentials_role=role))     # UPDATE /url
        url.add_method("DELETE", gateway.LambdaIntegration(handler_))#,credentials_role=role))    # DELETE /url
 
        return api
            
    
    
    def create_lambda(self, id_, asset, handler,role):
        return lambda_.Function(self, id_, 
                runtime = lambda_.Runtime.PYTHON_3_6,
                handler = handler,
                timeout= Duration.minutes(1),
                code = lambda_.Code.from_asset(asset),
                role = role
                )
                
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    ##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%            
                
    
                
    def create_lambda_role(self, policyName):
        '''
             Link To Docs: https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_iam.html
            https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_iam/ManagedPolicy.html
            
            AWS Identity and Access Management Construct Library:
            Define a role and add permissions to it. This will automatically create and attach an IAM policy to the role:
            
            Class: ManagedPolicy:
                -example: my_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"))
                
            classmethod from_aws_managed_policy_name(managed_policy_name)
            Import a managed policy from one of the policies that AWS manages.
            For this managed policy, you only need to know the name to be able to use it.
            Some managed policy names start with “service-role/”, some start with “job-function/”,
            and some don’t start with anything. Include the prefix when constructing this object.
        
        '''
        lambda_role = iam_.Role(self, "Role",
        assumed_by=iam_.ServicePrincipal("lambda.amazonaws.com"),
        description = "example role")
        
        lambda_role.add_managed_policy(iam_.ManagedPolicy.from_aws_managed_policy_name(policyName))
        
        return lambda_role
        
        
        #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        
    def create_table(self, id, partition_key=None, sort_key=None):
        '''
        Link: https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_dynamodb/Attribute.html
        aws_cdk.aws_dynamodb.Table Provides a DynamoDB table.
        Parameters
            scope (Construct) –
            id (str) – 
            partition_key (Attribute) – Partition key attribute definition.
            sort_key (Optional[Attribute]) – Sort key attribute definition. Default: no sort key
                                Attribute-> Represents an attribute for describing the key schema for the table and indexes.
        '''
        dynamo_table = dynamodb.Table(self, id,
                                #   table_name=tableName,
                                  partition_key= dynamodb.Attribute(name=partition_key, type=dynamodb.AttributeType.STRING),
                                  sort_key= dynamodb.Attribute(name=sort_key, type=dynamodb.AttributeType.STRING),
                                  removal_policy=RemovalPolicy.RETAIN)
        return dynamo_table
        
        
        
        #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        
        
    def lambda_role(self, id=None, assumed_by=None, managed_policies=None):  # creating a function for defining a lambda role
        '''
            Link To Docs: https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_iam.html
            https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_iam/ManagedPolicy.html
            
            AWS Identity and Access Management Construct Library:
            Define a role and add permissions to it. This will automatically create and attach an IAM policy to the role:
            
            Class: ManagedPolicy:
                -example: my_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"))
                
            classmethod from_aws_managed_policy_name(managed_policy_name)
            Import a managed policy from one of the policies that AWS manages.
            For this managed policy, you only need to know the name to be able to use it.
            Some managed policy names start with “service-role/”, some start with “job-function/”,
            and some don’t start with anything. Include the prefix when constructing this object.
        
        '''
    
        lambda_role = iam_.Role(self, "Role",
                               assumed_by=iam_.ServicePrincipal("lambda.amazonaws.com"),
                               managed_policies=[
                                                iam_.ManagedPolicy.from_aws_managed_policy_name('CloudWatchFullAccess'),
                                                iam_.ManagedPolicy.from_aws_managed_policy_name('AmazonDynamoDBFullAccess'),
                                                iam_.ManagedPolicy.from_aws_managed_policy_name('service-role/AWSLambdaBasicExecutionRole'),
                                                iam_.ManagedPolicy.from_aws_managed_policy_name('AWSLambdaInvocation-DynamoDB')
                                                ])
        return lambda_role



    def api_lambda_role(self, id=None, assumed_by=None, managed_policies=None):  # creating a function for defining a lambda role
        '''
            Link To Docs: https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_iam.html
            https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_iam/ManagedPolicy.html
            
            AWS Identity and Access Management Construct Library:
            Define a role and add permissions to it. This will automatically create and attach an IAM policy to the role:
            
            Class: ManagedPolicy:
                -example: my_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"))
                
            classmethod from_aws_managed_policy_name(managed_policy_name)
            Import a managed policy from one of the policies that AWS manages.
            For this managed policy, you only need to know the name to be able to use it.
            Some managed policy names start with “service-role/”, some start with “job-function/”,
            and some don’t start with anything. Include the prefix when constructing this object.
        
        '''
    
        lambda_role = iam_.Role(self, "APiRole",
                               assumed_by=iam_.ServicePrincipal("lambda.amazonaws.com"),
                               managed_policies=[
                                                iam_.ManagedPolicy.from_aws_managed_policy_name('CloudWatchFullAccess'),
                                                iam_.ManagedPolicy.from_aws_managed_policy_name('AmazonDynamoDBFullAccess'),
                                                iam_.ManagedPolicy.from_aws_managed_policy_name('service-role/AWSLambdaBasicExecutionRole'),
                                                iam_.ManagedPolicy.from_aws_managed_policy_name('AWSLambdaInvocation-DynamoDB')
                                                ])
        return lambda_role
        # The code that defines your stack goes here

        # example resource
        # queue = sqs.Queue(
        #     self, "Sprint4MubarizQueue",
        #     visibility_timeout=Duration.seconds(300),
        # )
    
    
    def create_dbtable(self, id, partition_key=None):
        '''
        Link: https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_dynamodb/Attribute.html
        aws_cdk.aws_dynamodb.Table Provides a DynamoDB table.
        Parameters
            scope (Construct) –
            id (str) – 
            partition_key (Attribute) – Partition key attribute definition.
            sort_key (Optional[Attribute]) – Sort key attribute definition. Default: no sort key
                                Attribute-> Represents an attribute for describing the key schema for the table and indexes.
        '''
        dynamo_table = dynamodb.Table(self, id,
                                #   table_name=tableName,
                                  partition_key= dynamodb.Attribute(name=partition_key, type=dynamodb.AttributeType.STRING),
                                #   sort_key= dynamodb.Attribute(name=sort_key, type=dynamodb.AttributeType.STRING),
                                  removal_policy=RemovalPolicy.RETAIN)
        return dynamo_table
    
    # def createNewDB(self):
    #     # Get the service resource.
        
    #     dynamodb = boto3.resource('dynamodb')
        
    #     # Create the DynamoDB table.
    #     table = dynamodb.create_table(
    #         TableName='bktTotableDBNAME1',
    #         KeySchema=[
    #             {
    #                 'AttributeName': 'id_',
    #                 'KeyType': 'HASH'
    #             },
    #             {
    #                 'AttributeName': 'url',
    #                 'KeyType': 'RANGE'
    #             }
    #         ],
    #         AttributeDefinitions=[
    #             {
    #                 'AttributeName': 'id_',
    #                 'AttributeType': 'N'
    #             },
    #             {
    #                 'AttributeName': 'url',
    #                 'AttributeType': 'S'
    #             },
    #         ],
    #         ProvisionedThroughput={
    #             'ReadCapacityUnits': 5,
    #             'WriteCapacityUnits': 5
    #         })
        
    #     return table