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
