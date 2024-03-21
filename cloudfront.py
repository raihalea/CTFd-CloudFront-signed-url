import os
import datetime

from flask import redirect
from CTFd.utils import uploads
from CTFd.utils.uploads.uploaders import S3Uploader

import boto3
from botocore.signers import CloudFrontSigner

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding


class S3UploaderWithCF(S3Uploader):

    def __init__(self):
        super().__init__()
        self.s3 = self._get_s3_connection()
        self.bucket = os.getenv("AWS_S3_BUCKET")
        custom_prefix = os.getenv("AWS_S3_CUSTOM_PREFIX")
        if custom_prefix and custom_prefix.endswith("/") is False:
            custom_prefix += "/"
        self.s3_prefix: str = custom_prefix

        self.cf_key_id = os.getenv("AWS_CF_PUBLIC_KEY_ID")
        self.custom_domain = os.getenv("AWS_S3_CUSTOM_DOMAIN")
        self.ssm = self._get_ssm_connection()
        self.private_key = self._load_private_key()
        self.cloudfront_signer = CloudFrontSigner(self.cf_key_id, self._rsa_signer)

    def _get_ssm_connection(self):
        client = boto3.client("ssm")
        return client

    def _load_private_key(self):
        # Directly insert PrivateKey in environment variable
        private_key = os.getenv("AWS_CF_PRIVATE_KEY")
        if private_key:
            return private_key

        # Insert the name of the SSM parameter that contains the PrivateKey into an environment variable
        private_key_param = os.getenv("AWS_CF_PRIVATE_KEY_SSM_PARM")
        if private_key_param:
            res = self.ssm.get_parameter(Name=private_key_param, WithDecryption=True)
            return res["Parameter"]["Value"]

    def _rsa_signer(self, message):
        private_key = serialization.load_pem_private_key(
            self.private_key.encode(), password=None, backend=default_backend()
        )
        return private_key.sign(message, padding.PKCS1v15(), hashes.SHA1())

    def download(self, filename):
        expire_time = datetime.datetime.now() + datetime.timedelta(hours=1)
        filename = os.path.join(self.s3_prefix, filename)
        url = f"https://{self.custom_domain}/{filename}"
        signed_url = self.cloudfront_signer.generate_presigned_url(
            url, date_less_than=expire_time
        )
        return redirect(signed_url)


def load(app):
    uploads.UPLOADERS.update({"s3withcf": S3UploaderWithCF})
