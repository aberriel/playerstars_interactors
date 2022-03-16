from datetime import datetime
from playerstars_domain import MemberStatus, MemberType
from playerstars_interactors import (
    GetTeamByUserInteractor, GetTeamByUserRequestModel,
    GetAcceptedTeamsByUserRequestModel, GetAcceptedTeamsByUserInteractor)
from unittest.mock import MagicMock
from tests.team.utils_test_team import (
    make_team_duarte_captain_no_members, make_team_duarte_member_invited_json,
    make_team_duarte_captain_json, make_team_duarte_captain_no_members_json,
    make_console, make_team_duarte_captain, make_team_member_duarte,
    make_team_duarte_captain_rogerio_invited, team_list,
    make_team_duarte_captain_rogerio_invited_json,
    make_team_duarte_member_accepted_json)


def make_request(get_actives: bool, get_inactives: bool,
                 get_invited: bool, get_accepted: bool):
    return {
        'player_id':
            make_team_member_duarte(
                MemberType.MEMBER, MemberStatus.ACCEPTED).player_id,
        'get_actives': get_actives,
        'get_inactives': get_inactives,
        'get_invited': get_invited,
        'get_accepted': get_accepted}


association_datetime_mock = datetime(2019, 6, 7, 13, 11, 9)


def test_check_active_team():
    console_adapter = MagicMock()
    team_adapter = MagicMock()
    request_json = make_request(
        get_actives=True, get_inactives=True,
        get_accepted=True, get_invited=True)
    request = GetTeamByUserRequestModel(request_json)
    interactor = GetTeamByUserInteractor(
        request=request, team_adapter=team_adapter,
        console_adapter=console_adapter)

    # Capitão de um time cujo membro não aceitou convite
    test_result_1 = interactor.check_active_team(
        make_team_duarte_captain_no_members())
    assert not test_result_1

    # Capitão de um time que não tem membros
    test_result_2 = interactor.check_active_team(
        make_team_duarte_captain_rogerio_invited())
    assert not test_result_2

    # Capitão de um time que há membros que aceitaram o convite
    test_result_3 = interactor.check_active_team(
        make_team_duarte_captain())
    assert test_result_3


def test_get_by_user():
    console_adapter = MagicMock(get_by_id=MagicMock(
        return_value=make_console()))
    team_adapter = MagicMock(list_all=MagicMock(return_value=team_list))
    request_json = make_request(
        get_actives=True, get_inactives=True,
        get_accepted=True, get_invited=True)
    request = GetTeamByUserRequestModel(request_json)
    interactor = GetTeamByUserInteractor(
        request=request, console_adapter=console_adapter,
        team_adapter=team_adapter)

    result = interactor.run()
    assert isinstance(result, list)
    result_to_compare = [{
        'membership_type': 'CAPTAIN',
        'team': make_team_duarte_captain_json()
    }, {
        'membership_type': 'CAPTAIN',
        'team': make_team_duarte_captain_no_members_json()
    }, {
        'membership_type': 'CAPTAIN',
        'team': make_team_duarte_captain_rogerio_invited_json()
    }, {
        'membership_type': 'MEMBER',
        'team': make_team_duarte_member_invited_json()
    }, {
        'membership_type': 'MEMBER',
        'team': make_team_duarte_member_accepted_json()
    }]
    assert result == result_to_compare


def test_get_by_user_empty():
    console_adapter = MagicMock()
    team_adapter = MagicMock(lista_all=MagicMock(return_value=[]))
    request_json = make_request(True, True, True, True)
    request = GetTeamByUserRequestModel(request_json)
    interactor = GetTeamByUserInteractor(
        request=request, console_adapter=console_adapter,
        team_adapter=team_adapter)
    result = interactor.run()

    assert isinstance(result, list)
    assert result == []


def test_get_by_user_valids():
    console_adapter = MagicMock(get_by_id=MagicMock(
        return_value=make_console()))
    team_adapter = MagicMock(list_all=MagicMock(return_value=team_list))
    request_json = make_request(
        get_actives=True, get_inactives=False,
        get_accepted=True, get_invited=False)
    request = GetTeamByUserRequestModel(request_json)
    interactor = GetTeamByUserInteractor(
        request=request, console_adapter=console_adapter,
        team_adapter=team_adapter)
    result = interactor.run()

    assert isinstance(result, list)
    assert result == [{
        'membership_type': 'CAPTAIN',
        'team': make_team_duarte_captain_json()
    }, {
        'membership_type': 'MEMBER',
        'team': make_team_duarte_member_accepted_json()
    }]


team_list_valids_empty = [make_team_duarte_captain_no_members(),
                          make_team_duarte_captain_rogerio_invited()]


def test_get_by_user_valids_empty():
    console_adapter = MagicMock()
    team_adapter = MagicMock(list_all=MagicMock(
        return_value=team_list_valids_empty))
    request_json = make_request(
        get_actives=True, get_inactives=False, get_invited=False,
        get_accepted=True)
    request = GetTeamByUserRequestModel(request_json)
    interactor = GetTeamByUserInteractor(
        request=request, console_adapter=console_adapter,
        team_adapter=team_adapter)
    result = interactor.run()

    assert isinstance(result, list)
    assert result == []


def test_get_by_user_captain_valid_empty():
    console_adapter = MagicMock()
    team_adapter = MagicMock(list_all=MagicMock(
        return_value=team_list_valids_empty))
    request_json = make_request(True, False, False, False)
    request = GetTeamByUserRequestModel(request_json)
    interactor = GetTeamByUserInteractor(
        request=request, console_adapter=console_adapter,
        team_adapter=team_adapter)
    result = interactor.run()

    assert isinstance(result, list)
    assert result == []


def test_get_by_user_only_accepted():
    console_adapter = MagicMock(get_by_id=MagicMock(
        return_value=make_console()))
    team_adapter = MagicMock(list_all=MagicMock(return_value=team_list))
    request_json = make_request(
        get_actives=False, get_inactives=False,
        get_invited=False, get_accepted=True)
    request = GetTeamByUserRequestModel(request_json)
    interactor = GetTeamByUserInteractor(
        request=request, console_adapter=console_adapter,
        team_adapter=team_adapter)
    result = interactor.run()

    assert isinstance(result, list)
    assert result == [{
        'membership_type': 'MEMBER',
        'team': make_team_duarte_member_accepted_json()
    }]


def test_get_accepted_by_user():
    console_adapter = MagicMock(get_by_id=MagicMock(
        return_value=make_console()))
    team_adapter = MagicMock(list_all=MagicMock(return_value=team_list))
    request = GetAcceptedTeamsByUserRequestModel(
        "f930959f-63ec-4478-89d6-7d84bb748b37")
    interactor = GetAcceptedTeamsByUserInteractor(
        request, team_adapter, console_adapter)
    result = interactor.run()
    assert result == [{
        'membership_type': 'CAPTAIN',
        'team': make_team_duarte_captain_json()
    }, {
        'membership_type': 'CAPTAIN',
        'team': make_team_duarte_captain_no_members_json()
    }, {
        'membership_type': 'CAPTAIN',
        'team': make_team_duarte_captain_rogerio_invited_json()
    }, {
        'membership_type': 'MEMBER',
        'team': make_team_duarte_member_accepted_json()
    }]
