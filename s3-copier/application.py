import botocore
import jmespath
import streamlit as st
import boto3
import os
from configparser import ConfigParser
import shutil
from stqdm import stqdm


# Ensure staging directory exists and is empty
def setup_staging_area(stage_dir):
    if os.path.exists(stage_dir):
        shutil.rmtree(stage_dir)
    os.makedirs(stage_dir, exist_ok=True)


# Function to get AWS profiles from credentials file
def get_aws_profiles():
    aws_credentials_file = os.path.expanduser('~/.aws/credentials')
    parser = ConfigParser()
    parser.read(aws_credentials_file)
    return parser.sections()

def bucket_exists(s3, bucket_name):
    try:
        s3.head_bucket(Bucket=bucket_name)
        return True
    except botocore.exceptions.ClientError as e:
        error_code = int(e.response['Error']['Code'])
        if error_code == 404:  # Not Found
            return False
        else:
            st.error(f"Error checking bucket existence: {e}")
            return False


# Function to copy files from S3 to local staging area
def copy_files_to_local(profile, bucket, prefix, file_limit, file_pattern, staging_directory):
    setup_staging_area()
    session = boto3.Session(profile_name=profile)
    s3 = session.client('s3')

    if not bucket_exists(s3, bucket):
        st.error(f"Bucket '{bucket}' does not exist or you don't have permission to access it.")
        return

    paginator = s3.get_paginator('list_objects_v2')
    count = 0
    if file_pattern:
        jmespath_expression = f"Contents[?contains(Key,'{file_pattern}')][]"
    else:
        jmespath_expression = "[*]"  # Select all objects if no pattern is provided


    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        filtered_objects = jmespath.search(jmespath_expression, page)

        for obj in stqdm(filtered_objects, total=min(file_limit, len(filtered_objects)), desc="Downloading files"):
                if count >= file_limit:
                    break
                path = obj['Key']
                if not path.endswith('/'):  # Avoid creating empty folders for keys that are prefixes
                    s3.download_file(bucket, obj['Key'], os.path.join(staging_directory, os.path.basename(obj['Key'])))
                    count += 1
                if count >= file_limit:
                    break


# Function to upload files from local staging to S3
def upload_files_from_local(profile, bucket, prefix, staging_directory):
    session = boto3.Session(profile_name=profile)
    s3 = session.client('s3')
    files = os.listdir(staging_directory)
    total_files = len(files)
    count = 0

    for file in files:
        file_path = os.path.join(staging_directory, file)
        s3.upload_file(file_path, bucket, os.path.join(prefix, file))
        count += 1
        st.progress(count / total_files)
        st.write(f"Uploaded {file} to {bucket}/{prefix}")


def main():
    st.title('S3 File Copy Tool')

    profiles = get_aws_profiles()
    source_profile = st.selectbox('Select source profile for download', profiles)
    source_bucket = st.text_input('Enter source bucket name')
    source_prefix = st.text_input('Enter source prefix')
    staging_directory = st.text_input('Enter the the local stage directory', '/tmp/filecopier')
    file_limit = st.number_input('Limit number of files to copy to local', min_value=1, value=10, step=1)
    file_pattern = st.text_input("Enter file pattern (e.g., '.txt' or 'image_')", value="")

    if not source_bucket:
        st.error("Provide a bucket name")

    if st.button('Copy to Local Staging'):
        copy_files_to_local(source_profile, source_bucket, source_prefix, file_limit, file_pattern, staging_directory)

    st.write("---")  # Visual separator

    # Option to reload profiles in case of any updates
    if st.button('Reload Profiles'):
        profiles = get_aws_profiles()
        st.success("Profiles reloaded")

    destination_profile = st.selectbox('Select destination profile for upload', profiles)
    destination_bucket = st.text_input('Enter destination bucket name')
    destination_prefix = st.text_input('Enter destination prefix')

    if st.button('Upload from Local Staging'):
        upload_files_from_local(destination_profile, destination_bucket, destination_prefix, staging_directory)


if __name__ == "__main__":
    main()
