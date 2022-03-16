from unittest.mock import patch, MagicMock

from playerstars_interactors import \
    PostAppNotificationInteractor, BasicPostRequestModel
from playerstars_domain import Notification


prefix_post_app_notification = \
    'playerstars_interactors.notification.post_app_notification'


prefix_basic_post = 'playerstars_interactors.basic_interactor.basic_post'


@patch(f'{prefix_basic_post}.BasicPostResponseModel')
@patch.object(Notification, 'from_json')
def test_post_app_notification(from_json_mock, response_model_mock):
    adapter = MagicMock()
    post_data = MagicMock()
    request = BasicPostRequestModel(post_data)
    interactor = PostAppNotificationInteractor(request, adapter, Notification)
    response = interactor.run()

    from_json_mock.assert_called_with(post_data)
    from_json_mock().set_adapter.assert_called_with(adapter)
    from_json_mock().save.assert_called_once()
    response_model_mock.assert_called_with(from_json_mock().save())
    assert response == response_model_mock()()
