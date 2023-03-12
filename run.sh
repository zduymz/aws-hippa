#!/usr/bin/env bash


usage() {
  echo "Usage: run.sh <stack_name> <management_vpc_cidr> <production_vpc_cdir> <aws_config_arn>"
}

if [ -z "$1" ]; then
    echo "Miss management vpc cidr"
    usage
    exit 1
fi

if [ -z "$2" ]; then
    echo "Miss management vpc cidr"
    usage
    exit 1
fi

if [ -z "$3" ]; then
    echo "Miss production vpc cidr"
    usage
    exit 1
fi

if [ -z "$4" ]; then
    echo "Miss AWSConfigARN"
    usage
    exit 1
fi

# if [ -z "$5" ]; then
#     echo "Miss Prefix"
#     usage
#     exit 1
# fi

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

STACK_NAME="$1"
python3 subnet-divider.py $2 $3 $4 "arn:aws:iam::421987627244:role/aws-service-role/config.amazonaws.com/AWSServiceRoleForConfig"

if [ $? -ne 0 ]; then
  exit 1
fi

echo "Creating stack..."
STACK_ID=$( \
  aws cloudformation create-stack \
  --stack-name ${STACK_NAME} \
  --template-url "https://cft-hipaa-automation-us-east-1.s3.amazonaws.com/quickstart-compliance-hipaa/templates/compliance-hipaa-second-entrypoint.template.yaml" \
  --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
  --parameters file://${DIR}/parameters.json )

echo "Waiting on ${STACK_ID} create completion..."
aws cloudformation wait stack-create-complete --stack-name ${STACK_NAME}
aws cloudformation describe-stacks --stack-name ${STACK_NAME} | jq .Stacks[0].Outputs

