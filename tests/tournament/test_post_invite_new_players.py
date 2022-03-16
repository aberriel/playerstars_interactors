from collections import namedtuple
from unittest.mock import MagicMock, patch

from playerstars_domain import DuelMemberType as MemberType
from pytest import fixture

from playerstars_interactors.tournament.post_invite_new_players import \
    PostInviteNewPlayersAdapters, PostInviteNewPlayersInteractor, \
    PostInviteNewPlayersRequestModel, PostInviteNewPlayersResponseModel


@fixture
def interactor():
    def factory(mock_request=MagicMock(),
                mock_adapters=MagicMock()):
        Interactor = namedtuple('Interactor',
                                'interactor, request, adapters')
        testing_interactor = PostInviteNewPlayersInteractor(
            request=mock_request,
            adapters=mock_adapters)
        return Interactor(testing_interactor,
                          mock_request,
                          mock_adapters)
    return factory


def test_post_invite_new_players_add_new_members(interactor):
    factory = interactor()
    player1 = MagicMock()
    player2 = MagicMock()

    factory.interactor.request.new_players = [player1, player2]
    tournament = MagicMock()
    result = factory.interactor.add_new_members(tournament)
    assert result
    assert tournament.members.append.call_count == 2


def test_post_invite_new_players_get_tournament_adapter(interactor):
    factory = interactor()
    factory.request.member_type = MemberType.PLAYER
    result = factory.interactor.get_tournament_adapter()
    assert result == factory.adapters.player_tournament_adapter


@patch('playerstars_interactors.tournament.post_invite_new_players.'
       'report_failed_invites')
@patch('playerstars_interactors.tournament.post_invite_new_players.'
       'send_invites')
def test_post_invite_new_players_run(send, report, interactor):
    factory = interactor()
    tournament = MagicMock()
    factory.adapters.player_tournament_adapter = MagicMock(
        get_by_id=MagicMock(return_value=tournament))
    factory.interactor.get_tournament_adapter = MagicMock(
        return_value=factory.adapters.player_tournament_adapter)
    factory.interactor.add_new_members = MagicMock()

    result = factory.interactor.run()
    assert result
    factory.interactor.get_tournament_adapter.assert_called_once()
    factory.interactor.add_new_members.assert_called_once_with(tournament)
    send.assert_called_once()
    report.assert_called_once()


def test_post_invite_new_players_models():
    request = PostInviteNewPlayersRequestModel(
        player_id='schrubles',
        member_type=MemberType.PLAYER,
        data=dict(
            tournament_id='aloalo',
            new_players=['1234', '45678'])
    )
    assert request
    adapters = PostInviteNewPlayersAdapters(
        MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock()
    )
    assert adapters
    response = PostInviteNewPlayersResponseModel(MagicMock())
    assert response()
