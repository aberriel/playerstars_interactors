from playerstars_domain import Tournament, Duel
import logging
from datetime import timedelta


class GetTournamentPhaseError(BaseException):
    pass


class GetTournamentPhaseRequestModel:
    def __init__(self, player_id, tournament_id):
        self.player_id = player_id
        self.tournament_id = tournament_id


class GetTournamentPhaseResponseModel:
    def __init__(self, phase_detail):
        self.phase_detail = phase_detail

    def __call__(self, *args, **kwargs):
        return self.phase_detail if self.phase_detail else None


class GetTournamentPhaseAdapters:
    def __init__(self,
                 player_adapter,
                 team_adapter,
                 player_tournament_adapter,
                 team_tournament_adapter,
                 duel_adapter):
        self.player_adapter = player_adapter
        self.team_adapter = team_adapter
        self.player_tournament_adapter = player_tournament_adapter
        self.team_tournament_adapter = team_tournament_adapter
        self.duel_adapter = duel_adapter


class GetTournamentPhaseInteractor:
    def __init__(self, request: GetTournamentPhaseRequestModel,
                 adapters: GetTournamentPhaseAdapters):
        self.request = request
        self.adapters = adapters
        self.logger = logging.getLogger(__name__)

    def check_if_yourself(self, player_id):
        return True if player_id == self.request.player_id else False

    def get_duel_members(self, challenger_id, challenged_id):
        challenger = self.adapters.player_adapter.get_by_id(challenger_id)
        challenged = self.adapters.player_adapter.get_by_id(challenged_id)
        return [
            dict(entity_id=challenger.entity_id,
                 winner=False,
                 featured=self.check_if_yourself(challenger.entity_id),
                 player=dict(
                    nickname=challenger.user.nickname,
                    logo_path=challenger.user.profile_image)),
            dict(entity_id=challenged.entity_id,
                 winner=False,
                 featured=self.check_if_yourself(challenged.entity_id),
                 player=dict(
                     nickname=challenged.user.nickname,
                     logo_path=challenged.user.profile_image))
        ]

    def get_duels_details(self, phase):
        duels_details = list()
        for duel_id in phase.duels:
            duel: Duel = self.adapters.duel_adapter.get_by_id(duel_id)
            duels_details.append(dict(
                entity_id=duel.entity_id,
                players=self.get_duel_members(
                    duel.challenger, duel.challenged)
            ))
        return duels_details

    @staticmethod
    def get_end_date(start, duration):
        return start + timedelta(duration)

    def format_phase(self, tournament: Tournament):
        all_phases = list()
        for phase in tournament.phases:
            duels_details = self.get_duels_details(phase)

            formated_phase = dict(
                phase=phase.phase,
                start_date=phase.start_datetime,
                end_date=self.get_end_date(phase.start_datetime,
                                           tournament.level_duration),
                duels=duels_details
            )
            all_phases.append(formated_phase)

        return all_phases

    def run(self):
        tournament = self.adapters.player_tournament_adapter.get_by_id(
            self.request.tournament_id)
        if not tournament:
            raise GetTournamentPhaseError(
                f'Tournament {self.request.tournament_id} not found in'
                f' player tournaments')
        formated_phase = self.format_phase(tournament)
        response = GetTournamentPhaseResponseModel(formated_phase)
        return response
