from playerstars_adapters import (
    PlayerAdapter,
    TeamAdapter)
from playerstars_domain import (
    DuelMemberType,
    MemberStatus,
    MemberType,
    Player,
    Team)

import logging


class GetOpponentCandidateListException(BaseException):
    pass


class GetOpponentCandidateListRequestModel:
    def __init__(self, json_data):
        self.player_id = json_data['player_id']
        self.team_id = json_data.get('team_id', None)
        self.console_id = json_data['console_id']
        self.game_id = json_data['game_id']
        self.duel_member_type = json_data['duel_member_type']


class GetOpponentCandidateListResponseModel:
    def __init__(self, candidate_list):
        self.candidate_list = candidate_list

    def __call__(self):
        return [x.to_json() for x in self.candidate_list]


class GetOpponentCandidateListInteractor:
    def __init__(self,
                 request: GetOpponentCandidateListRequestModel,
                 player_adapter: PlayerAdapter,
                 team_adapter: TeamAdapter):
        self.request = request
        self.player_adapter = player_adapter
        self.team_adapter = team_adapter
        self.logger = logging.getLogger(__name__)

    def _get_adapter(self):
        member_type = DuelMemberType(self.request.duel_member_type)
        return self.player_adapter \
            if member_type == DuelMemberType.PLAYER else self.team_adapter

    def get_candidate_list(self):
        member_type = DuelMemberType(self.request.duel_member_type)
        candidate_list = self.get_candidate_list_player() \
            if member_type == DuelMemberType.PLAYER \
            else self.get_candidate_list_team()
        return candidate_list

    def check_player_for_opponent(self, player_data: Player):
        if player_data.entity_id == self.request.player_id:
            return False

        console_found = next((x for x in player_data.consoles
                              if x.console_id == self.request.console_id),
                             None)
        if console_found:
            game_found = next((x for x in console_found.game_points
                               if x.game_id == self.request.game_id),
                              None)
            if game_found:
                return True

        return False

    def check_captain_not_on_members(self, team_data: Team):
        if team_data.captain.player_id == self.request.player_id:
            return False

        player_found = next((x for x in team_data.members
                             if x.player_id == self.request.player_id),
                            None)
        if player_found:
            return False
        return True

    def check_valid_team(self, team_data: Team):
        if team_data.members is None or len(team_data.members) == 0:
            return False

        if len(team_data.members) == 1 \
                and team_data.members[0].player_id == \
                team_data.captain.player_id:
            return False

        valid_members = [x for x in team_data.members
                         if x.member_type == MemberType.MEMBER
                         and x.status == MemberStatus.ACCEPTED
                         and x.player_id != team_data.captain.player_id]

        if valid_members and len(valid_members) > 0:
            return True
        return False

    def check_team_for_opponent(self, team_data: Team):
        if team_data.entity_id == self.request.team_id:
            return False
        if not self.check_captain_not_on_members(team_data):
            return False
        if not self.check_valid_team(team_data):
            return False
        if team_data.console_id == self.request.console_id \
                and team_data.game_id == self.request.game_id:
            return True
        return False

    def get_candidate_list_player(self):
        all_players = self.player_adapter.list_all()
        opponent_list = list()
        for candidate in all_players:
            if self.check_player_for_opponent(candidate):
                opponent_list.append(candidate)
        return opponent_list

    def get_candidate_list_team(self):
        all_teams = self.team_adapter.list_all()
        opponent_list = list()
        for candidate in all_teams:
            if self.check_team_for_opponent(candidate):
                opponent_list.append(candidate)
        return opponent_list

    def run(self):
        try:
            candidate_list = self.get_candidate_list()
            response = GetOpponentCandidateListResponseModel(candidate_list)
            return response
        except Exception as exc:
            msg = f'Error during restoring duel candidates: {str(exc)}'
            self.logger.error(msg)
            raise GetOpponentCandidateListException(msg)
