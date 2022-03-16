# noinspection PyProtectedMember
from unittest import TestCase
from unittest.mock import MagicMock, patch

from playerstars_domain import DuelMemberType
from pytest import raises, fixture

from playerstars_interactors import EndDuelInteractor
from playerstars_interactors.duel.end_duel import LoadDuelException, \
    LoadMemberException, JudgeException


@fixture
def interactor_factory():
    def interactor(mock_request=MagicMock(),
                   mock_s3name=MagicMock(),
                   mock_s3url=MagicMock(),
                   mock_adapters=MagicMock(),
                   mock_judge_matrix=MagicMock()):
        return EndDuelInteractor(
            request=mock_request,
            s3_bucket_name=mock_s3name,
            s3_bucket_url=mock_s3url,
            adapters=mock_adapters,
            judge_matrix=mock_judge_matrix)
    return interactor


# noinspection PyProtectedMember
def test_load_duel(interactor_factory):
    interactor = interactor_factory()
    interactor._load_duel()


# noinspection PyProtectedMember
def test_load_duel_raises(interactor_factory):
    mock_adapters = MagicMock()
    mock_adapters.duel_adapter.get_by_id = MagicMock(side_effect=ValueError('oops'))
    interactor = interactor_factory(mock_adapters=mock_adapters)
    with raises(LoadDuelException) as excinfo:
        interactor._load_duel()
    TestCase().assertIn('ValueError(oops)', str(excinfo.value))


# noinspection PyProtectedMember
@patch.object(EndDuelInteractor, 'get_challenger')
@patch.object(EndDuelInteractor, 'duel', MagicMock(member_type=DuelMemberType.PLAYER))
def test_load_challenger(mock_get_challenger, interactor_factory):
    interactor = interactor_factory()
    interactor._load_challenger()
    mock_get_challenger.assert_called_once()


# noinspection PyProtectedMember
@patch.object(EndDuelInteractor, 'get_challenger', side_effect=ValueError('oops'))
def test_load_challenger_raises(mock_get_challenger, interactor_factory):
    interactor = interactor_factory()
    with raises(LoadMemberException) as excinfo:
        interactor._load_challenger()
    assert 'oops' in str(excinfo.value)


# noinspection PyProtectedMember
@patch.object(EndDuelInteractor, 'get_challenged')
@patch.object(EndDuelInteractor, 'duel', MagicMock(member_type=DuelMemberType.PLAYER))
def test_load_challenged(mock_get_challenged, interactor_factory):
    interactor = interactor_factory()
    interactor._load_challenged()
    mock_get_challenged.assert_called_once()


# noinspection PyProtectedMember
@patch.object(EndDuelInteractor, 'get_challenged', side_effect=ValueError('oops'))
def test_load_challenged_raises(mock_get_challenged, interactor_factory):
    interactor = interactor_factory()
    with raises(LoadMemberException) as excinfo:
        interactor._load_challenged()
    assert 'oops' in str(excinfo.value)


# noinspection PyProtectedMember
@patch.object(EndDuelInteractor, 'judge_duel', side_effect=ValueError('oops'))
@patch.object(EndDuelInteractor, 'duel_ready_to_finish', return_value=True)
def test_judge_raises(mock_is_duel_ready, mock_judge_duel, interactor_factory):
    interactor = interactor_factory()
    with raises(JudgeException) as excinfo:
        interactor._judge_duel()
    assert 'oops' in str(excinfo.value)
