import boto3


class GetUploadImageUrlInteractor:
    def __init__(self, bucket_name=None,
                 temp_url_expiration=None,
                 folder=None, object_name=None):
        self.s3_client = None
        self.bucket_name = bucket_name
        self.temp_url_expiration = temp_url_expiration
        self.folder = folder
        self.object_name = object_name

    def set_s3_client(self):
        self.s3_client = boto3.client('s3')

    def create_presigned_post(self, bucket_name,
                              expiration=60):
        if self.folder:
            self.object_name = "{}/{}".format(self.folder, self.object_name)

        response = self.s3_client.generate_presigned_post(
            Bucket=bucket_name,
            Key=self.object_name,
            ExpiresIn=expiration)

        return response

    def run(self):
        self.set_s3_client()
        return self.create_presigned_post(
            bucket_name=self.bucket_name,
            expiration=self.temp_url_expiration)
