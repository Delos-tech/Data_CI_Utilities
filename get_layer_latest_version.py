"""
__author__=sshasan
__project__=DelosDataPlatform
"""

import boto3
import argparse


def get_latest_version(layer_name, arn=False):
    """
    Extracts the latest version of the a lambda layer. This uses the AWS default profile present in the environment.
    :param layer_name: Name of the lambda layer to extract latest version from.
    :param arn: Boolean indicating whether to return the version number as part of the ARN (True) or
    just the version number.
    :return: The version number if the query to AWS was successful, otherwise returns -1.
    """
    try:
        client = boto3.client('lambda')
        response = client.list_layer_versions(LayerName=layer_name, MaxItems=1)
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            version_info = response['LayerVersions'][0]['LayerVersionArn'] if arn else \
                response['LayerVersions'][0]['Version']
            return version_info
        else:
            raise Exception('There was an error getting the latest version number')
    except:
        return -1


if __name__ == "__main__":
    parser = argparse.ArgumentParser('Get the latest version number for a lambda layer')
    parser.add_argument('--layer', help='Layer name', required=True)
    parser.add_argument('--arn', help='Return the full ARN', action='store_true')
    args = parser.parse_args()
    print(get_latest_version(args.layer, arn=args.arn))
