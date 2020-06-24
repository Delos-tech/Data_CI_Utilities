import unittest
import os
from unittest.mock import patch
from src.check_lambda_function_exists import check_lambda_exists


class MyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.aws_credentials = {
            'aws_key': os.environ.get('AWS_ACCESS_KEY_ID'),
            'aws_secret': os.environ.get('AWS_SECRET_ACCESS_KEY'),
            'region': 'us-east-2'
        }
        self.aws_credentials_incorrect = {'aws_key': '123', 'aws_secret': 'abc', 'region': 'mars-trinity-1'}

    def test_check_lambda_exists_correct(self):
        correct_value = 1
        function_name = 'data_domotz_api'
        with patch('builtins.print') as _:
            response = check_lambda_exists(function_name=function_name, credentials=self.aws_credentials)
            self.assertEqual(correct_value, response)

    def test_check_lambda_exists_incorrect_function_name(self):
        correct_value = 0
        function_name = 'incorrectfunction'
        with patch('builtins.print') as _:
            response = check_lambda_exists(function_name=function_name, credentials=self.aws_credentials)
            self.assertEqual(correct_value, response)

    def test_check_lambda_exists_incorrect_credentials(self):
        correct_value = -1
        function_name = 'data_domotz_api'
        with patch('builtins.print') as _:
            response = check_lambda_exists(function_name=function_name, credentials=self.aws_credentials_incorrect)
            self.assertEqual(correct_value, response)

