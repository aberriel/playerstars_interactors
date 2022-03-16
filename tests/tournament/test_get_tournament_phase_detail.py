from playerstars_interactors.tournament.get_tournament_phase_detail import (
    GetTournamentPhaseAdapters, GetTournamentPhaseError,
    GetTournamentPhaseInteractor, GetTournamentPhaseRequestModel
)
from tests.player.player_utils import \
    player1, tournament, duel1
from playerstars_domain import TournamentStatus, TournamentPhase
from unittest.mock import MagicMock, patch
import pytest
from datetime import datetime


now = datetime.utcnow()


def get_interactor():
    request = GetTournamentPhaseRequestModel(
        'player123', 'tournament123')
    tournament.phases = [TournamentPhase(
        phase=TournamentStatus.PHASE1,
        start_datetime=now,
        duels=['duel1', 'duel2']
    )]
    adapters = GetTournamentPhaseAdapters(
        player_adapter=MagicMock(
            get_by_id=MagicMock(return_value=player1)
        ),
        team_adapter=MagicMock(),
        team_tournament_adapter=MagicMock(),
        player_tournament_adapter=MagicMock(
            get_by_id=MagicMock(return_value=tournament)),
        duel_adapter=MagicMock(
            get_by_id=MagicMock(return_value=duel1)
        )
    )
    return GetTournamentPhaseInteractor(
        request=request,
        adapters=adapters
    )


@patch('playerstars_interactors.tournament.get_tournament_detail.'
       'format_tournament')
def test_run(format):
    interactor = get_interactor()
    response = interactor.run()
    assert response()
    interactor.adapters.player_tournament_adapter.get_by_id.\
        assert_called_once()
    assert interactor.adapters.duel_adapter.get_by_id.call_count == 2
    assert interactor.adapters.player_adapter.get_by_id.call_count == 4
    # format.assert_called_once()


@patch('playerstars_interactors.tournament.get_tournament_detail.'
       'format_tournament')
def test_run_not_found(format):
    interactor = get_interactor()
    interactor.adapters.player_tournament_adapter.get_by_id = MagicMock(
        return_value=None)
    with pytest.raises(GetTournamentPhaseError) as excinfo:
        interactor.run()
    assert "Tournament tournament123 not found in player tournaments"\
           in str(excinfo.value)
