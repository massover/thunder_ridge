# Thunder Ridge

A lambda function to run on SES Emails using [python lambda](https://github.com/nficano/python-lambda)

## Quickstart

```
git clone https://github.com/massover/thunder_ridge.git
make develop
make test
```

## Deploy

```
make deploy
```

## AWS Configuration

Lambda requires an `IAM` `role` with the following policies

- AmazonS3FullAccess
- AmazonSESFullAccess
- AWSLambdaBasicExecutionRole