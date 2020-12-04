import os.path

import aws_cdk.core as core
import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_iam as iam
import aws_cdk.aws_s3_assets as s3_asset

dirname = os.path.dirname(__file__)

class PythonStack(core.Stack): 

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # The code that defines your stack goes here
        
        ## 1/ CREATE NEW VPC
        vpc = ec2.Vpc(self,
        "devExVPC",
        nat_gateways=0,
        subnet_configuration=[ec2.SubnetConfiguration(name="devExPublic",subnet_type=ec2.SubnetType.PUBLIC)])

        ## 2/ CONFIGURE AMI FOR EC2 INSTANCE 
        amzn_linux = ec2.MachineImage.latest_amazon_linux(
            generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
            edition=ec2.AmazonLinuxEdition.STANDARD,
            virtualization=ec2.AmazonLinuxVirt.HVM,
            storage=ec2.AmazonLinuxStorage.GENERAL_PURPOSE
            )

        ## 3/ CREATE EC2 INSTANCE    
        ec2_instance = ec2.Instance(self,"devExInstance",
        instance_type=ec2.InstanceType("t2.micro"),
        machine_image=amzn_linux,
        vpc=vpc
        )

        ## 4/ Script in S3 as Asset
        asset = s3_asset.Asset(self, "Asset", path=os.path.join(dirname, "configure.sh"))
        local_path = ec2_instance.user_data.add_s3_download_command(
            bucket=asset.bucket,
            bucket_key=asset.s3_object_key
        )

        ## 5/ Userdata executes script from S3
        ec2_instance.user_data.add_execute_file_command(
            file_path=local_path
            )
        asset.grant_read(ec2_instance.role)

        ## 6/ UPDATE SECURITY GROUP ALLOW ANY IP ACCESS PORT 80
        ec2_instance.connections.allow_from_any_ipv4(
            ec2.Port.tcp(80), "Allow http from internet")

        ## 7/ LOG OUT INSTANCE IPV4
        core.CfnOutput(self, "Output",
                       value=ec2_instance.instance_public_ip)