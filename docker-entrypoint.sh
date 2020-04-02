#!/bin/bash
set -e

if [ -f /run/secrets/aws_access_key ]; then
    export AWS_ACCESS_KEY_ID=$(cat /run/secrets/aws_access_key)
fi

if [ -f /run/secrets/aws_secret_access_key ]; then
    export AWS_SECRET_ACCESS_KEY=$(cat /run/secrets/aws_secret_access_key)
fi

if [ -f /run/secrets/aws_region ]; then
    export AWS_DEFAULT_REGION=$(cat /run/secrets/aws_region)
fi

if [ -f /run/secrets/aws_dynamo_table ]; then
    export AWS_DYNAMO_TABLE=$(cat /run/secrets/aws_dynamo_table)
fi

if [ -f /run/secrets/ocean_user ] && [ -f /run/secrets/ocean_pass ]; then
    creds=("--rpcuser=$(cat /run/secrets/ocean_user)" "--rpcpassword=$(cat /run/secrets/ocean_pass)")
elif [ -f /run/secrets/ocean_pass ]; then
    creds=("--rpcpass=$(cat /run/secrets/ocean_pass)")
fi

exec "$@" "${creds[@]}"
