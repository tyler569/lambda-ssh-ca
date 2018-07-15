import json
import subprocess
import boto3
import os

def create_res(status, body):
    res = {
        "statusCode": status,
        "headers": {},
        "body": json.dumps(body),
        "isBase64Encoded": False
    }
    return res

def lambda_handler(event, context):
    os.umask(0o177)
    s3 = boto3.client('s3')
    bucket_name = os.environ["KEY_BUCKET"]
    object_name = os.environ["KEY_OBJECT"]
    pubkey = json.loads(event["body"])["pubkey"]

    if not pubkey:
        return create_res(400, {"error": "no client credential provided"})

    try:
        obj = s3.get_object(Bucket=bucket_name, Key=object_name)
        key = obj['Body'].read().decode('utf-8')
    except Exception as e:
        return create_res(500, {
            "error": "could not retrieve key object from s3",
            "message": repr(e)
        })

    with open("/tmp/ca", "w") as ca:
        ca.write(key)
    with open("/tmp/client", "w") as client:
        client.write(pubkey)

    gen = 0
    try:
        gen = subprocess.check_output(
            "./ssh-keygen -s /tmp/ca -I testing -V +30m /tmp/client; exit 0",
            stderr=subprocess.STDOUT, shell=True
        ).decode()
    except Exception as e:
        return create_res(500, {
            "error": "ssh-keygen failed",
            "message": repr(e)
        })

    cert = ""
    with open("/tmp/client-cert.pub") as cert:
        cert = cert.read()

    return create_res(200, {
        "ssh-keygen": gen,
        "cert": cert
    })
