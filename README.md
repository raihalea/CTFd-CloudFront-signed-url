# CTFd-CloudFront-Signed-URL Plugin
This plugin enables CTFd to generate signed URLs for objects stored in S3, redirecting clients through CloudFront. This leverages CloudFront's capabilities to securely and efficiently distribute content globally.

## Setup

### Requirements
- CTFd version 3.7.0 or later.

### Installation
Clone this repository into the `CTFd/plugins/` directory.

### Required Environment Variables
- `AWS_S3_BUCKET`: Name of the S3 bucket.
  - Example: `bucket-name`
- `AWS_S3_CUSTOM_PREFIX`: Used to resolve the path disparity between CloudFront and S3. This should be a unique path not overlapping with other configurations.
  - Example: `files/s3/`
- `AWS_CF_PUBLIC_KEY_ID`: The Key ID associated with the CloudFront distribution's public key.
  - Example: `K3P1AK7ASAMPLE`
- `AWS_S3_CUSTOM_DOMAIN`: The domain name of the CloudFront distribution.
  - Example: `example.com`

Additionally, one of the following is required for private key configuration:
- `AWS_CF_PRIVATE_KEY`: Direct input of the private key, starting with `-----BEGIN PRIVATE KEY-----` and ending with `-----END PRIVATE KEY-----`.
- `AWS_CF_PRIVATE_KEY_SSM_PARAM`: The name of the SSM Parameter storing the private key (not the ARN). Adequate IAM permissions are necessary for CTFd to access this parameter from SSM.

### CloudFront Configuration
To utilize CloudFront with CTFd, follow these general guidelines. For comprehensive details, refer to the AWS documentation at [https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/private-content-task-list.html](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/private-content-task-list.html).
- Register the public key with CloudFront and create a Key Group containing it.
- Specify both CTFd (as the default behavior) and S3 as origins.
- Set up an additional path pattern matching `AWS_S3_CUSTOM_PREFIX` with a wildcard (e.g., `files/s3/*`) and designate Trusted Key Groups for viewer access control.
- Adopt the S3-recommended `CachingOptimized` cache policy.
