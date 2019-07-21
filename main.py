from api.rekognition import Rekognition

collection_id = 'sample'

rek = Rekognition()
# rek.create_collection(collection_id=collection_id)
rek.list_collections()
rek.describe_collection(collection_id)
