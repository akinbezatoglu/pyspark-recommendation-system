import logging
import boto3
from botocore.exceptions import ClientError
import os
import argparse
import sys
import threading

class ProgressPercentage(object):

    def __init__(self, filename):
        self._filename = filename
        self._size = float(os.path.getsize(filename))
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        # To simplify, assume this is hooked up to a single filename
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            sys.stdout.write(
                "\r%s  %s / %s  (%.2f%%)" % (
                    self._filename, self._seen_so_far, self._size,
                    percentage))
            sys.stdout.flush()

def create_bucket(bucket_name, region=None):
    """Create an S3 bucket in a specified region

    If a region is not specified, the bucket is created in the S3 default
    region (us-east-1).

    :param bucket_name: Bucket to create
    :param region: String region to create bucket in, e.g., 'us-west-2'
    :return: True if bucket created, else False
    """

    try:
        if region is None:
            s3_client = boto3.client('s3')
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            s3_client = boto3.client('s3', region_name=region)
            location = {'LocationConstraint': region}
            s3_client.create_bucket(Bucket=bucket_name,
                                    CreateBucketConfiguration=location)
    except ClientError as e:
        logging.error(e)
        return False
    return True

def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name,
                                         Callback=ProgressPercentage(os.path.join(dirname, filename)))
    except ClientError as e:
        logging.error(e)
        return False
    return True

if __name__ == "__main__":
    ap = argparse.ArgumentParser()

    # Add region argument to the parser
    ap.add_argument("-r", "--region", required=False, help="specify the region of the s3 bucket to be created")
    # Add bucket-name argument to the parser
    ap.add_argument("-n", "--bucketname", required=True, help="specify the bucket name of the s3 bucket to be created")
    # Add folder path argument to the parser
    ap.add_argument("-f", "--filepath", required=True, help="specify the local path of folder to be uploaded")

    args = vars(ap.parse_args())
    
    # Create bucket
    create_bucket(bucket_name=args['bucketname'], region=args['region'])

    # Upload files to the created bucket
    destination = 'preprocessed-data/'
    for dirname, _, filenames in os.walk(args['filepath']):
        for filename in filenames:
            # construct the full local path
            local_path = os.path.join(dirname, filename)
            relative_path = os.path.relpath(local_path, args['filepath'])
            s3_path = os.path.join(destination, relative_path)
            upload_file(file_name=local_path,
                        bucket=args['bucketname'],
                        object_name=s3_path)
