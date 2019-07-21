import json

import boto3
from PIL import Image
from botocore.exceptions import ClientError

from api.utils import ShowBoundingBoxPositions


class Rekognition:
    client = boto3.client('rekognition')

    def compare_faces(self, source_file, target_file):
        image_source = open(source_file, 'rb')
        image_target = open(target_file, 'rb')

        response = self.client.compare_faces(
            SimilarityThreshold=70,
            SourceImage={'Bytes': image_source.read()},
            TargetImage={'Bytes': image_target.read()})

        for faceMatch in response['FaceMatches']:
            position = faceMatch['Face']['BoundingBox']
            confidence = str(faceMatch['Face']['Confidence'])
            print('The face at ' +
                  str(position['Left']) + ' ' +
                  str(position['Top']) +
                  ' matches with ' + confidence + '% confidence')

        image_source.close()
        image_target.close()

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
    def delete_faces_from_collection(self, collection_id, face_id):
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

    def detect_labels(self, bucket, photo):
        response = self.client.detect_labels(
            Image={'S3Object': {'Bucket': bucket, 'Name': photo}},
            MaxLabels=10)

        print('Detected labels for ' + photo)
        print()
        for label in response['Labels']:
            print("Label: " + label['Name'])
            print("Confidence: " + str(label['Confidence']))
            print("Instances:")
            for instance in label['Instances']:
                print("  Bounding box")
                print("    Top: " + str(instance['BoundingBox']['Top']))
                print("    Left: " + str(instance['BoundingBox']['Left']))
                print("    Width: " + str(instance['BoundingBox']['Width']))
                print("    Height: " + str(instance['BoundingBox']['Height']))
                print("  Confidence: " + str(instance['Confidence']))
                print()

            print("Parents:")
            for parent in label['Parents']:
                print("   " + parent['Name'])
            print("----------")

    def detect_moderation_labels(self, bucket, photo):
        response = self.client.detect_moderation_labels(
            Image={'S3Object': {'Bucket': bucket, 'Name': photo}})

        print('Detected labels for ' + photo)
        for label in response['ModerationLabels']:
            print(label['Name'] + ' : ' + str(label['Confidence']))
            print(label['ParentName'])

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

    def image_orientation_bounding_box(self, photo):
        """Exercise the Rekognition recognize_celebrities() method and
            ShowBoundingBoxPositions()"""
        # Extract the image width, height, and EXIF data
        width = None
        height = None
        image_binary = None
        try:
            with Image.open(photo) as image:
                width, height = image.size
                exif = None
                if 'exif' in image.info:
                    exif = image.info['exif']
                print(f'exif: {exif}')
        except IOError as e:
            print(e)
            exit(1)
        print(f'File name: {photo}')
        print(f'Image width, height: {width}, {height}')

        # Read the entire image into memory
        try:
            with open(photo, 'rb') as f:
                image_binary = f.read()
        except IOError as e:
            print(e)
            exit(2)

        # Detect the celebrities in the photo
        response = self.client.recognize_celebrities(Image={'Bytes': image_binary})

        if 'OrientationCorrection' in response:
            print(f'Image orientation: {response["OrientationCorrection"]}')
        else:
            print('No estimated orientation. Check the image\'s Exif metadata.')

        # List the identified celebrities
        print('Detected celebrities...')
        celebrities = response['CelebrityFaces']
        if not celebrities:
            print('No celebrities detected')
        else:
            for celebrity in celebrities:
                print(f'\nName: {celebrity["Name"]}')
                print(f'Match confidence: {celebrity["MatchConfidence"]}')

                # List the bounding box that surrounds the face
                if 'OrientationCorrection' in response:
                    ShowBoundingBoxPositions(
                        height, width,
                        celebrity['Face']['BoundingBox'],
                        response['OrientationCorrection'])

    def search_faces_by_image_collection(self, collection_id, bucket, file_name):
        threshold = 70
        max_faces = 2

        response = self.client.search_faces_by_image(
            CollectionId=collection_id,
            Image={'S3Object': {'Bucket': bucket, 'Name': file_name}},
            FaceMatchThreshold=threshold,
            MaxFaces=max_faces)

        face_matches = response['FaceMatches']
        print('Matching faces')
        for match in face_matches:
            print('FaceId:' + match['Face']['FaceId'])
            print('Similarity: ' + "{:.2f}".format(match['Similarity']) + "%")

    def search_faces_collection(self, collection_id, face_id):
        threshold = 50
        max_faces = 2

        response = self.client.search_faces(
            CollectionId=collection_id,
            FaceId=face_id,
            FaceMatchThreshold=threshold,
            MaxFaces=max_faces)

        face_matches = response['FaceMatches']
        print('Matching faces')
        for match in face_matches:
            print('FaceId:' + match['Face']['FaceId'])
            print('Similarity: ' + "{:.2f}".format(match['Similarity']) + "%")
