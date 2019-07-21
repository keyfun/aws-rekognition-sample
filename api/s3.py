import boto3


class S3:
    s3 = boto3.resource('s3')
    s3_buckets = 'rekognition-sample'

    def list_all_buckets(self):
        for bucket in self.s3.buckets.all():
            print(bucket.name)

    def upload(self, file):
        data = open(file, 'rb')
        self.s3.Bucket(self.s3_buckets).put_object(Key=file, Body=data)
