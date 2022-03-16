from collections import namedtuple
from playerstars_adapters import (
    NotificationAdapter,
    PlayerAdapter,
    TeamAdapter)
from playerstars_domain import (
    MemberStatus,
    MemberType,
    NotificationType)
from playerstars_interactors import (
    PostTeamInteractor,
    PostTeamRequestModel,
    PostTeamResponseModel,
    SaveTeamException)
from pytest import fixture, raises
from unittest import TestCase
from unittest.mock import MagicMock, patch

import pytest


prefix = 'playerstars_interactors.team.post_team'


def test_post_team_request_model():
    mock_json_data = MagicMock()
    request = PostTeamRequestModel(mock_json_data)
    calls = {x[1][0]: x() for x in mock_json_data.mock_calls}

    fields = [('name', 'name'), ('captain', 'captain'),
              ('members', 'members'), ('description', 'description'),
              ('image_base64', 'image_base64'),
              ('console_id', 'console_id'), ('game_id', 'game_id')]

    for field in fields:
        assert getattr(request, field[0]) == calls[field[1]]
    assert len(calls) == len(fields)


def test_post_team_response_model():
    mock_saved_id = MagicMock()
    response_model = PostTeamResponseModel(mock_saved_id)
    assert response_model
    assert response_model.saved_id == mock_saved_id


def test_post_team_response_model__call():
    mock_saved_id = MagicMock()
    response_model = PostTeamResponseModel(mock_saved_id)
    call_result = response_model()
    assert call_result == mock_saved_id


Factory = namedtuple('Factory',
                     'interactor, mock_request, mock_player_adapter, '
                     'mock_team_adapter, mock_notification_adapter, '
                     'mock_s3_bucket_name, mock_s3_bucket_url')


@fixture(scope='class')
def interactor_fixture(request):
    def factory(request: PostTeamRequestModel = MagicMock(),
                player_adapter: PlayerAdapter = MagicMock(),
                team_adapter: TeamAdapter = MagicMock(),
                notification_adapter: NotificationAdapter = MagicMock(),
                s3_bucket_name: str = MagicMock(),
                s3_bucket_url: str = MagicMock()):
        interactor = PostTeamInteractor(
            request=request,
            player_adapter=player_adapter,
            team_adapter=team_adapter,
            notification_adapter=notification_adapter,
            s3_bucket_name=s3_bucket_name,
            s3_bucket_url=s3_bucket_url)
        return Factory(interactor, request, player_adapter,
                       team_adapter, notification_adapter, s3_bucket_name,
                       s3_bucket_url)
    request.cls.factory = factory


@pytest.mark.usefixtures('interactor_fixture')
class TestPostTeamInteractor(TestCase):
    def setUp(self):
        fac = TestPostTeamInteractor.factory()
        self.interactor: PostTeamInteractor = fac.interactor
        self.mock_request = fac.mock_request
        self.mock_player_adapter = fac.mock_player_adapter
        self.mock_team_adapter = fac.mock_team_adapter
        self.mock_notification_adapter = fac.mock_notification_adapter
        self.mock_s3_bucket_name = fac.mock_s3_bucket_name
        self.mock_s3_bucket_url = fac.mock_s3_bucket_url

    def tearDown(self):
        pass

    def test_init(self):
        assert self.interactor.request == self.mock_request
        assert self.interactor.player_adapter == self.mock_player_adapter
        assert self.interactor.team_adapter == self.mock_team_adapter
        assert self.interactor.notification_adapter == \
            self.mock_notification_adapter
        assert self.interactor.s3_bucket_name == self.mock_s3_bucket_name
        assert self.interactor.s3_bucket_url == self.mock_s3_bucket_url

    def test_get_member(self):
        mock_member_id = MagicMock()
        member = self.interactor.get_member(mock_member_id)
        self.mock_player_adapter.get_by_id.assert_called_with(mock_member_id)
        assert member == self.mock_player_adapter.get_by_id()

    @patch.object(PostTeamInteractor, '_init_member')
    def test__init_captain(self, mock_init_member):
        captain = self.interactor._init_captain()
        mock_init_member.assert_called_with(
            member_id=self.mock_request.captain,
            member_type=MemberType.CAPTAIN,
            member_status=MemberStatus.ACCEPTED)
        assert captain == mock_init_member()

    @patch.object(PostTeamInteractor, 'get_member')
    @patch(f'{prefix}.TeamMember')
    @patch(f'{prefix}.aware_now')
    def test__init_member(self, mock_aware_now,
                          mock_team_member,
                          mock_get_member):
        mock_member_id = MagicMock()
        mock_member_type = MemberType.CAPTAIN
        mock_member_status = MagicMock()
        member = self.interactor._init_member(
            member_id=mock_member_id,
            member_type=mock_member_type,
            member_status=mock_member_status)

        mock_get_member.assert_called_with(mock_member_id)
        mock_team_member.assert_called_with(
            player_id=mock_member_id,
            member_type=mock_member_type,
            status=mock_member_status,
            association_date=mock_aware_now(),
            last_status_change_datetime=mock_aware_now())
        mock_aware_now.assert_called()
        assert member == mock_team_member()

    @patch.object(PostTeamInteractor,
                  'get_member',
                  return_value=None)
    @patch(f'{prefix}.TeamMember')
    @patch(f'{prefix}.aware_now')
    def test__init_member_error(self, mock_aware_now,
                                mock_team_member,
                                mock_get_member):
        mock_member_id = MagicMock()
        mock_member_type = MemberType.CAPTAIN
        mock_member_status = MagicMock()
        self.mock_request.captain = '1'

        with raises(Exception) as exc:
            self.interactor._init_member(
                member_id=mock_member_id,
                member_type=mock_member_type,
                member_status=mock_member_status)
        assert 'Team member CAPTAIN 1 not found' in str(exc.value)

    @patch.object(PostTeamInteractor, '_init_member')
    def test_mount_member_list(self, mock_init_member):
        mock_member_list = ['1']
        assert len(mock_member_list) == 1
        result = self.interactor.mount_member_list(mock_member_list)
        assert isinstance(result, list)
        assert result == [mock_init_member()]
        mock_init_member.assert_called()

    @patch.object(PostTeamInteractor, '_init_member')
    def test_mount_member_list_empty(self, mock_init_member):
        mock_member_list = []
        assert len(mock_member_list) == 0
        result = self.interactor.mount_member_list(mock_member_list)
        assert isinstance(result, list)
        assert len(result) == 0
        mock_init_member.assert_not_called()

    @patch.object(PostTeamInteractor, '_init_member')
    def test_mount_member_list_repeated(self, mock_init_member):
        mock_member_list = ['1', '1']
        assert len(mock_member_list) == 2
        result = self.interactor.mount_member_list(mock_member_list)
        assert isinstance(result, list)
        assert len(result) == 1
        mock_init_member.assert_called_with(
            member_id='1',
            member_type=MemberType.MEMBER,
            member_status=MemberStatus.INVITED)

    @patch.object(PostTeamInteractor, 'invite_member')
    def test_invite_members(self, mock_invite_member):
        mock_team = MagicMock()
        mock_member = MagicMock()
        mock_member.status = MemberStatus.INVITED
        mock_members = [mock_member]
        mock_team.members = mock_members
        self.interactor.invite_members(mock_team)
        mock_invite_member.assert_called_with(
            member_data=mock_member,
            team=mock_team)

    @patch.object(PostTeamInteractor, 'invite_member')
    def test_invite_members__not_call_invite_member(self, mock_invite_member):
        mock_team = MagicMock()
        mock_member = MagicMock()
        mock_member.status = MemberStatus.ACCEPTED
        mock_members = [mock_member]
        mock_team.members = mock_members
        self.interactor.invite_members(mock_team)
        mock_invite_member.assert_not_called()

    @patch.object(PostTeamInteractor, 'get_member')
    @patch(f'{prefix}.create_notification')
    def test_invite_member(self, mock_create_notification,
                           mock_get_member):
        mock_member_data = MagicMock()
        mock_team = MagicMock()
        self.interactor.invite_member(
            member_data=mock_member_data,
            team=mock_team)
        mock_get_member.assert_called_with(mock_member_data.player_id)
        mock_create_notification.assert_called_with(
            player_data=mock_get_member(),
            notification_adapter=self.mock_notification_adapter,
            notification_type=NotificationType.TEAM_INVITE,
            notification_image=mock_team.logo_path,
            notification_complement=mock_team.name,
            team_id=mock_team.entity_id,
            logger_instance=self.interactor.logger)

    @patch(f'{prefix}.upload_photo_and_return_url')
    def test__upload_team_image(self, mock_upload_photo_and_return_url):
        mock_team = MagicMock()
        result = self.interactor._upload_team_image(mock_team)
        mock_upload_photo_and_return_url.assert_called_with(
            sent_image=self.mock_request.image_base64,
            unique_name=mock_team.entity_id,
            s3_bucket_name=self.mock_s3_bucket_name,
            s3_bucket_url=self.mock_s3_bucket_url)
        assert result == mock_upload_photo_and_return_url()

    @patch(f'{prefix}.upload_photo_and_return_url')
    def test__upload_team_image__not_request_image(
            self, mock_upload_photo_and_return_url):
        mock_team = MagicMock()
        self.mock_request.image_base64 = None
        result = self.interactor._upload_team_image(mock_team)
        assert result is None
        mock_upload_photo_and_return_url.assert_not_called()

    def test_check_request_data_all_true(self):
        self.mock_request.captain = MagicMock()
        self.mock_request.console_id = MagicMock()
        self.mock_request.game_id = MagicMock()
        result = self.interactor.check_request_data()
        assert result is True

    def test_check_request_data__not_captain(self):
        self.mock_request.captain = None
        with raises(Exception) as exc:
            self.interactor.check_request_data()
        assert 'Team leader was not provided' in str(exc.value)

    def test_check_request_data__not_console_id(self):
        self.mock_request.captain = MagicMock()
        self.mock_request.console_id = None
        with raises(Exception) as exc:
            self.interactor.check_request_data()
        assert 'Team console was not provided' in str(exc.value)

    def test_check_request_data_not_game_id(self):
        self.mock_request.game_id = None
        with raises(Exception) as exc:
            self.interactor.check_request_data()
        assert 'Team game was not provided' in str(exc.value)

    @patch.object(PostTeamInteractor, '_init_captain')
    @patch.object(PostTeamInteractor, 'mount_member_list')
    @patch.object(PostTeamInteractor, '_upload_team_image')
    @patch(f'{prefix}.Team')
    @patch(f'{prefix}.uuid')
    def test__init_team(self, mock_uuid,
                        mock_team,
                        mock_upload_team_image,
                        mock_mount_member_list,
                        mock_init_captain):
        team_data = self.interactor._init_team()
        mock_init_captain.assert_called()
        mock_mount_member_list.assert_called_with(self.mock_request.members)
        mock_team.assert_called_with(
            entity_id=str(mock_uuid.uuid4()),
            name=self.mock_request.name,
            captain=mock_init_captain(),
            members=mock_mount_member_list(),
            description=self.mock_request.description,
            game_id=self.mock_request.game_id,
            console_id=self.mock_request.console_id)
        mock_upload_team_image.assert_called_with(mock_team())
        assert team_data == mock_team()

    def test__save_team(self):
        mock_team = MagicMock()
        result = self.interactor._save_team(mock_team)
        mock_team.set_adapter.assert_called_with(self.mock_team_adapter)
        mock_team.save.assert_called()
        assert result == mock_team.save()

    @patch.object(PostTeamInteractor, 'check_request_data')
    @patch.object(PostTeamInteractor, '_init_team')
    @patch.object(PostTeamInteractor, 'invite_members')
    @patch.object(PostTeamInteractor, '_save_team')
    @patch(f'{prefix}.PostTeamResponseModel')
    def test_run(self, mock_response_model,
                 mock_save_team,
                 mock_invite_members,
                 mock_init_team,
                 mock_check_request_data):
        response = self.interactor.run()
        mock_check_request_data.assert_called()
        mock_init_team.assert_called()
        mock_invite_members.assert_called_with(mock_init_team())
        mock_save_team.assert_called_with(mock_init_team())
        mock_response_model.assert_called_with(mock_save_team())
        assert response == mock_response_model()

    @patch.object(PostTeamInteractor,
                  'check_request_data',
                  side_effect=Exception('oops'))
    @patch.object(PostTeamInteractor, '_init_team')
    @patch.object(PostTeamInteractor, 'invite_members')
    @patch.object(PostTeamInteractor, '_save_team')
    @patch(f'{prefix}.PostTeamResponseModel')
    def test_run_raises(self, mock_response_model,
                        mock_save_team,
                        mock_invite_members,
                        mock_init_team,
                        mock_check_request_data):
        with raises(SaveTeamException) as exc:
            self.interactor.run()
        assert 'Error during team creation: oops' in str(exc.value)
        mock_check_request_data.assert_called()
        mock_init_team.assert_not_called()
        mock_invite_members.assert_not_called()
        mock_save_team.assert_not_called()
        mock_response_model.assert_not_called()
