#!/usr/bin/env bash
echo "Installing the required testing packages"
pip install -r requirements.txt
pip install pytest
pip install coverage

echo "Setting up the AWS environment"
wget https://raw.githubusercontent.com/Delos-tech/Data_CI_Utilities/master/src/create_aws_environment.sh -O create_aws_environment.sh
chmod +rx create_aws_environment.sh
bash create_aws_environment.sh
rm create_aws_environment.sh

echo "Getting the staging file"
wget https://raw.githubusercontent.com/Delos-tech/Data_CI_Utilities/master/src/staging.sh -O staging.sh
chmod +rx staging.sh
