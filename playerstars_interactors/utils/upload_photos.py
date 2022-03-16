from base64 import b64decode
from io import BytesIO
import boto3


def convert_from_base64(image_base64):
    return b64decode(image_base64)


def upload_profile_image(photo_name,
                         image_base64,
                         s3_bucket_name,
                         extension):
    s3_file_name = f"{photo_name}-photo.{extension}"
    s3 = boto3.client('s3')
    s3.upload_fileobj(image_base64,
                      s3_bucket_name,
                      s3_file_name,
                      ExtraArgs={'ACL': 'public-read'})
    return s3_file_name

# data:image/jpeg;base64,


def check_and_remove_metadata(sent_image):
    if "data:image/jpeg;base64," in sent_image:
        return sent_image.split('data:image/jpeg;base64,')[1], 'jpeg'
    if "data:image/jpg;base64," in sent_image:
        return sent_image.split('data:image/jpg;base64,')[1], 'jpg'
    if "data:image/png;base64," in sent_image:
        return sent_image.split('data:image/png;base64,')[1], 'png'
    return sent_image, 'jpg'


def upload_photo_and_return_url(sent_image,
                                unique_name,
                                s3_bucket_name,
                                s3_bucket_url):
    image_base_64, extension = check_and_remove_metadata(sent_image)
    new_photo_base64 = image_base_64
    profile_image = convert_from_base64(new_photo_base64)
    s3_image_name = upload_profile_image(
        photo_name=unique_name,
        image_base64=BytesIO(profile_image),
        s3_bucket_name=s3_bucket_name,
        extension=extension)
    return s3_bucket_url + "/" + s3_image_name
