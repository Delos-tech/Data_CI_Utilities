"""
__author__=sshasan
__project__=DelosDataPlatform
"""

import boto3
import argparse
import traceback


def check_lambda_exists(function_name: str, credentials: dict = None) -> int:
    """
    Checks whether a function_name exists as a lambda function
    :param function_name: String with the function name
    :param credentials: AWS credentials to use, can be None (uses default). Expected in the following form:
    {
        "aws_key": <aws access key id>,
        "aws_secret": <aws_secret_access_key>,
        "region": <AWS region>
    }
    :return: 0 if function does not exist, 1 if it does, -1 when there was an error
    """
    try:
        client = boto3.client('lambda') if not credentials else \
            boto3.client('lambda',
                         aws_access_key_id=credentials['aws_key'],
                         aws_secret_access_key=credentials['aws_secret'],
                         region_name=credentials['region'])
        response = client.get_function(FunctionName=function_name)
        if function_name in response['Configuration']['FunctionName']:
            print('Found the function')
            return 1
        else:
            print('Could not find the function')
            return 0
    except Exception as e:
        if 'ResourceNotFound' in str(e):
            print('Could not find function')
            return 0
        else:
            print(f'There was an exception. \n{traceback.format_exc()}')
            return -1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--function', help='Name of the function to check', required=True)
    parser.add_argument('--access', help='AWS Access Key ID', default=None)
    parser.add_argument('--secret', help='AWS Secret Key', default=None)
    parser.add_argument('--region', help='AWS Region', default='us-east-2')

    args = parser.parse_args()

    aws_credentials = None
    if args.access is not None and args.secret is not None:
        aws_credentials = {
            'aws_key': args.access,
            'aws_secret': args.secret,
            'region': args.region
        }

    print(check_lambda_exists(args.function, aws_credentials))