from playerstars_interactors.tournament.get_tournament_detail import (
    GetTournamentInteractor, GetTournamentRequestModel, GetTournamentAdapters,
    GetTournamentError
)
from unittest.mock import MagicMock, patch
import pytest


@patch('playerstars_interactors.tournament.get_tournament_detail.'
       'format_tournament')
def test_run(format):
    request = GetTournamentRequestModel('player123', 'tournament123')
    adapters = GetTournamentAdapters(
        player_adapter=MagicMock(),
        team_adapter=MagicMock(),
        team_tournament_adapter=MagicMock(),
        player_tournament_adapter=MagicMock()
    )
    interactor = GetTournamentInteractor(
        request=request,
        adapters=adapters,
        tournament_review_time='1111111'
    )
    response = interactor.run()
    assert response()
    interactor.adapters.player_tournament_adapter.get_by_id.\
        assert_called_once()
    format.assert_called_once()


@patch('playerstars_interactors.tournament.get_tournament_detail.'
       'format_tournament')
def test_run_not_found(format):
    request = GetTournamentRequestModel('player123', 'tournament123')
    adapters = GetTournamentAdapters(
        player_adapter=MagicMock(),
        team_adapter=MagicMock(),
        team_tournament_adapter=MagicMock(),
        player_tournament_adapter=MagicMock(
            get_by_id=MagicMock(return_value=None))
    )
    interactor = GetTournamentInteractor(
        request=request,
        adapters=adapters,
        tournament_review_time='1111111'
    )
    with pytest.raises(GetTournamentError) as excinfo:
        interactor.run()
    assert "Tournament tournament123 not found in player tournaments"\
           in str(excinfo.value)
