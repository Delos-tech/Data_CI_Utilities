"""
__author__=sshasan
__project__=DelosDataPlatform
"""

import boto3
import argparse
import json
import traceback


def get_iam_role_arn(role_name: str, credentials: dict = None) -> str:
    """
    Extracts the ARN of the IAM role specified.
    :param role_name: String with the name of the role
    :param credentials: The aws credentials in the form of
    {
        "aws_key": <aws access key id>,
        "aws_secret": <aws_secret_access_key>,
        "region": <aws region>
    }
    can be None (in which case the default shall be used)
    :return: string with the ARN of the role, empty string represents an error.
    """
    try:
        print('Setting up the AWS connection')
        if role_name is None or role_name == '':
            raise Exception('Role name not defined')
        iam = boto3.client('iam') if not credentials else \
            boto3.client('iam', aws_access_key_id=credentials['aws_key'],
                         aws_secret_access_key=credentials['aws_secret'], region_name=credentials['region'])
        print('Getting the role')
        response = iam.get_role(RoleName=role_name)
        if 'Role' not in response:
            raise Exception('Role was not in the response')
        print('Returning the ARN')
        return response['Role']['Arn']
    except:
        print(f'There was an error in getting the ARN. \n{traceback.format_exc()}')
        return ''


def get_lambda_layer_latest_version(layer_name: str, credentials: dict = None, aws_client=None) -> tuple:
    """
    Extracts the latest version of the a lambda layer.
    :param layer_name: Name of the lambda layer to extract latest version from.
    :param credentials: The aws credentials in the form of
    {
        "aws_key": <aws access key id>,
        "aws_secret": <aws_secret_access_key>,
        "region": <AWS region>
    }
    can be None (in which case the default shall be used)
    :param aws_client: Boto3 client that can be reused. If None, a new client is created.
    :returns Tuple with first element as the layer ARN (empty if there is an error), and the second element the boto3
    client (None if an error has occured)
    """
    try:
        if layer_name is None or layer_name == '':
            raise Exception('Layer name not present')

        print('Setting up the AWS connection')
        if aws_client is None:
            aws_client = boto3.client('lambda') if not credentials else \
                boto3.client('lambda', aws_access_key_id=credentials['aws_key'],
                             aws_secret_access_key=credentials['aws_secret'], region_name=credentials['region'])
        print('Getting the layer ARN')
        response = aws_client.list_layer_versions(LayerName=layer_name, MaxItems=1)
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            version_info = response['LayerVersions'][0]['LayerVersionArn']
            return version_info, aws_client
        else:
            raise Exception('Status code was not 200.')
    except:
        print(f'There was an error getting the layer ARN. \n{traceback.format_exc()}')
        return '', None


def create_json(function_name: str, runtime: str, role: str, handler: str, description: str,
                timeout: int = 3, memory_size: int = 128, publish: bool = False, lambda_layers: list = None,
                tags: dict = None, vpc_subnets: list = None, vpc_security_groups: list = None) -> dict:
    """
    Create the JSON that the aws lambda create-function --cli-input-json will take
    :param function_name: The name of the Lambda function to display
    :param runtime: The runtime for the function eg. python3.7
    :param role: The ARN of the role to use for the lambda function
    :param handler: The handler within the function that executes. Should be of the format <module_name>.<handler>
    :param description: The description for the lambda function
    :param timeout: The timeout value in seconds. Default is 3.
    :param memory_size: The memory size for the lambda function. Default is 128
    :param publish: Do we want to publish a new version? Default is False.
    :param lambda_layers: List of ARNs of layers to include for the lambda.
    :param tags: Any tags that we might want to associate with the lambda. Form of a dictionary with
    <key_name>: <tag_value> format
    :param vpc_subnets: List of VPC subnets to associate with the lambda function.
    :param vpc_security_groups: List of security groups to associate with the VPC.
    :return: A JSON in the expected format. Returns an empty JSON in case of an error.
    """
    try:
        print('Running basic checks')
        if None in [function_name, runtime, role, handler]:
            raise Exception('One of the required variables are not available')
        if description is None or description == '':
            description = f'Lambda function: {function_name}'
        to_return = {
            "FunctionName": function_name,
            "Runtime": runtime,
            "Role": role,
            "Handler": handler,
            "Description": description,
            "Timeout": timeout,
            "MemorySize": memory_size,
            "Publish": publish,
            "VpcConfig": {
                "SubnetIds": [],
                "SecurityGroupIds": []
            }
        }
        if lambda_layers is not None:
            if len(lambda_layers) is not 0:
                to_return["Layers"] = lambda_layers
        if tags is not None:
            if len(tags) is not 0:
                to_return["Tags"] = tags
        if vpc_subnets is not None:
            if len(vpc_subnets) is not 0:
                to_return['VpcConfig']['SubnetIds'] = vpc_subnets
        if vpc_security_groups is not None:
            if len(vpc_security_groups) is not 0:
                to_return['VpcConfig']['SecurityGroupIds'] = vpc_security_groups
        return to_return
    except:
        print(f'There was an error. \n{traceback.format_exc()}')
        return {}


if __name__ == "__main__":
    try:
        print('Setting up the arguments')
        parser = argparse.ArgumentParser('Get the latest version number for a lambda layer')
        # add the arguments
        parser.add_argument('--function', help='The name of the Lambda function to display', required=True)
        parser.add_argument('--handler', help='The handler within the function that executes. '
                                              'Should be of the format <module_name>.<handler>', required=True)
        parser.add_argument('--runtime', help='The runtime for the function eg. python3.7', required=True)
        parser.add_argument('--role', help='The name of the role', required=True)
        parser.add_argument('--description', help='The description for the lambda function', default=None)
        parser.add_argument('--timeout', help='The timeout value in seconds. Default is 3.', type=int, default=3)
        parser.add_argument('--memory', help='The memory size for the lambda function', type=int, default=128)
        parser.add_argument('--publish', help='Do we want to publish a new version? Default is False.', type=bool,
                            default=False)
        parser.add_argument('--layers', help='Layer name(s), multiple names can be entered with spaces', nargs='+',
                            required=True)
        parser.add_argument('--vpc-subnets', help='VPC subnets to associate with the Lambda', nargs='+')
        parser.add_argument('--vpc-security-groups', help='VPC security groups to associate with the Lambda',
                            nargs='+')
        parser.add_argument('--tags', help='JSON file with tags', default=None)
        parser.add_argument('--access', help='AWS access key', default=None)
        parser.add_argument('--secret', help='AWS secret key', default=None)
        parser.add_argument('--region', help='AWS Region', default='us-east-2')
        parser.add_argument('--output', help='Create the output JSON for update-function-configuration', required=True)

        print('Parsing the arguments')
        args = parser.parse_args()

        print('Checking the ')
        aws_credentials = None
        if args.access is not None and args.secret is not None:
            aws_credentials = {
                'aws_key': args.access,
                'aws_secret': args.secret,
                'region': args.region
            }

        print('making checks for tags')
        tags = None
        if args.tags is not None:
            with open(args.tags, 'r') as f:
                tags = json.load(f)

        print('making checks for layers')
        if args.layers is not None:
            layers = []
            client = None
            for layer in args.layers:
                layer_arn, client = get_lambda_layer_latest_version(layer_name=layer, credentials=aws_credentials,
                                                                    aws_client=client)
                if layer_arn is not '':
                    layers.append(layer_arn)
                else:
                    raise Exception(f'The layer {layer} could not be found')
        print('Getting the role ARN')
        role_arn = get_iam_role_arn(role_name=args.role, credentials=aws_credentials)
        print('Creating the JSON')
        json_file = create_json(function_name=args.function, runtime=args.runtime, role=role_arn, handler=args.handler,
                                description=args.description, timeout=args.timeout, memory_size=args.memory,
                                publish=args.publish, lambda_layers=layers, tags=tags)
        print(f'Writing the JSON file: \n{json.dumps(json_file, indent=4)}')
        with open(args.output, 'w') as f:
            json.dump(obj=json_file, fp=f)
        print('Done')
    except:
        print(f'There was an error in the process. \n{traceback.format_exc()}')
