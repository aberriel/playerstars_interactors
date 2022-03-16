from collections import namedtuple
from playerstars_domain import (
    MemberStatus,
    MemberType,
    NotificationType)
from playerstars_interactors.team import (
    DuplicateMemberException,
    PutTeamAdapters,
    PutTeamInteractor,
    PutTeamRequestModel,
    PutTeamResponseModel,
    UpdateTeamException)
from pytest import fixture, raises
from unittest import TestCase
from unittest.mock import MagicMock, patch

import pytest


prefix = 'playerstars_interactors.team.put_team'


def test_request_model():
    mock_json_data = MagicMock()
    request = PutTeamRequestModel(mock_json_data)
    calls = {x[1][0]: x() for x in mock_json_data.mock_calls}

    fields = [('entity_id', 'entity_id'), ('name', 'name'),
              ('members', 'members'), ('console_id', 'console_id'),
              ('description', 'description'),
              ('image_base64', 'image_base64'), ('game_id', 'game_id')]

    for field in fields:
        assert getattr(request, field[0]) == calls[field[1]]
    assert len(calls) == len(fields)


def test_response_model():
    mock_saved_id = MagicMock()
    response = PutTeamResponseModel(mock_saved_id)
    assert response.saved_id == mock_saved_id


def test_response_model__call():
    mock_saved_id = MagicMock()
    response = PutTeamResponseModel(mock_saved_id)
    response_call = response()
    assert response_call == mock_saved_id


def test_adapters():
    mock_notification_adapter = MagicMock()
    mock_player_adapter = MagicMock()
    mock_team_adapter = MagicMock()
    adapters = PutTeamAdapters(
        notification_adapter=mock_notification_adapter,
        player_adapter=mock_player_adapter,
        team_adapter=mock_team_adapter)

    assert adapters.notification_adapter == mock_notification_adapter
    assert adapters.player_adapter == mock_player_adapter
    assert adapters.team_adapter == mock_team_adapter


Factory = namedtuple('Factory', 'interactor, mock_request, mock_adapters, '
                                'mock_s3_bucket_name, mock_s3_bucket_url')


@fixture(scope='class')
def interactor_fixture(request):
    def factory(request: PutTeamRequestModel = MagicMock(),
                adapters: PutTeamAdapters = MagicMock(),
                s3_bucket_name: str = MagicMock(),
                s3_bucket_url: str = MagicMock()):
        interactor = PutTeamInteractor(
            request=request,
            adapters=adapters,
            s3_bucket_name=s3_bucket_name,
            s3_bucket_url=s3_bucket_url)
        return Factory(interactor, request, adapters,
                       s3_bucket_name, s3_bucket_url)
    request.cls.factory = factory


@pytest.mark.usefixtures('interactor_fixture')
class TestPutTeamInteractor(TestCase):
    def setUp(self):
        fac = TestPutTeamInteractor.factory()
        self.interactor: PutTeamInteractor = fac.interactor
        self.mock_request = fac.mock_request
        self.mock_adapters = fac.mock_adapters
        self.mock_s3_bucket_name = fac.mock_s3_bucket_name
        self.mock_s3_bucket_url = fac.mock_s3_bucket_url

    def tearDown(self):
        pass

    def test_init(self):
        assert self.interactor.request == self.mock_request
        assert self.interactor.adapters == self.mock_adapters
        assert self.interactor.s3_bucket_name == self.mock_s3_bucket_name
        assert self.interactor.s3_bucket_url == self.mock_s3_bucket_url

    @patch(f'{prefix}.find_entity_by_id')
    def test_get_saved_team(self, mock_find_entity_by_id):
        team_data = self.interactor.get_saved_team()
        mock_find_entity_by_id.assert_called_with(
            _id=self.mock_request.entity_id,
            adapter_instance=self.mock_adapters.team_adapter,
            class_name='Team')
        assert team_data == mock_find_entity_by_id()

    def test_find_member_old_team_is_captain(self):
        mock_member_id = '1'
        self.interactor.saved_team = MagicMock()
        self.interactor.saved_team.captain.player_id = mock_member_id
        with raises(UpdateTeamException) as exc:
            self.interactor.find_member_old_team(mock_member_id)
        assert 'Member 1 is team leader' in str(exc.value)

    def test_find_member_old_team_is_not_captain(self):
        mock_member_id = MagicMock()
        mock_team = MagicMock()

        mock_member = MagicMock()
        mock_member.player_id = mock_member_id
        mock_members = [mock_member]
        mock_team.members = mock_members
        self.interactor.saved_team = mock_team

        member_found = self.interactor.find_member_old_team(mock_member_id)
        assert member_found == mock_member

    @patch(f'{prefix}.find_entity_by_id')
    def test_get_member(self, mock_find_entity_by_id):
        mock_member_id = MagicMock()
        member_data = self.interactor.get_member(mock_member_id)
        mock_find_entity_by_id.assert_called_with(
            _id=mock_member_id,
            adapter_instance=self.mock_adapters.player_adapter,
            class_name='Player')
        assert member_data == mock_find_entity_by_id()

    @patch(f'{prefix}.aware_now')
    @patch(f'{prefix}.TeamMember')
    @patch.object(PutTeamInteractor, 'get_member')
    @patch.object(PutTeamInteractor,
                  'find_member_old_team',
                  return_value=None)
    def test_mount_member_list(self, mock_find_member_old_team,
                               mock_get_member,
                               mock_team_member,
                               mock_aware_now):
        mock_members = ['1']
        member_list = self.interactor.mount_member_list(mock_members)

        mock_get_member.assert_called_with('1')
        mock_aware_now.assert_called()
        mock_find_member_old_team.assert_called_with('1')
        mock_team_member.assert_called_with(
            player_id=mock_get_member().entity_id,
            association_date=mock_aware_now(),
            member_type=MemberType.MEMBER,
            status=MemberStatus.INVITED)
        assert member_list == [mock_team_member()]

    @patch(f'{prefix}.aware_now')
    @patch(f'{prefix}.TeamMember')
    @patch.object(PutTeamInteractor,
                  'get_member',
                  return_value=None)
    @patch.object(PutTeamInteractor, 'find_member_old_team')
    def test_mount_member_list__not_member(
            self, mock_find_member_old_team,
            mock_get_member,
            mock_team_member,
            mock_aware_now):
        mock_members = ['1']
        with raises(Exception) as exc:
            self.interactor.mount_member_list(mock_members)
        assert 'Player 1 not found' in str(exc.value)
        mock_get_member.assert_called_with('1')
        mock_aware_now.assert_not_called()
        mock_find_member_old_team.assert_not_called()

    @patch(f'{prefix}.aware_now')
    @patch(f'{prefix}.TeamMember')
    @patch.object(PutTeamInteractor, 'get_member')
    @patch.object(PutTeamInteractor, 'find_member_old_team')
    def test_mount_member_list__saved_member(
            self, mock_find_member_old_team,
            mock_get_member,
            mock_team_member,
            mock_aware_now):
        mock_members = ['1']
        members = self.interactor.mount_member_list(mock_members)

        mock_get_member.assert_called_with('1')
        mock_aware_now.assert_called()
        mock_find_member_old_team.assert_called_with('1')
        mock_team_member.assert_called_with(
            player_id=mock_get_member().entity_id,
            association_date=mock_find_member_old_team().association_date,
            member_type=MemberType.MEMBER,
            status=mock_find_member_old_team().status)
        assert members == [mock_team_member()]

    @patch(f'{prefix}.aware_now')
    @patch(f'{prefix}.TeamMember')
    @patch.object(PutTeamInteractor, 'get_member')
    @patch.object(PutTeamInteractor, 'find_member_old_team')
    def test_mount_member_list__empty_list(
            self, mock_find_member_old_team,
            mock_get_member,
            mock_team_member,
            mock_aware_now):
        mock_members = []
        members = self.interactor.mount_member_list(mock_members)

        mock_get_member.assert_not_called()
        mock_find_member_old_team.assert_not_called()
        mock_team_member.assert_not_called()
        mock_aware_now.assert_not_called()
        assert members == []

    @patch.object(PutTeamInteractor, 'invite_new_member')
    def test_invite_new_members(self, mock_invite_new_member):
        mock_team = MagicMock()
        mock_saved_team = MagicMock()

        mock_team_member = MagicMock()
        mock_team_member.player_id = '1'
        mock_members = [mock_team_member]
        mock_team.members = mock_members
        self.interactor.saved_team = mock_saved_team

        self.interactor.invite_new_members(mock_team)
        mock_invite_new_member.assert_called_with(
            member_id='1',
            team=mock_team)

    @patch.object(PutTeamInteractor, 'invite_new_member')
    def test_invite_new_members__not_invite(
            self, mock_invite_new_member):
        mock_team = MagicMock()
        mock_saved_team = MagicMock()

        mock_team_member = MagicMock()
        mock_team_member.player_id = '1'
        mock_members = [mock_team_member]
        mock_saved_team.members = mock_members
        mock_team.members = mock_members
        self.interactor.saved_team = mock_saved_team

        self.interactor.invite_new_members(mock_team)
        mock_invite_new_member.assert_not_called()

    @patch(f'{prefix}.create_notification')
    @patch.object(PutTeamInteractor, 'get_member')
    def test_invite_new_member(self, mock_get_member,
                               mock_create_notification):
        mock_member_id = MagicMock()
        mock_team = MagicMock()
        self.interactor.invite_new_member(
            member_id=mock_member_id,
            team=mock_team)

        mock_get_member.assert_called_with(mock_member_id)
        mock_create_notification.assert_called_with(
            player_data=mock_get_member(),
            notification_adapter=self.mock_adapters.notification_adapter,
            notification_type=NotificationType.TEAM_INVITE,
            team_id=mock_team.entity_id,
            notification_image=mock_team.logo_path,
            notification_complement=mock_team.name,
            logger_instance=self.interactor.logger)

    @patch(f'{prefix}.upload_photo_and_return_url')
    @patch(f'{prefix}.Team')
    @patch.object(PutTeamInteractor, 'mount_member_list')
    @patch.object(PutTeamInteractor, 'invite_new_members')
    def test_init_team(self, mock_invite_new_members,
                       mock_mount_member_list,
                       mock_team,
                       mock_upload_photo_and_return_url):
        self.mock_request.image_base64 = None
        mock_old_team = MagicMock()
        team_data = self.interactor.init_team(mock_old_team)

        mock_mount_member_list.assert_called_with(self.mock_request.members)
        mock_upload_photo_and_return_url.assert_not_called()
        mock_team.assert_called_with(
            name=self.mock_request.name,
            captain=mock_old_team.captain,
            members=mock_mount_member_list(),
            console_id=self.mock_request.console_id,
            entity_id=self.mock_request.entity_id,
            description=self.mock_request.description,
            game_id=self.mock_request.game_id,
            logo_path=mock_old_team.logo_path)
        mock_invite_new_members.assert_called_with(mock_team())
        assert team_data == mock_team()

    @patch(f'{prefix}.upload_photo_and_return_url')
    @patch(f'{prefix}.Team')
    @patch.object(PutTeamInteractor, 'mount_member_list')
    @patch.object(PutTeamInteractor, 'invite_new_members')
    def test_init_team__upload_image(self, mock_invite_new_members,
                                     mock_mount_member_list,
                                     mock_team,
                                     mock_upload_photo_and_return_url):
        mock_old_team = MagicMock()
        self.mock_request.image_base64 = MagicMock()
        self.mock_request.name = MagicMock()
        self.mock_request.console_id = MagicMock()
        self.mock_request.game_id = MagicMock()
        self.mock_request.description = MagicMock()
        team_data = self.interactor.init_team(mock_old_team)

        mock_mount_member_list.assert_called_with(self.mock_request.members)
        mock_upload_photo_and_return_url.assert_called_with(
            sent_image=self.mock_request.image_base64,
            unique_name=self.mock_request.entity_id,
            s3_bucket_name=self.mock_s3_bucket_name,
            s3_bucket_url=self.mock_s3_bucket_url)
        mock_team.assert_called_with(
            name=self.mock_request.name,
            captain=mock_old_team.captain,
            members=mock_mount_member_list(),
            console_id=self.mock_request.console_id,
            entity_id=self.mock_request.entity_id,
            description=self.mock_request.description,
            game_id=self.mock_request.game_id,
            logo_path=mock_upload_photo_and_return_url())
        mock_invite_new_members.assert_called_with(mock_team())
        assert team_data == mock_team()

    @patch(f'{prefix}.upload_photo_and_return_url')
    @patch(f'{prefix}.Team')
    @patch.object(PutTeamInteractor, 'mount_member_list')
    @patch.object(PutTeamInteractor, 'invite_new_members')
    def test_init_team__request_some_fields_none(
            self, mock_invite_new_members,
            mock_mount_member_list,
            mock_team,
            mock_upload_photo_and_return_url):
        mock_old_team = MagicMock()
        self.mock_request.image_base64 = MagicMock()
        self.mock_request.name = None
        self.mock_request.console_id = None
        self.mock_request.description = None
        self.mock_request.game_id = None
        team_data = self.interactor.init_team(mock_old_team)

        mock_mount_member_list.assert_called_with(self.mock_request.members)
        mock_upload_photo_and_return_url.assert_called_with(
            sent_image=self.mock_request.image_base64,
            unique_name=self.mock_request.entity_id,
            s3_bucket_name=self.mock_s3_bucket_name,
            s3_bucket_url=self.mock_s3_bucket_url)
        mock_team.assert_called_with(
            name=mock_old_team.name,
            captain=mock_old_team.captain,
            members=mock_mount_member_list(),
            console_id=mock_old_team.console_id,
            entity_id=self.mock_request.entity_id,
            description=mock_old_team.description,
            game_id=mock_old_team.game_id,
            logo_path=mock_upload_photo_and_return_url())
        mock_invite_new_members.assert_called_with(mock_team())
        assert team_data == mock_team()

    def test_check_member_list_duplicates_raise(self):
        mock_member_list = ['1', '1']
        self.mock_request.members = mock_member_list
        with raises(DuplicateMemberException) as exc:
            self.interactor.check_member_list_duplicates()
        assert 'Member 1 has more than on entry.' in str(exc.value)

    def test_persist_team(self):
        mock_team = MagicMock()
        self.interactor.persist_team(mock_team)
        mock_team.set_adapter.assert_called_with(
            self.mock_adapters.team_adapter)
        mock_team.save.assert_called()

    @patch(f'{prefix}.PutTeamResponseModel')
    @patch.object(PutTeamInteractor, 'get_saved_team')
    @patch.object(PutTeamInteractor, 'check_member_list_duplicates')
    @patch.object(PutTeamInteractor, 'init_team')
    @patch.object(PutTeamInteractor, 'persist_team')
    def test_run(self, mock_persist_team,
                 mock_init_team,
                 mock_check_member_list_duplicates,
                 mock_get_saved_team,
                 mock_response_model):
        response = self.interactor.run()
        mock_get_saved_team.assert_called()
        mock_check_member_list_duplicates.assert_called()
        mock_init_team.assert_called_with(mock_get_saved_team())
        mock_persist_team.assert_called_with(mock_init_team())
        mock_response_model.assert_called_with(mock_init_team().entity_id)
        assert response == mock_response_model()

    @patch(f'{prefix}.PutTeamResponseModel')
    @patch.object(PutTeamInteractor,
                  'get_saved_team',
                  side_effect=Exception('oops'))
    @patch.object(PutTeamInteractor, 'check_member_list_duplicates')
    @patch.object(PutTeamInteractor, 'init_team')
    @patch.object(PutTeamInteractor, 'persist_team')
    def test_run_raises(self, mock_persist_team,
                        mock_init_team,
                        mock_check_member_list_duplicates,
                        mock_get_saved_team,
                        mock_response_model):
        with raises(UpdateTeamException) as exc:
            self.interactor.run()
        assert 'Team update error: oops' in str(exc.value)
        mock_get_saved_team.assert_called()
        mock_check_member_list_duplicates.assert_not_called()
        mock_init_team.assert_not_called()
        mock_persist_team.assert_not_called()
        mock_response_model.assert_not_called()
