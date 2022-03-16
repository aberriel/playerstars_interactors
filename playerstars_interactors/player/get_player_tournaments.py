from playerstars_interactors.tournament.tournament_detail_util import \
    format_tournament
from playerstars_domain import DuelMemberType
import logging


class GetPlayerTournamentsError(BaseException):
    pass


class GetPlayerTournamentsRequestModel:
    def __init__(self, player_id, param=None):
        self.player_id = player_id
        self.status = None
        if param:
            self.status = param.get('status').split('-') \
                if param.get('status') else None


class GetPlayerTournamentsResponseModel:
    def __init__(self, tournaments):
        self.tournaments = tournaments

    def __call__(self, *args, **kwargs):
        return self.tournaments if self.tournaments else list()


class GetPlayerTournamentsInteractor:
    def __init__(self, request: GetPlayerTournamentsRequestModel,
                 player_adapter, team_adapter,
                 team_tournament_adapter,
                 player_tournament_adapter,
                 tournament_review_time):
        self.request = request
        self.player_adapter = player_adapter
        self.team_adapter = team_adapter
        self.team_tournament_adapter = team_tournament_adapter
        self.player_tournament_adapter = player_tournament_adapter
        self.tournament_review_time = tournament_review_time
        self.logger = logging.getLogger(__name__)

    def get_individual_tournaments(self):
        duel_type = DuelMemberType.PLAYER

        tournaments = self.player_tournament_adapter.filter(
            status__is_in=self.request.status) if self.request.status \
            else self.player_tournament_adapter.list_all()

        self.logger.info('player_id: ' + self.request.player_id)
        self.logger.info('status: ' + str(self.request.status))
        self.logger.info('all player tournaments')
        self.logger.info(tournaments)

        individual_tournaments = [
            format_tournament(x, duel_type, self.player_adapter,
                              self.tournament_review_time)
            for x in tournaments
            if x.is_member(self.request.player_id)
        ]

        self.logger.info('specific player tournaments')
        self.logger.info(individual_tournaments)
        return individual_tournaments

    def get_team_tournaments(self):
        duel_type = DuelMemberType.TEAM

        team_tournaments = list()
        tournaments = self.team_tournament_adapter.filter(
            status__is_in=self.request.status) if self.request.status \
            else self.team_tournament_adapter.list_all()

        for tourney in tournaments:
            for member in tourney.members:
                team = self.team_adapter.get_by_id(member.member_id)
                members_ids = [x.player_id for x in team.get_active_members()]
                if self.request.player_id in members_ids:
                    team_tournaments.append(
                        format_tournament(tourney, duel_type,
                                          self.player_adapter,
                                          self.tournament_review_time))
                    break
        return team_tournaments

    def run(self):
        individual_tournaments = self.get_individual_tournaments()
        team_tournaments = self.get_team_tournaments()
        player_tournaments = individual_tournaments + team_tournaments
        response = GetPlayerTournamentsResponseModel(player_tournaments)
        return response
