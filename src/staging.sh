#!/usr/bin/env bash

function usage(){
    echo "Usage: $0 [-e MODE - test/deploy] [-f FUNCTION_NAME] [-r RUNTIME] [-a ROLE] \
        [-d HANDLER (MODULE_NAME.FUNCTION_NAME)] [-t TIMEOUT IN SECONDS] [-m MEMORY IN MB] \
        [-l LAYERS AS A LIST IN QUOTES] [-v VPC SUBNETS AS A LIST IN QUOTES] \
        [-s VPC SECURITY GROUPS AS A LIST IN QUOTES][-o OUTPUT FILE FOR LAMBDA CONFIG] [-h HELP]"
    exit 2
}

function check_update_success(){
    if cat $1 | grep -q "\"LastUpdateStatus\": \"Successful\""; then
        return 1
    elif cat $1 | grep -q "\"LastUpdateStatus\": \"InProgress\""; then
        return 1
    elif cat $1 | grep -q "\"Status\": \"Pending\""; then
        return 1
    elif cat $1 | grep -q "\"Status\": \"Active\""; then
        return 1
    else
        return 0
    fi
}

while getopts "e:f:r:a:d:t:m:l:v:s:o:?h" c
do
    case $c in
    e) VAR_MODE=$OPTARG ;;
    f) VAR_FUNC_NAME=$OPTARG ;;
    r) VAR_RUNTIME=$OPTARG ;;
    a) VAR_ROLE=$OPTARG ;;
    d) VAR_HANDLER=$OPTARG ;;
    t) VAR_TIMEOUT=$OPTARG ;;
    m) VAR_MEMORY=$OPTARG ;;
    l) VAR_LAYERS=$OPTARG ;;
    v) VAR_SUBNETS=$OPTARG ;;
    s) VAR_SECURITY_GROUPS=$OPTARG ;;
    o) VAR_OUTPUT=$OPTARG ;;
    h|?) usage ;;
    esac
done

if [[ "$VAR_MODE" == "test" ]]; then
    bash basic_setup.sh
    cd src
    coverage run -m pytest ../tests/
elif [[ "$VAR_MODE" == "deploy" ]]; then
    echo "DEPLOY: Checking folder and zipping files"
    if pwd | grep -q "src"; then
        echo "In the source folder"
    else
        echo "Changing directory to src"
        cd src
    fi

    zip -r ../my_lambda_func.zip *.py
    cd ../

    echo "DEPLOY: Getting the AWS lambda related files"
    wget https://raw.githubusercontent.com/Delos-tech/Data_CI_Utilities/master/src/create_lambda_deployment_json.py \
        -O create_lambda_deployment_json.py
    wget https://raw.githubusercontent.com/Delos-tech/Data_CI_Utilities/master/src/check_lambda_function_exists.py \
        -O check_lambda_function_exists.py

    echo "DEPLOY: Creating the config json: lambda_config.json"
    python create_lambda_deployment_json.py --function ${VAR_FUNC_NAME} \
        --runtime ${VAR_RUNTIME} \
        --role ${VAR_ROLE} \
        --handler ${VAR_HANDLER} \
        --description "Deploy build $TRAVIS_BUILD_NUMBER to AWS Lambda via Travis CI" \
        --timeout ${VAR_TIMEOUT} \
        --memory ${VAR_MEMORY} \
        --layers ${VAR_LAYERS}  \
        --vpc-subnets ${VAR_SUBNETS} \
        --vpc-security-groups ${VAR_SECURITY_GROUPS} \
        --output ${VAR_OUTPUT}

    echo "DEPLOY: Checking existence of lambda"
    python check_lambda_function_exists.py --function ${VAR_FUNC_NAME}
    function_exists=$(cat function_exists.txt)
    if [[ "$function_exists" == "1" ]]; then
        echo "DEPLOY: Function already exists, updating the code and configuration"
        aws lambda update-function-code --function-name ${VAR_FUNC_NAME} \
            --zip-file fileb://my_lambda_func.zip --no-publish >> update_function.json
        check_update_success update_function.json
        if [[ "$?" == 1 ]]; then
            echo "DEPLOY: The code update was successful, updating the configuration. The following is being used: "
            # delete the publish term from the configuration file
            sed 's/"Publish": false,//g' lambda_config.json >> lambda_config_update.json
            cat lambda_config_update.json
            aws lambda update-function-configuration \
                --cli-input-json file://lambda_config_update.json >> update_config.json
            # check condition
            check_update_success update_config.json
            if [[ "$?" == 1 ]]; then
                echo "DEPLOY: The configuration update was successful";
                exit 0
            else
                echo "DEPLOY: The configuration update failed."
                cat update_config.json
                exit 1
            fi
        else
            echo "DEPLOY: The update code failed."
            echo update_function.json
            exit 1
        fi
    elif [[ "$function_exists" == "0" ]]; then
        echo "DEPLOY: Function does not exist. Creating a new one"
        aws lambda create-function --cli-input-json file://lambda_config.json \
            --zip-file fileb://my_lambda_func.zip >> create_function.json
        check_update_success create_function.json
        if [[ "$?" == 1 ]]; then
                echo "DEPLOY: Function creation was successful";
                exit 0
        else
            echo "DEPLOY: The function creation failed."
            cat create_function.json
            exit 1
        fi
    elif [[ "$function_exists" == "-1" ]]; then
        echo "DEPLOY: There was an error in checking the existence"
        exit 1
    fi
fi