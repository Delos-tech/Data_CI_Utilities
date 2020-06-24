import os
import unittest
from unittest.mock import patch
from src.create_lambda_deployment_json import get_iam_role_arn, get_lambda_layer_latest_version, create_json


class MyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.aws_credentials = {
            'aws_key': os.environ.get('AWS_ACCESS_KEY_ID'),
            'aws_secret': os.environ.get('AWS_SECRET_ACCESS_KEY'),
            'region': 'us-east-2'
        }
        self.aws_credentials_incorrect = {'aws_key': '123', 'aws_secret': 'abc', 'region': 'mars-trinity-1'}

    def test_get_iam_role_arn_correct_role(self):
        role_name = 'Data_Lambda_Full_Access'
        correct_arn = 'arn:aws:iam::157648923453:role/Data_Lambda_Full_Access'
        with patch('builtins.print') as _:
            response = get_iam_role_arn(role_name=role_name, credentials=self.aws_credentials)
            self.assertEqual(response, correct_arn)

    def test_get_iam_role_arn_incorrect_role(self):
        role_name = 'Incorrect_Lambda_Role'
        with patch('builtins.print') as _:
            response = get_iam_role_arn(role_name=role_name, credentials=self.aws_credentials)
            self.assertEqual(response, '')

    def test_get_iam_role_arn_incorrect_credentials(self):
        role_name = 'Data_Lambda_Full_Access'
        with patch('builtins.print') as _:
            response = get_iam_role_arn(role_name=role_name, credentials=self.aws_credentials_incorrect)
            self.assertEqual(response, '')

    def test_get_lambda_layer_latest_version_correct(self):
        layers = ['requests', 'jsonschema']
        correct_arns = [
            "arn:aws:lambda:us-east-2:157648923453:layer:requests:13",
            "arn:aws:lambda:us-east-2:157648923453:layer:jsonschema:3"
        ]
        acquired_arns = []
        client = None
        with patch('builtins.print') as _:
            for layer in layers:
                layer_arn, client = get_lambda_layer_latest_version(layer_name=layer, credentials=self.aws_credentials,
                                                                    client=client)
                acquired_arns.append(layer_arn)
            self.assertListEqual(acquired_arns, correct_arns)

    def test_get_lambda_layer_latest_version_incorrect_layers(self):
        layer = 'incorrectLayer'
        with patch('builtins.print') as _:
            layer_arn, client = get_lambda_layer_latest_version(layer_name=layer, credentials=self.aws_credentials)
            self.assertEqual('', layer_arn)
            self.assertIsNone(client)

    def test_get_lambda_layer_latest_version_incorrect_credentials(self):
        layer = 'requests'
        with patch('builtins.print') as _:
            layer_arn, client = get_lambda_layer_latest_version(layer_name=layer,
                                                                credentials=self.aws_credentials_incorrect)
            self.assertEqual('', layer_arn)
            self.assertIsNone(client)

    def test_create_json_correct(self):
        correct_json = dict(FunctionName="testFunc", Runtime="python3.7",
                            Role="arn:aws:iam::157648923453:role/Data_Lambda_Full_Access",
                            Handler="modulename.function_handler", Code={"ZipFile": "fileb://dummy.zip"},
                            Description="dummy description", Timeout=60, MemorySize=256, Publish=False,
                            Layers=[ "arn:aws:lambda:us-east-2:157648923453:layer:requests:13",
                                     "arn:aws:lambda:us-east-2:157648923453:layer:jsonschema:3"])
        with patch('builtins.print') as _:
            json_body = create_json(function_name="testFunc", runtime="python3.7",
                                    role="arn:aws:iam::157648923453:role/Data_Lambda_Full_Access",
                                    handler="modulename.function_handler", zip_file="dummy.zip",
                                    description="dummy description", timeout=60, memory_size=256,
                                    layers=[ "arn:aws:lambda:us-east-2:157648923453:layer:requests:13",
                                             "arn:aws:lambda:us-east-2:157648923453:layer:jsonschema:3"])
            self.assertDictEqual(correct_json, json_body)

    def test_create_json_incorrect(self):
        with patch('builtins.print') as _:
            json_body = create_json(function_name=None, runtime="python3.7",
                                    role="arn:aws:iam::157648923453:role/Data_Lambda_Full_Access",
                                    handler="modulename.function_handler", zip_file="dummy.zip",
                                    description="dummy description", timeout=60, memory_size=256,
                                    layers=["arn:aws:lambda:us-east-2:157648923453:layer:requests:13",
                                            "arn:aws:lambda:us-east-2:157648923453:layer:jsonschema:3"])
            self.assertEqual({}, json_body)


if __name__ == '__main__':
    unittest.main()
