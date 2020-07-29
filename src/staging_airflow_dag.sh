#!/usr/bin/env bash

function usage(){
    echo "Usage $0 [-m MODE test/deploy][-z ZIP FILE NAME] [-e SERVER PATH] [-u SERVER USERNAME] \
            [-d SERVER UPLOAD DIRECTORY] [-k SERVER PEM FILE] [-h HELP]"
    exit 2
}

while getopts "z:e:u:d:k:?h" c
do
    case ${c} in
    m) VAR_MODE=$OPTARG ;;
    z) VAR_ZIP_FILE=$OPTARG ;;
    e) VAR_SERVER_URL=$OPTARG ;;
    u) VAR_SERVER_USER=$OPTARG ;;
    d) VAR_SERVER_UPLOAD_DIR=$OPTARG ;;
    k) VAR_SERVER_PEM=$OPTARG ;;
    h|?) usage ;;
    esac
done

if [[ "$VAR_MODE" == "test" ]]; then
    echo "[TEST] Running the basic setup"
    bash basic_setup.sh
    echo "[TEST] Changing the directory to src and running the tests"
    cd src
    coverage run -m pytest ../tests/

elif [[ "$VAR_MODE" == "deploy" ]]; then
    echo "[DEPLOY] Checking if I am still in the src folder"
    if pwd | grep -q "src"; then
        echo "In the src folder"
    else
        echo "Changing directory to src"
        cd src
    fi
    echo "[DEPLOY] zipping the code"
    zip -r "../$VAR_ZIP_FILE" .
    cd ../

    echo "[DEPLOY] deploying the file to the airflow server"
    echo "scp -i \"$VAR_SERVER_PEM\" $VAR_ZIP_FILE ${VAR_SERVER_USER}@${VAR_SERVER_URL}:\"$VAR_SERVER_UPLOAD_DIR\"" | bash
    if [[ "$?" == "0" ]]; then
        echo "[DEPLOY] deployment successful"
        exit 0
    else
        echo "[DEPLOY] There was an error in the deployment"
        exit 1
     fi
else
    echo "incorrect usage";
    usage
fi