import hashlib

from api.rekognition import Rekognition
from api.s3 import S3

collection_id = 'sample'
region = 'ap-northeast-1'
bucket = 'keyfun-' + region + '-rekognition-sample'
sample = 'samples/sample_001.jpg'
image_id = hashlib.md5(sample.encode()).hexdigest()

rek = Rekognition()
s3 = S3(region=region)

# rek.create_collection(collection_id=collection_id)
# s3.create_bucket(bucket)
# s3.upload_file(bucket, sample, image_id)

# rek.detect_faces(bucket=bucket, photo=image_id)
# rek.add_faces_to_collection(collection_id, bucket=bucket, photo=image_id)
# rek.search_faces_by_image_collection(collection_id, bucket, image_id)

rek.list_collections()
rek.describe_collection(collection_id)

