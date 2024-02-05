from aws_cdk import (
    Stack,
    ScopedAws,
    CfnOutput,
    aws_ecs as ecs,
    aws_s3 as s3,
)
from aws_cdk.aws_iam import (
    ManagedPolicy,
    ServicePrincipal,
    Role,
)
from constructs import Construct

from .ipv6_vpc import Ipv6Vpc


class CdkIpv6SubnetsStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        scoped_aws = ScopedAws(self)

        vpc = Ipv6Vpc(self, "Ipv6Vpc")

        cluster = ecs.Cluster(
            self,
            "AppCluster",
            vpc=vpc.vpc,
            enable_fargate_capacity_providers=True,
        )

        log_bucket = s3.Bucket(self, "AppClusterLogs")
        CfnOutput(self, "LogBucketName", value=log_bucket.bucket_name)

        task_role = Role(
            self,
            "EcsTaskRole",
            assumed_by=ServicePrincipal("ecs-tasks.amazonaws.com"),
        )
        log_bucket.grant_put(task_role)

        exec_role = Role(
            self,
            "EcsTaskExecRole",
            assumed_by=ServicePrincipal("ecs-tasks.amazonaws.com"),
            managed_policies=[
                ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AmazonECSTaskExecutionRolePolicy"
                )
            ],
        )

        task_definition = ecs.FargateTaskDefinition(
            self,
            "MainService",
            cpu=256,
            memory_limit_mib=512,
            task_role=task_role.without_policy_updates(),
            # add_containerでloggingを渡すと、ECRにアクセスするActionがないロールを勝手に作るので、自分でつくって指定する
            execution_role=exec_role.without_policy_updates(),
        )
        task_definition.add_firelens_log_router(
            "fluent-bit",
            # dockerhubからpullする
            image=ecs.ContainerImage.from_registry("amazon/aws-for-fluent-bit"),
            firelens_config=ecs.FirelensConfig(
                type=ecs.FirelensLogRouterType.FLUENTBIT,
            ),
        )
        task_definition.add_container(
            "app",
            # NOTE: これはdockerhubからpullしてくる
            image=ecs.ContainerImage.from_registry("amazon/amazon-ecs-sample"),
            # NOTE: ECRはIPv6に対応していないのでECRからイメージをpullできずタスクが起動しない
            # image=ecs.ContainerImage.from_registry("public.ecr.aws/ecs-sample-image/amazon-ecs-sample:latest"),
            logging=ecs.FireLensLogDriver(
                options={
                    "Name": "s3",
                    "Match": "*",
                    "region": scoped_aws.region,
                    "bucket": log_bucket.bucket_name,
                    "endpoint": f"https://s3.dualstack.{scoped_aws.region}.amazonaws.com",
                    "total_file_size": "1M",
                    "use_put_object": "On",
                },
            ),
            # NOTE: CloudWatch LogsがIPv6に対応してないようなので、ロギングを有効にするとタスクが起動しない
            # logging=ecs.GenericLogDriver(
            #    log_driver="awslogs",
            #    options={
            #        "awslogs-create-group": "true",
            #        "awslogs-group": construct_id,
            #        "awslogs-region": "ap-northeast-1",
            #        "awslogs-stream-prefix": "app",
            #    }
            # )
        )

        service = ecs.FargateService(
            self,
            "AppService",
            cluster=cluster,
            task_definition=task_definition,
            security_groups=[
                vpc.sg_default,
                vpc.sg_allow_http,
            ],
        )
