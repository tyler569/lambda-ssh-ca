## Lambda SSH CA

This is a very simple implementation of an SSH CA in AWS lambda

### Usage:

- Deploy the lambda_function folder to AWS Lambda
  - The folder includes a couple of binaries that are required dependancies (ssh-keygen and libfipscheck) that should continue to work as long as the lambda runtime is based on the 201703 Amazon Linux AMI.
  - If the lambda environment changes, these dependancies will likely need to be updated, since the lambda environment does not include any SSH binaries.
- Create an AWS API gateway and set it to back to the Lambda function
- Upload an ssh keypair to S3 in a secured bucket.
- Give the IAM user the Lambda function is running as read-only access to that bucket
- Add the bucket name and file name as environment variables in the Lambda function (KEY_BUCKET and KEY_OBJECT)


- Edit ca_credentials.sh with your AWS credentials, region, and API gateway URL.
- The client needs requests installed, which can be installed through pip globally or in a virtualenv.

### Notes:

- I reccomend giving the function ~512MB of RAM, since Lambda allocates CPU and network resources proportional to the RAM amount, and 512MB seemed to be the sweet spot for speed.  Since Lambda charges for the GB\*second, 128MB\*1.5 seconds costs more than 512MB\*0.2 seconds.

