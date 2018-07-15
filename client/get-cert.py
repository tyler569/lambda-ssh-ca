#!/usr/bin/env python3

import sys, os, base64, datetime, hashlib, hmac 
import requests
import json

# AWS request variables
method = 'POST'
service = 'execute-api'
host = os.environ.get("AWS_SSHCA_HOST")
region = os.environ.get("AWS_SSHCA_REGION")
endpoint = os.environ.get("AWS_SSHCA_ENDPOINT")
request_parameters = ''
canonical_uri = os.environ.get("AWS_SSHCA_URI")

if (not host or not region or not endpoint or not canonical_uri):
    print("host, region, endpoint, and uri need to be set")
    print("Have you edited the example ca_credentials.sh to match your")
    print("AWS setup and sourced it into your terminal?")
    exit(1)

# Adapted from https://docs.aws.amazon.com/general/latest/gr/sigv4-signed-request-examples.html

def sign(key, msg):
    return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

def get_aws_signature_key(key, dateStamp, regionName, serviceName):
    kDate = sign(('AWS4' + key).encode('utf-8'), dateStamp)
    kRegion = sign(kDate, regionName)
    kService = sign(kRegion, serviceName)
    kSigning = sign(kService, 'aws4_request')
    return kSigning

def get_certificate(pubkey_filename):
    access_key = os.environ.get('AWS_SSHCA_ACCESS_KEY_ID')
    secret_key = os.environ.get('AWS_SSHCA_SECRET_ACCESS_KEY')
    if access_key is None or secret_key is None:
        print('No access key is available.')
        sys.exit()

    t = datetime.datetime.utcnow()
    amzdate = t.strftime('%Y%m%dT%H%M%SZ')
    datestamp = t.strftime('%Y%m%d')

    canonical_querystring = request_parameters
    canonical_headers = 'host:' + host + '\n' + 'x-amz-date:' + amzdate + '\n'
    signed_headers = 'host;x-amz-date'

    with open(pubkey_filename) as pubkey_file:
        pubkey = pubkey_file.read()
    payload = json.dumps({
        "pubkey": pubkey
    }).encode()

    payload_hash = hashlib.sha256(payload).hexdigest()

    canonical_request = (
        method + '\n' + canonical_uri + '\n' + canonical_querystring + '\n' +
        canonical_headers + '\n' + signed_headers + '\n' + payload_hash
    )
    canonical_request = canonical_request.encode()

    algorithm = 'AWS4-HMAC-SHA256'
    credential_scope = datestamp + '/' + region + '/' + service + '/' + 'aws4_request'
    string_to_sign = (
        algorithm + '\n' +  amzdate + '\n' +  credential_scope + '\n' +
        hashlib.sha256(canonical_request).hexdigest()
    )

    signing_key = get_aws_signature_key(secret_key, datestamp, region, service)
    signature = hmac.new(signing_key, (string_to_sign).encode('utf-8'), hashlib.sha256).hexdigest()

    authorization_header = (
        algorithm + ' ' + 'Credential=' + access_key + '/' + credential_scope +
        ', ' +  'SignedHeaders=' + signed_headers + ', ' + 'Signature=' + signature
    )
    headers = {'x-amz-date':amzdate, 'Authorization':authorization_header}
    request_url = endpoint + '?' + canonical_querystring

    r = requests.post(request_url, headers=headers, data=payload)
    j = json.loads(r.text)
    if "cert" in j:
        return j["cert"]
    else:
        print(j)
        return None

def main():
    pubkey_file = os.environ.get("SSH_PUBLIC_KEY")
    # For now this just prints the certificate, more work is needed to properly use this
    print(get_certificate(pubkey_file))

if __name__ == "__main__":
    main()

