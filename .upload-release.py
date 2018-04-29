#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import os
import boto
from boto.exception import S3ResponseError
import argparse

BUCKET_NAME = 'cnry-python-packages'


def ensure_bucket(s3, name):
    try:
        bucket = s3.get_bucket(name)
    except S3ResponseError:
        bucket = s3.create_bucket(name)

    return bucket


def upload_package_to_s3(local_path):
    s3 = boto.connect_s3()
    bucket = ensure_bucket(s3, BUCKET_NAME)
    key = bucket.new_key(os.path.basename(local_path))
    key.set_contents_from_filename(local_path, replace=True)
    key.set_metadata('Content-Type', 'application/gzip')
    key.set_canned_acl('public-read')
    return key.generate_url(expires_in=0, query_auth=False, force_http=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='upload-release')
    parser.add_argument('package_path', help='the path to the gzip file')
    params = parser.parse_args()

    print upload_package_to_s3(params.package_path)
