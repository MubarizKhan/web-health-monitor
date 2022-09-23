from aws_cdk import (
    Stack,
    pipelines,
    aws_iam as iam,
    SecretValue,
    aws_codepipeline_actions as cpactions_, #https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_codepipeline_actions/GitHubTrigger.html#aws_cdk.aws_codepipeline_actions.GitHubTrigger
    aws_codebuild as cb,
    )
    
from constructs import Construct
import aws_cdk as cdk
from s3_resources import s3_res
from sprint5_mubariz.sprint5_mak_infrastage import sprint5MakInfrastage 


class sprint5MakPipelineStack(Stack):
    

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        pipeline_roles = self.create_role()                                                
        
        '''
             classmethod git_hub(repo_string, branch, *, authentication=None, trigger=None)
            Returns a GitHub source, using OAuth tokens to authenticate with GitHub and a separate webhook to detect changes.
            pipelines.CodePipelineSource.git_hub("owner/repo", "main")
            Authentication will be done by a secret called github-token in AWS Secrets Manager (unless specified otherwise).
            The token should have these permissions:
            repo - to read the repository
            admin:repo_hook - if you plan to use webhooks (true by default)
                            Parameters
                                    repo_string (str) –
                                    branch (str) 
                                    authentication (Optional[SecretValue]) – A GitHub OAuth token to use for authentication. 
                                                                            It is recommended to use a Secrets Manager Secret to obtain the token:: const oauth = cdk.SecretValue.secretsManager(‘my-github-token’); 
                                                                            The GitHub Personal Access Token should have these scopes: - repo - to read the repository - admin:repo_hook -
                                                                            if you plan to use webhooks (true by default) Default: - SecretValue.secretsManager(‘github-token’)
                                                                            
                                    trigger (Optional[GitHubTrigger]) – How AWS CodePipeline should be triggered. With the default value “WEBHOOK”, 
                                                                        a webhook is created in GitHub that triggers the action. With “POLL”,
                                                                        CodePipeline periodically checks the source for changes. With “None”, 
                                                                        the action is not triggered through changes in the source.
                                                                        To use WEBHOOK, your GitHub Personal Access Token should have admin:repo_hook scope (in addition to the regular repo scope).
                                                                        Default: GitHubTrigger.WEBHOOK
        '''
        
        # CodePipelineSource : https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.pipelines/CodePipelineSource.html
        #We are defining our Source here
        source = pipelines.CodePipelineSource.git_hub( "mubarizkhan2022skipq/Voyager", 
                                    "main",
                                    authentication=SecretValue.secrets_manager("mak-token"),
                                    trigger=cpactions_.GitHubTrigger("POLL")
                                    
                                  )
        # aws_codepipeline_actions.GitHubTrigger(value)
        
        #we are building our code here.
        
        synth=pipelines.ShellStep("Synth", 
                                  input=source,
                                  commands=["cd mubarizkhan/sprint5_mubariz",
                                            "pip install -r requirements.txt",
                                            "npm install -g aws-cdk",
                                            "cdk synth"
                                            ],
                                  primary_output_directory = "mubarizkhan/sprint5_mubariz/cdk.out",
                                #   role = pipeline_roles,
                                #   privileged = True
                                #   /Voyager/mubarizkhan/sprint3_mubariz/cdk.out
                                 )
        #This is the Build Part
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.pipelines/CodePipelineSource.html
        # We are building our pipeline here.
        mak_pipeline = pipelines.CodePipeline( self, 
                                              "mak_pipeline",
                                              synth = synth,
                                              docker_enabled_for_self_mutation=True
                                             )
                                             
        #https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.pipelines/ShellStep.html
        stack_test =pipelines.ShellStep(
            "Unit Test",
            commands=[
                "cd mubarizkhan/sprint5_mubariz/",
                "pip install -r requirements.txt",
                "npm install -g aws-cdk",
                "pytest"]
        )
        
        
        # pyresttest_exec = pipelines.CodeBuildStep("pyresttest_exec", commands=[],
        #                         # Changes to environment. This environment will be combined with the pipeline’s default environment
        #                         build_environment = cb.BuildEnvironment(
        #                                                 build_image = cb.LinuxBuildImage.from_asset(self,"docker_imageid", directory="./pyrest").from_docker_registry(name='docker:dind'),
        #                                                 privileged = True),
                                 
        #                         partial_build_spec = cb.BuildSpec.from_object(
        #                             {
        #                                 "version": 0.2,
        #                                 "phases" : {
                                                    
        #                                             "install": { "commands": ["nohup /usr/local/bin/dockerd --host=unix:///var/run/docker.sock --host=tcp://127.0.0.1:2375 --storage-driver=overlay2 &",
        #                                                          "timeout 15 sh -c \"until docker info; do echo .; sleep 1; done\""]
                                                        
        #                                                         },
        #                                             "pre_build" : { "commands": [ "cd Voyager/mubarizkhan/sprint4_mubariz/pyrest",
        #                                                                         #   "docker pull janssen92/pyresttest",
        #                                                                             "ls",
        #                                                                           "sudo docker build -t api-mak ."
        #                                                                         ]
        #                                                           },
        #                                             "build": {"commands":["sudo docker images","sudo docker run api-mak"]}
        #                                     #   "docker run helloworld echo "Hello, World!"
        #                                             }
        #                             }),
        #                         role = pipeline_roles
        #                         ) 
                                #   /Voyager/mubarizkhan/sprint3_mubariz/cdk.out
                                
                #docker test for the pipeline as post beta stage

        pbs = cb.BuildSpec.from_object(
                    {
                        "version": 0.2,
                        "phase": {
                            "install": {
                                "commands": [
                                                "nohup /usr/local/bin/dockerd --host=unix:///var/run/docker.sock --host=tcp://127.0.0.1:2375 --storage-driver=overlay2 &",
                                                "timeout 15 sh -c \"until docker info; do echo .; sleep 1; done\""
                                            ]
                                        },
                            "pre_build":{
                                "commands":[   
                                                "ls && cd sprint5_mubariz/pyrest" ,

                                                "docker build -t api-mak2 ."
                                            ]    
                                        },
                            "build":{
                                "commands": [
                                        "docker images",
                                        "docker run  api-mak2 https://4ifp46i0ie.execute-api.us-west-1.amazonaws.com api_test.yml"
                                    ]                                
                                }            
                            }    
                    }    

            )
        doc_pyrrest_test = pipelines.CodeBuildStep("mak" , commands = [] ,
                        build_environment = cb.BuildEnvironment(
                                        build_image = cb.LinuxBuildImage.from_asset(self , "MakPyrestImage" , directory = "./pyrest").from_docker_registry(name='docker:dind'),
                                        privileged = True), 
                        partial_build_spec = pbs)



                                 
        
        
        #for staging, we'll define another stack infra_stage
        beta = sprint5MakInfrastage(self, "makS5-beta-stage")#,env=cdk.Environment(region='us-west-1'))
        prod = sprint5MakInfrastage(self, "makS5-prod-stage")#, env=cdk.Environment(region='us-east-1'))
        
        
                    
            
        '''
        
                  Deploy a single Stage by itself.

                Add a Stage to the pipeline, to be deployed in sequence with other Stages added to the pipeline.
                All Stacks in the stage will be deployed in an order automatically determined by their relative dependencies.
                
                Parameters:
                        stage (Stage) –
                
                        post (Optional[Sequence[Step]]) – Additional steps to run after all of the stacks in the stage.
                        Default: - No additional steps
                
                        pre (Optional[Sequence[Step]]) – Additional steps to run before any of the stacks in the stage. 
                        Default: - No additional steps
                
                        stack_steps (Optional[Sequence[StackSteps]]) – Instructions for stack level steps. 
                        Default: - No additional instructions
                        
                    
                class aws_cdk.pipelines.ManualApprovalStep(id, *, comment=None)
            
                Bases: aws_cdk.pipelines.Step
                A manual approval step.
                If this step is added to a Pipeline, the Pipeline will be paused waiting for a human to resume it
                Only engines that support pausing the deployment will support this step type.
                        ExampleMetadata
                            infused
                        Example:
            
                                # pipeline: pipelines.CodePipeline
                            
                                preprod = MyApplicationStage(self, "PreProd")
                                prod = MyApplicationStage(self, "Prod")
                            
                                pipeline.add_stage(preprod,
                                    post=[
                                        pipelines.ShellStep("Validate Endpoint",
                                            commands=["curl -Ssf https://my.webservice.com/"]
                                        )
                                    ]
                                )
                                pipeline.add_stage(prod,
                                    pre=[
                                        pipelines.ManualApprovalStep("PromoteToProd")
                                    ]
                                )
            '''
        
        
        # add stage to pipeline
        
        mak_pipeline.add_stage(beta, pre=[stack_test], post=[doc_pyrrest_test])
        
        mak_pipeline.add_stage(prod, pre = [pipelines.ManualApprovalStep("mak_test-step")]) # added a amanual approval step



    def create_role(self):  
            
        """
            creating a function for defining a roles/
            
            Represents a principal that has multiple types of principals.
    
            A composite principal cannot have conditions. i.e. multiple 
            ServicePrincipals that form a composite principal 
            
            AWS service principals
            
            A service principal is an identifier for a service. 
            IAM roles that can be assumed by an AWS service are called service roles. 
            Service roles must include a trust policy. 
            Trust policies are resource-based policies attached to a role that defines 
            which principals can assume the role
        
        """
        role = iam.Role(self, "Pipeline-Role",
                       assumed_by=iam.CompositePrincipal(
                           iam.ServicePrincipal("lambda.amazonaws.com"),
                           iam.ServicePrincipal("sns.amazonaws.com"),
                           iam.ServicePrincipal("codebuild.amazonaws.com")),
                       managed_policies=
                       [
                        iam.ManagedPolicy.from_aws_managed_policy_name('CloudWatchFullAccess'),
                        iam.ManagedPolicy.from_aws_managed_policy_name('AmazonDynamoDBFullAccess'),
                        iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AWSLambdaBasicExecutionRole'),
                        iam.ManagedPolicy.from_aws_managed_policy_name('AWSLambdaInvocation-DynamoDB'),
                        
                        iam.ManagedPolicy.from_aws_managed_policy_name("AwsCloudFormationFullAccess"),
                        iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMFullAccess"),
                        iam.ManagedPolicy.from_aws_managed_policy_name("AWSCodePipeline_FullAccess"),
                        iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess")                  
                        
                        ])
        return role