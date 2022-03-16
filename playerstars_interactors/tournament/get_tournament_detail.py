from playerstars_interactors.tournament.tournament_detail_util import \
    format_tournament
from playerstars_domain import DuelMemberType
import logging


class GetTournamentError(BaseException):
    pass


class GetTournamentRequestModel:
    def __init__(self, player_id, tournament_id):
        self.player_id = player_id
        self.tournament_id = tournament_id


class GetTournamentResponseModel:
    def __init__(self, tournament):
        self.tournament = tournament

    def __call__(self, *args, **kwargs):
        return self.tournament if self.tournament else None


class GetTournamentAdapters:
    def __init__(self,
                 player_adapter,
                 team_adapter,
                 player_tournament_adapter,
                 team_tournament_adapter):
        self.player_adapter = player_adapter
        self.team_adapter = team_adapter
        self.player_tournament_adapter = player_tournament_adapter
        self.team_tournament_adapter = team_tournament_adapter


class GetTournamentInteractor:
    def __init__(self, request: GetTournamentRequestModel,
                 adapters: GetTournamentAdapters,
                 tournament_review_time):
        self.request = request
        self.adapters = adapters
        self.tournament_review_time = tournament_review_time
        self.logger = logging.getLogger(__name__)

    def run(self):
        tournament = self.adapters.player_tournament_adapter.get_by_id(
            self.request.tournament_id)
        if not tournament:
            raise GetTournamentError(
                f'Tournament {self.request.tournament_id} not found in'
                f' player tournaments')
        formated_tournament = format_tournament(
            tournament, DuelMemberType.PLAYER, self.adapters.player_adapter,
            self.tournament_review_time)
        response = GetTournamentResponseModel(formated_tournament)
        return response
