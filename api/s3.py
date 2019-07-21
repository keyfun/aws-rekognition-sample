import logging

import boto3
from botocore.exceptions import ClientError


class S3:
    client = None
    region = None

    def __init__(self, region=None):
        print(f'region={region}')
        self.region = region
        self.client = boto3.client('s3', region_name=region)

    def list_all_buckets(self):
        for bucket in self.client.bucket.all():
            print(bucket.name)

    def create_bucket(self, bucket_name, region=None):
        try:
            if region is None:
                location = {'LocationConstraint': self.region}
                self.client.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration=location)
            else:
                self.client = boto3.client('s3', region_name=region)
                location = {'LocationConstraint': region}
                self.client.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration=location)
        except ClientError as e:
            logging.error(e)
            return False
        return True

    def upload_file(self, bucket, file_name, object_name):
        if object_name is None:
            object_name = file_name
        try:
            self.client.upload_file(file_name, bucket, object_name)
        except ClientError as e:
            logging.error(e)
            return False
        return True
