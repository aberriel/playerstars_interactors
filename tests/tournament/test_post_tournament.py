from collections import namedtuple
from datetime import datetime
from typing import List
from unittest.mock import MagicMock, patch, call
from uuid import uuid4

from playerstars_domain import (TournamentMember,
                                TournamentMemberStatus,
                                PlayerTournament,
                                TeamTournament,
                                TournamentStatus,
                                NotificationType,
                                DuelMemberType as MemberType)
from playerstars_domain.utils.datetime_helper import aware_utc
from pytest import fixture

from playerstars_interactors.tournament.post_tournament_interactor import \
    PostTournamentRestModel, PostTournamentAdapters, \
    PostTournamentInteractor, FailedInvite


@fixture
def post_request():
    def request_factory(mock_start: datetime, mock_members: List[str]):
        return dict(
            game_id='game id',
            console_id='console id',
            duel_type='PLAYER',
            star_amount=3,
            start_datetime=mock_start.isoformat(),
            phase_duration=300,
            phases_per_day=4,
            member_amount=16,
            members=mock_members)

    def assert_request_model(request_model, mock_start, mock_members):
        assert request_model.game_id == 'game id'
        assert request_model.console_id == 'console id'
        assert request_model.duel_type == MemberType.PLAYER
        assert request_model.star_amount == 3
        assert request_model.start_datetime == mock_start
        assert request_model.phase_duration == 300
        assert request_model.phases_per_day == 4
        assert request_model.member_amount == 16
        assert request_model.members == mock_members

    return namedtuple('Request', 'factory, asserter')(request_factory,
                                                      assert_request_model)


def test_post_tournament_request_unserialize(post_request):
    mock_start = aware_utc(datetime(2020, 1, 1, 14, 30, 0))
    mock_members = [str(uuid4()) for _ in range(20)]
    json_data = post_request.factory(mock_start, mock_members)

    request_model = PostTournamentRestModel.from_json(json_data)

    post_request.asserter(request_model, mock_start, mock_members)


def test_post_tournament_adapters():
    mock_tournament = MagicMock()
    mock_console = MagicMock()
    mock_values = MagicMock()
    mock_notif_gql = MagicMock()
    adapters = PostTournamentAdapters(mock_tournament,
                                      mock_console,
                                      mock_values,
                                      mock_notif_gql)

    assert adapters.tournament == mock_tournament
    assert adapters.console == mock_console
    assert adapters.values == mock_values


@fixture
def interactor():
    def factory(mock_request=MagicMock(),
                mock_adapters=MagicMock(),
                mock_owner=MagicMock()):
        Interactor = namedtuple('Interactor',
                                'interactor, request, adapters, owner')
        testing_interactor = PostTournamentInteractor(
            request=mock_request,
            adapters=mock_adapters,
            player_id=mock_owner)
        return Interactor(testing_interactor,
                          mock_request,
                          mock_adapters,
                          mock_owner)
    return factory


# noinspection PyProtectedMember
def test_post_tournament_interactor__get_values(interactor):
    factory = interactor()
    result = factory.interactor._get_values()

    factory.adapters.values.get_by_id.assert_called_with('1')
    assert result == factory.adapters.values.get_by_id()


# noinspection PyProtectedMember
def test_post_tournament_interactor__fill_award_values(interactor):
    factory = interactor()
    mock_values = MagicMock()
    factory.interactor._fill_award_values(mock_values)

    first = mock_values.championship_award_first_place_perc
    second = mock_values.championship_award_second_place_perc
    third = mock_values.championship_award_third_place_perc

    assert factory.interactor.awards.first == first
    assert factory.interactor.awards.second == second
    assert factory.interactor.awards.third == third


# noinspection PyProtectedMember
def test_post_tournament_interactor__member_factory():
    mock_id = MagicMock()
    result = PostTournamentInteractor._member_factory(mock_id)

    assert isinstance(result, TournamentMember)
    assert result.member_id == mock_id
    assert result.status == TournamentMemberStatus.INVITED


# noinspection PyProtectedMember
def test_post_tournament_interactor__fill_members(interactor):
    factory = interactor()
    factory.request.members = ['4', '2']
    factory.interactor._fill_members()

    for i, member_id in enumerate(factory.request.members):
        assert isinstance(factory.interactor.members[i], TournamentMember)
        assert factory.interactor.members[i].member_id == member_id


# noinspection PyProtectedMember
def test_post_tournament_interactor__fill_console(interactor):
    factory = interactor()

    factory.interactor._fill_console()

    mock_console_adapter = factory.adapters.console
    mock_request = factory.request

    mock_console_adapter.get_by_id.assert_called_with(mock_request.console_id)


# noinspection PyProtectedMember
def test_post_tournament_interactor__fill_game(interactor):
    factory = interactor()

    mock_games = [MagicMock(entity_id=str(x)) for x in range(10)]
    factory.request.game_id = '7'
    console = MagicMock(games=mock_games)

    factory.interactor._fill_game(console)

    assert factory.interactor.game == mock_games[7]


# noinspection PyProtectedMember
def test_post_tournament_interactor__get_tournament_class(interactor):
    factory = interactor()

    factory.request.duel_type = MemberType.PLAYER
    assert factory.interactor._get_tournament_class() == PlayerTournament

    factory.request.duel_type = MemberType.TEAM
    assert factory.interactor._get_tournament_class() == TeamTournament


# noinspection PyProtectedMember
@patch('playerstars_interactors.tournament.post_tournament_interactor'
       '.PostTournamentRestModel')
def test_post_tournament_interactor__make_response(mock_rest_model,
                                                   interactor):
    factory = interactor()
    factory.interactor.tournament = MagicMock()
    result = factory.interactor._make_response()

    factory.request.to_json.assert_called_once()
    mock_rest_model.from_json.assert_called_with(factory.request.to_json())

    assert result == mock_rest_model.from_json()

    assert result.entity_id == factory.interactor.tournament.entity_id


# noinspection PyProtectedMember
@patch.object(PostTournamentInteractor, '_invite_member')
def test_post_tournament_interactor__send_invites(mock_invite_member,
                                                  interactor):
    factory = interactor()
    factory.interactor.members = [MagicMock(), MagicMock()]
    factory.interactor._send_invites()

    mock_invite_member.assert_has_calls([
        call(factory.interactor.members[0]),
        call(factory.interactor.members[1])])


# noinspection PyProtectedMember
@patch('playerstars_interactors.tournament.post_tournament_interactor'
       '.Notification')
@patch.object(PostTournamentInteractor, '_format_complement')
def test_post_tournament_interactor__invite_member(mock_format_complement,
                                                   mock_notification,
                                                   interactor):
    factory = interactor()
    mock_member = MagicMock()
    factory.interactor.tournament = MagicMock()
    factory.interactor.game = MagicMock()
    factory.interactor._invite_member(mock_member)

    mock_format_complement.assert_called_once()
    mock_notification.assert_called_with(
        player_id=mock_member.member_id,
        notification_type=NotificationType.CHAMPIONSHIP_INVITE_PLAYER,
        championship_id=factory.interactor.tournament.entity_id,
        notification_complement=mock_format_complement(),
        notification_image=factory.interactor.game.logo_path)
    mock_notification().set_adapter.assert_called_with(
        factory.adapters.notification_adapter)
    mock_notification().save.assert_called_once()


# noinspection PyProtectedMember
@patch('playerstars_interactors.tournament.post_tournament_interactor'
       '.Notification', side_effect=ValueError('Errou!'))
@patch.object(PostTournamentInteractor, '_get_tb')
def test_post_tournament_interactor__invite_member_raise(mock_get_tb,
                                                         mock_notification,
                                                         interactor):
    factory = interactor()
    mock_member = MagicMock()
    factory.interactor.tournament = MagicMock()
    factory.interactor.game = MagicMock()
    factory.interactor._invite_member(mock_member)

    assert factory.interactor.failed_invites == [
        FailedInvite(mock_member, 'ValueError', 'Errou!', mock_get_tb())]


# noinspection PyProtectedMember
@patch.object(PostTournamentInteractor, '_failed_invites_count',
              return_value=1)
def test_post_tournament_interactor__report_failed_invites(
        mock_failed_invite_count,
        interactor):
    mock_tournament = MagicMock()
    mock_logger = MagicMock()
    mock_failed = MagicMock()

    factory = interactor()
    factory.interactor.tournament = mock_tournament
    factory.interactor.logger = mock_logger
    factory.interactor.failed_invites = [mock_failed]
    factory.interactor._report_failed_invites()

    mock_failed_invite_count.assert_called_once()
    mock_logger.error.assert_has_calls([
        call(f'1 invites failed on tournament {mock_tournament.entity_id}:'),
        call(f'Failed invite:\t'
             f'member_id: {mock_failed.member.member_id}\t'
             f'error: {mock_failed.exception}\t'
             f'Message: {mock_failed.message}\t'
             f'Traceback: {mock_failed.traceback}')
    ])


@patch('playerstars_interactors.tournament.post_tournament_interactor.sys')
@patch('playerstars_interactors.tournament.post_tournament_interactor'
       '.format_exception', return_value=['1', '2'])
def test_post_tournament_interactor__get_tb(mock_format_exception,
                                            mock_sys):
    mock_etype, mock_value, mock_traceback = (MagicMock(),
                                              MagicMock(),
                                              MagicMock())
    mock_sys.exc_info = MagicMock(return_value=(mock_etype,
                                                mock_value,
                                                mock_traceback))

    result = PostTournamentInteractor._get_tb()

    mock_sys.exc_info.assert_called_once()
    mock_format_exception.assert_called_with(mock_etype,
                                             mock_value,
                                             mock_traceback)
    assert result == '1\n2'


def test_post_tournament_interactor__failed_count(interactor):
    factory = interactor()
    factory.interactor.failed_invites = list(range(42))
    result = factory.interactor._failed_invites_count()

    assert result == 42


@patch.object(PostTournamentInteractor, '_get_values')
@patch.object(PostTournamentInteractor, '_fill_award_values')
@patch.object(PostTournamentInteractor, '_fill_members')
@patch.object(PostTournamentInteractor, '_fill_console')
@patch.object(PostTournamentInteractor, '_fill_game')
@patch.object(PostTournamentInteractor, '_make_response')
@patch.object(PostTournamentInteractor, '_get_tournament_class')
@patch('playerstars_interactors.tournament.post_tournament_interactor'
       '.aware_now')
def test_post_tournament_interactor_run(mock_aware_now,
                                        mock_get_tournament_class,
                                        mock_make_response,
                                        mock_fill_game,
                                        mock_fill_console,
                                        mock_fill_members,
                                        mock_fill_award_values,
                                        mock_get_values,
                                        interactor):
    factory = interactor()
    factory.interactor.game = MagicMock()
    factory.interactor.console = MagicMock()
    factory.interactor.awards = MagicMock(first=3, second=5, third=7)
    factory.interactor.members = MagicMock()
    result = factory.interactor.run()

    mock_get_values.assert_called_once()
    mock_fill_award_values.assert_called_with(mock_get_values())
    mock_fill_members.assert_called_once()
    mock_fill_console.assert_called_once()
    mock_fill_game.assert_called_with(factory.interactor.console)
    mock_get_tournament_class.assert_called_once()

    mock_get_tournament_class().assert_called_with(
        game=factory.interactor.game,
        console=factory.interactor.console,
        award_first_place_perc=factory.interactor.awards.first,
        award_second_place_perc=factory.interactor.awards.second,
        award_third_place_perc=factory.interactor.awards.third,
        price_to_enter=factory.request.star_amount,
        member_amount=factory.request.member_amount,
        level_duration=factory.request.phase_duration,
        levels_per_day=factory.request.phases_per_day,
        start_datetime=factory.request.start_datetime,
        members=factory.interactor.members,
        status=TournamentStatus.WAITING_START,
        creation_datetime=mock_aware_now())

    mock_tournament = mock_get_tournament_class()()
    mock_tournament.set_adapter.assert_called_with(
        factory.adapters.tournament)

    mock_tournament.save.assert_called_once()

    mock_make_response.assert_called_once()
    assert result == factory.interactor.run()
