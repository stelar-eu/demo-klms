"""
    Module classes related to the S3 storage system.
"""
from minio import S3Error

from stelar.etl import Module, Node


class BucketModule(Module):
    """Bucket creation module
    """

    def __init__(self, name: str, parent: Node = None, *, spec: dict = {}):
        if "bucket_name" not in spec:
            spec["bucket_name"] = name
        super().__init__(name, parent, spec=spec)

    def check_installed(self):
        name = self.spec['bucket_name']
        cli = self.catalog.client
        return cli.s3.bucket_exists(name)

    def install(self):
        cli = self.catalog.client
        cli.s3.make_bucket(** self.spec)

    def uninstall(self):
        cli = self.catalog.client
        bucket_name = self.spec['bucket_name']
        try:
            cli.s3.remove_bucket(bucket_name)
        except S3Error as e:
            if e.code != 'NoSuchBucket':
                raise

    @property
    def url(self):
        """Return the URL of the bucket."""
        cli = self.catalog.client
        bucket_name = self.spec['bucket_name']
        return f"s3://{bucket_name}"


class FileModule(Module):
    """File creation module"""

    def __init__(self, name: str, parent: Node = None, *, spec):
        super().__init__(name, parent, spec=spec)

    def check_installed(self):
        cli = self.catalog.client
        bucket_name = self.spec['bucket_name']
        object_name = self.spec['object_name']
        try:
            cli.s3.stat_object(bucket_name, object_name)
            return True
        except S3Error:
            return False

    def install(self):
        cli = self.catalog.client
        cli.s3.fput_object(** self.spec)

    def uninstall(self):
        cli = self.catalog.client
        bucket_name = self.spec['bucket_name']
        object_name = self.spec['object_name']
        cli.s3.remove_object(bucket_name, object_name)

    @property
    def url(self):
        """Return the URL of the file."""
        cli = self.catalog.client
        bucket_name = self.spec['bucket_name']
        object_name = self.spec['object_name']
        return f"s3//{bucket_name}/{object_name}"

