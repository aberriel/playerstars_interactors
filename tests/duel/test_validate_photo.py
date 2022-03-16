
from playerstars_interactors.duel.validate_photo import (
    ValidatePhotoAdapters, ValidatePhotoException, ValidatePhotoInteractor,
    ValidatePhotoRequestModel, ValidatePhotoResponseModel,
    UploadImageException)
from pytest import fixture
from unittest import TestCase
from unittest.mock import MagicMock, patch
from playerstars_domain import (
    ComponentResult, DuelMemberType, ImageValidity)
import pytest


prefix = 'playerstars_interactors.duel.validate_photo'


def test_request_model():
    response = ValidatePhotoRequestModel({
        'image_base64': 'teste/url',
        'duel_id': '1234',
        'player_id': '0987',
        'result': 'WINNER'
    })
    assert response
    assert response.photo == 'teste/url'
    assert response.duel_id == '1234'
    assert response.player_id == '0987'
    assert response.claimed_result == 'WINNER'


def test_response_model():
    result_mock = MagicMock()
    response = ValidatePhotoResponseModel(result_mock)

    assert response
    assert response.informed_result == result_mock.inform.value
    assert response.image_validity == result_mock.image_validity.value
    assert response.validation_result == result_mock.report_state.value


def test_response_model__call():
    result_mock = MagicMock()
    response = ValidatePhotoResponseModel(result_mock)
    call_result = response()

    assert call_result == {
        "informed_result": result_mock.inform.value,
        "image_validity": result_mock.image_validity.value,
        "validation_result": result_mock.report_state.value
    }


def test_adapters():
    player_adapter_mock = MagicMock()
    team_adapter_mock = MagicMock()
    duel_adapter_mock = MagicMock()
    values_adapter_mock = MagicMock()
    adapters = ValidatePhotoAdapters(
        player_adapter=player_adapter_mock,
        team_adapter=team_adapter_mock,
        duel_adapter=duel_adapter_mock,
        values_adapter=values_adapter_mock
    )

    assert adapters
    assert adapters.player_adapter == player_adapter_mock
    assert adapters.team_adapter == team_adapter_mock
    assert adapters.duel_adapter == duel_adapter_mock
    assert adapters.values_adapter == values_adapter_mock


# Factory = namedtuple('Factory', 'interactor, mock_console_adapter')


@fixture(scope='class')
def interactor_fixture(request):
    def factory(
            player_adapter=MagicMock(),
            team_adapter=MagicMock(),
            duel_adapter=MagicMock(),
            values_adapter=MagicMock()):
        requestm = MagicMock()
        adapters = MagicMock(
            player_adapter=player_adapter,
            team_adapter=team_adapter,
            duel_adapter=duel_adapter,
            values_adapter=values_adapter
        )
        interactor = ValidatePhotoInteractor(
            request=requestm, adapters=adapters,
            s3_bucket_name='bucket-name', s3_bucket_url='bucket-url')
        return interactor
    request.cls.factory = factory


@pytest.mark.usefixtures('interactor_fixture')
class TestValidatePhotoInteractor(TestCase):
    def setUp(self):
        fac = TestValidatePhotoInteractor.factory()
        self.interactor: ValidatePhotoInteractor = fac
        self.adapters = fac.adapters
        self.request = fac.request

    def tearDown(self):
        pass

    def test_init(self):
        assert self.interactor.adapters == self.adapters
        assert self.interactor.request == self.request

    @patch(f'{prefix}.upload_photo_and_return_url')
    def test_upload_image(self, upload_mock):
        result = self.interactor.upload_image()
        upload_mock.assert_called_with(
            sent_image=self.interactor.request.photo,
            unique_name=f'duel_{self.request.duel_id}_'
            f'{self.request.player_id}',
            s3_bucket_name=self.interactor.s3_bucket_name,
            s3_bucket_url=self.interactor.s3_bucket_url
        )
        assert result == upload_mock()

    @patch(f'{prefix}.upload_photo_and_return_url',
           side_effect=Exception('oops'))
    def test_upload_image_exception(self, upload_mock):
        with pytest.raises(UploadImageException) as e:
            self.interactor.upload_image()
        assert 'Error uploading result image' in str(e.value)

    @patch.object(ValidatePhotoInteractor, 'get_component_result')
    @patch(f'{prefix}.DuelComponentResult')
    def test_get_claimed_result_data(self, dcr_mock, gcr_mock):
        result = self.interactor.get_claimed_result_data('image-url')
        assert result
        gcr_mock.assert_called()
        gcr_mock.assert_called_with(
            self.interactor.request.claimed_result
        )
        dcr_mock.assert_called()
        dcr_mock.assert_called_with(
            result=gcr_mock(),
            result_image='image-url'
        )

    def test_get_component_result(self):
        result = self.interactor.get_component_result('victory')
        assert result
        assert result == ComponentResult.WINNER

    def test_get_team_captain_tag_name(self):
        team = MagicMock()
        captain_tag_name = self.interactor.get_team_captain_tag_name(
            team, 'c123')
        assert captain_tag_name
        self.interactor.adapters.player_adapter.get_by_id.assert_called()
        self.interactor.adapters.player_adapter.get_by_id.assert_called_with(
            team.captain.player_id
        )
        self.interactor.adapters.player_adapter.get_by_id().\
            get_tag_name.assert_called()
        self.interactor.adapters.player_adapter.get_by_id(). \
            get_tag_name.assert_called_with('c123')

    @patch.object(ValidatePhotoInteractor, 'compare_result_with_image')
    @patch.object(ValidatePhotoInteractor, 'get_team_captain_tag_name')
    @patch(f'{prefix}.PlayerDuelInfo')
    def test_process_member_result(self, pdi_mock, gtctn_mock, crwi_mock):
        member_mock = MagicMock()
        duel_mock = MagicMock()
        duel_result_mock = MagicMock()
        player_duel_info = self.interactor.process_member_result(
            duel_result_mock, member_mock, duel_mock)
        assert player_duel_info
        gtctn_mock.assert_called_with(
            member_mock, duel_mock.console.entity_id)
        crwi_mock.assert_called_with(
            duel_result_mock, gtctn_mock(), duel_mock.game.entity_id)
        pdi_mock.get_player_duel_info.assert_called_with(
            duel_member_result=duel_result_mock,
            image_validation=crwi_mock()
        )

    @patch.object(ValidatePhotoInteractor, 'get_validator_class_name')
    @patch(f'{prefix}.check_image')
    def test_compare_result_with_image(self, ci_mock, gvcn_mock):
        result = MagicMock()
        response = self.interactor.compare_result_with_image(
            result, 'ptn', 'g123')
        assert response
        gvcn_mock.assert_called_with('g123')
        ci_mock.assert_called_with(
            result, 'ptn', gvcn_mock(), self.interactor.logger
        )

    def test_compare_result_with_image_not_sent(self):
        response = self.interactor.compare_result_with_image(
            None, 'ptn', 'g123')
        assert response == ImageValidity.NOT_SENT

    def test_get_validator_class_name(self):
        self.interactor.adapters.values_adapter.list_all = MagicMock(
            return_value=[MagicMock(
                validator_maps=[MagicMock(game_id='g123')])])
        result = self.interactor.get_validator_class_name('g123')
        assert result
        self.interactor.adapters.values_adapter.list_all.assert_called()

    def test_get_member_player(self):
        duel_mock = MagicMock(member_type=DuelMemberType.PLAYER)
        member = self.interactor.get_member(duel_mock)
        assert member
        self.interactor.adapters.player_adapter.get_by_id.assert_called_with(
            self.interactor.request.player_id)

    def test_get_member_team(self):
        self.interactor.adapters.team_adapter.get_by_id.call_count = 0
        duel_mock = MagicMock(member_type=DuelMemberType.TEAM)
        member = self.interactor.get_member(duel_mock)
        assert member
        self.interactor.adapters.player_adapter.get_by_id.assert_called_with(
            self.interactor.request.player_id)
        assert self.interactor.adapters.team_adapter.get_by_id.call_count == 2
        self.interactor.adapters.\
            team_adapter.get_by_id.assert_called_with(
                duel_mock.challenged
            )

    def test_check_challenger_or_challenged_player(self):
        self.interactor.request.player_id = 'player123'
        duel = MagicMock(member_type=DuelMemberType.PLAYER,
                         challenger='player123')
        result = self.interactor.check_challenger_or_challenged(duel)
        assert result

    def test_check_challenger_or_challenged_team(self):
        self.interactor.request.player_id = 'player123'
        duel = MagicMock(member_type=DuelMemberType.TEAM,
                         challenger='player123')
        result = self.interactor.check_challenger_or_challenged(duel)
        assert result

    @patch.object(ValidatePhotoInteractor, 'check_challenger_or_challenged')
    def test_update_duel(self, ccoc_mock):
        duel_mock = MagicMock()
        duel_info_mock = MagicMock()
        claimed_result = MagicMock()
        self.interactor.update_duel(duel_mock, duel_info_mock, claimed_result)
        duel_mock.save.assert_called()
        ccoc_mock.assert_called_with(duel_mock)
        assert duel_mock.challenger_duel_info == duel_info_mock.report_state

    @patch.object(ValidatePhotoInteractor, 'check_challenger_or_challenged',
                  return_value=False)
    def test_update_duel2(self, ccoc_mock):
        duel_mock = MagicMock()
        duel_info_mock = MagicMock()
        claimed_result = MagicMock()
        self.interactor.update_duel(duel_mock, duel_info_mock, claimed_result)
        duel_mock.save.assert_called()
        ccoc_mock.assert_called_with(duel_mock)
        assert duel_mock.challenged_duel_info == duel_info_mock.report_state

    @patch.object(ValidatePhotoInteractor, 'get_member')
    @patch.object(ValidatePhotoInteractor, 'upload_image')
    @patch.object(ValidatePhotoInteractor, 'get_claimed_result_data')
    @patch.object(ValidatePhotoInteractor, 'process_member_result')
    def test_run(self, pmr_mock, gcrd_mock, ui_mock, gm_mock):
        result = self.interactor.run()
        assert result
        assert isinstance(result, ValidatePhotoResponseModel)

    @patch.object(ValidatePhotoInteractor, 'get_member',
                  side_effect=BaseException('oops'))
    def test_run_exception(self, gm_mock):
        with pytest.raises(ValidatePhotoException) as e:
            self.interactor.run()
        assert 'Error during photo validation' in str(e.value)
