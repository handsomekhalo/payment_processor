
"""
File for the separation of S3 file management.
"""
import boto3
from django.conf import settings
import pathlib


def upload_to_s3(file, file_name):
    """
    Upload file to S3 bucket and verify its size.
    """
    path = settings.COMPANY_PATH
    s3_file_name = f"{path}/{file_name}"
    s3 = boto3.client('s3')

    # bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    bucket_name = settings.BACK_BLAZE_BUCKET_NAME


    try:
        # Upload the file to S3
        s3.upload_fileobj(file, bucket_name, s3_file_name)

        s3.head_object(Bucket=bucket_name, Key=s3_file_name)
        s3_object_path = f"https://{bucket_name}.s3.amazonaws.com/{s3_file_name}"
        return s3_object_path
    except Exception:
        return None

def open_s3_file(filepath):
    """
    Open file from S3 link.
    """
    bucket = settings.AWS_STORAGE_BUCKET_NAME

    if bucket in str(filepath):

        s3 = boto3.client('s3'
                      )

        file_path = str(filepath).replace("https://" + bucket + ".s3.amazonaws.com/", "")
        if pathlib.Path(file_path).suffix == ".pdf":
            url = s3.generate_presigned_url(
                ClientMethod='get_object',
                Params={
                    'Bucket': bucket,
                    'Key': file_path,
                    "ResponseContentDisposition": "inline",
                    "ResponseContentType": "application/pdf"
                },
                ExpiresIn=3600
            )
        elif pathlib.Path(file_path).suffix == ".mp4":
            url = s3.generate_presigned_url(
                ClientMethod='get_object',
                Params={
                    'Bucket': bucket,
                    'Key': file_path,
                    "ResponseContentDisposition": "inline",
                    "ResponseContentType": "video/mp4"
                },
                ExpiresIn=3600
            )
        else:
            url = s3.generate_presigned_url(
                ClientMethod='get_object',
                Params={
                    'Bucket': bucket,
                    'Key': file_path,
                    "ResponseContentDisposition": "inline",
                },
                ExpiresIn=3600
            )

        return url

    else:
        return filepath


def delete_s3_file(filepath):
    """
    Delete file from the S3 bucket.
    """
    bucket = settings.AWS_STORAGE_BUCKET_NAME

    # Connect to the S3 bucket
    s3 = boto3.client('s3')
    file_name = str(filepath).replace("https://" + bucket + ".s3.amazonaws.com/", "")

    s3.delete_object(
        Bucket=bucket,
        Key=file_name)
    return True