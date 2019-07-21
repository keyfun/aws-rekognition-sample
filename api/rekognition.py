import json

import boto3
from botocore.exceptions import ClientError


class Rekognition:
    client = boto3.client('rekognition')

    def list_collections(self):
        max_results = 2

        # Display all the collections
        print('Displaying collections...')
        response = self.client.list_collections(MaxResults=max_results)

        while True:
            collections = response['CollectionIds']

            for collection in collections:
                print(collection)
            if 'NextToken' in response:
                next_token = response['NextToken']
                response = self.client.list_collections(NextToken=next_token, MaxResults=max_results)

            else:
                break
        print('done...')

    def describe_collection(self, collection_id):
        print('Attempting to describe collection ' + collection_id)

        try:
            response = self.client.describe_collection(CollectionId=collection_id)
            print("Collection Arn: " + response['CollectionARN'])
            print("Face Count: " + str(response['FaceCount']))
            print("Face Model Version: " + response['FaceModelVersion'])
            print("Timestamp: " + str(response['CreationTimestamp']))

        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                print('The collection ' + collection_id + ' was not found ')
            else:
                print('Error other than Not Found occurred: ' + e.response['Error']['Message'])
        print('Done...')

    def create_collection(self, collection_id):
        # Create a collection
        print('Creating collection:' + collection_id)

        response = self.client.create_collection(CollectionId=collection_id)

        print('Collection ARN: ' + response['CollectionArn'])
        print('Status code: ' + str(response['StatusCode']))
        print('Done...')

    def delete_collection(self, collection_id):
        print('Attempting to delete collection ' + collection_id)
        try:
            response = self.client.delete_collection(CollectionId=collection_id)
            status_code = response['StatusCode']

        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                print('The collection ' + collection_id + ' was not found ')
            else:
                print('Error other than Not Found occurred: ' + e.response['Error']['Message'])
            status_code = e.response['ResponseMetadata']['HTTPStatusCode']
        print('Operation returned Status Code: ' + str(status_code))
        print('Done...')

    # TODO: support multiple photos
    def add_faces_to_collection(self, collection_id, bucket, photo):
        response = self.client.index_faces(
            CollectionId=collection_id,
            Image={'S3Object': {'Bucket': bucket, 'Name': photo}},
            ExternalImageId=photo,
            MaxFaces=1,
            QualityFilter="AUTO",
            DetectionAttributes=['ALL'])

        print('Results for ' + photo)
        print('Faces indexed:')
        for faceRecord in response['FaceRecords']:
            print('  Face ID: ' + faceRecord['Face']['FaceId'])
            print('  Location: {}'.format(faceRecord['Face']['BoundingBox']))

        print('Faces not indexed:')
        for unindexed_face in response['UnindexedFaces']:
            print(' Location: {}'.format(unindexed_face['FaceDetail']['BoundingBox']))
            print(' Reasons:')
            for reason in unindexed_face['Reasons']:
                print('   ' + reason)

    # TODO: support multiple faces
    def delete_faces_to_collection(self, collection_id, face_id):
        faces = [face_id]

        response = self.client.delete_faces(
            CollectionId=collection_id,
            FaceIds=faces)

        print(str(len(response['DeletedFaces'])) + ' faces deleted:')
        for faceId in response['DeletedFaces']:
            print(faceId)

    def detect_faces(self, bucket, photo):
        response = self.client.detect_faces(Image={'S3Object': {'Bucket': bucket, 'Name': photo}}, Attributes=['ALL'])

        print('Detected faces for ' + photo)
        for face_detail in response['FaceDetails']:
            print('The detected face is between ' + str(face_detail['AgeRange']['Low'])
                  + ' and ' + str(face_detail['AgeRange']['High']) + ' years old')
            print('Here are the other attributes:')
            print(json.dumps(face_detail, indent=4, sort_keys=True))

    def list_faces_in_collection(self, collection_id):
        max_results = 2
        tokens = True

        response = self.client.list_faces(
            CollectionId=collection_id,
            MaxResults=max_results)

        print('Faces in collection ' + collection_id)

        while tokens:

            faces = response['Faces']

            for face in faces:
                print(face)
            if 'NextToken' in response:
                next_token = response['NextToken']
                response = self.client.list_faces(
                    CollectionId=collection_id,
                    NextToken=next_token,
                    MaxResults=max_results)
            else:
                tokens = False
