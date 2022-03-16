from unittest.mock import patch

from playerstars_interactors.game.get_upload_image_url import \
    GetUploadImageUrlInteractor


patch_root = 'playerstars_interactors.game.get_upload_image_url'


@patch(f'{patch_root}.boto3')
def test_set_s3_client(m):
    interactor = GetUploadImageUrlInteractor(bucket_name='bucket',
                                             temp_url_expiration=90)
    interactor.set_s3_client()
    m.client.assert_called_with('s3')


@patch(f'{patch_root}.boto3')
def test_create_presigned_post(m):
    interactor = GetUploadImageUrlInteractor(object_name='name',
                                             folder='game/mask')
    interactor.set_s3_client()

    interactor.create_presigned_post(bucket_name='bucket',
                                     expiration=90)

    m.client().generate_presigned_post.assert_called_once()
    assert interactor.object_name == 'game/mask/name'


@patch(f'{patch_root}.boto3')
def test_run(m):
    interactor = GetUploadImageUrlInteractor()
    interactor.set_s3_client()
    interactor.run()
    m.client().generate_presigned_post.assert_called_once()
