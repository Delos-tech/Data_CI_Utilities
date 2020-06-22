#!/bin/bash

:'
  author: sshasan
  project: 
  purpose: 
    1. This script installs awscli, 
    2. then creates the required aws cli folder (.aws), the credentials file, and the config file
    3. populates the files with the required values (all environment variables are expected to be present)
'
pip install awscli

echo "Creating the folder"
mkdir ~/.aws

echo "Creating the required files"
touch ~/.aws/credentials ~/.aws/config

echo "Populating the files"
echo "[default]" | tee -a ~/.aws/credentials ~/.aws/config
echo "aws_access_key_id=$AWS_ACCESS_KEY_ID" >> ~/.aws/credentials
echo "aws_secret_access_key=$AWS_SECRET_ACCESS_KEY" >> ~/.aws/credentials
echo "region=us-east-2" >> ~/.aws/config
