from playerstars_adapters import PlayerAdapter, TeamAdapter
from playerstars_domain import (
    Player,
    Team)
from playerstars_interactors.utils.domain_utils import (
    EntityNotFoundException,
    find_entity_by_id)

import logging


class GetMatchListException(BaseException):
    pass


class GetMatchListRequestModel:
    def __init__(self, json_data):
        self.player_id = json_data['player_id']
        self.member_type = json_data['member_type']
        self.team_id = json_data['team_id'] \
            if 'team_id' in json_data else None
        self.duel_console = json_data['console_id'] \
            if 'console_id' in json_data else None


class GetMatchListResponseModel:
    def __init__(self, match_list):
        self.match_list = match_list

    def __call__(self):
        response = [x.to_json() for x in self.match_list]
        return response


class GetMatchListInteractor:
    me_player = None
    me_team = None

    def __init__(self,
                 request: GetMatchListRequestModel,
                 player_adapter: PlayerAdapter,
                 team_adapter: TeamAdapter):
        self.request = request
        self.player_adapter = player_adapter
        self.team_adapter = team_adapter
        self.logger = logging.getLogger(__name__)

    def initial_tasks(self):
        self.get_me()
        self.initial_checks()

    def get_me(self):
        if self.request.member_type == 'PLAYER':
            self.get_me_player()
        else:
            self.get_me_player()
            self.get_me_team()

    def get_me_player(self):
        self.me_player = find_entity_by_id(
            _id=self.request.player_id,
            adapter_instance=self.player_adapter,
            class_name='Player')

    def get_me_team(self):
        self.me_team = find_entity_by_id(
            _id=self.request.team_id,
            adapter_instance=self.team_adapter,
            class_name='Team')

    def initial_checks(self):
        if self.request.member_type == 'TEAM':
            self.check_team()

    def check_team(self):
        team_to_check: Team = self.me_team
        if team_to_check.captain.player_id != self.request.player_id:
            raise Exception("Player {0} isn't the captain of team {1}"
                            .format(self.me_player.user.nickname,
                                    self.me_team.name))

        if team_to_check.console_id != self.request.duel_console:
            raise Exception("Team haven't the duel's console")

    def get_opponents_list(self):
        if self.request.member_type == 'PLAYER':
            return self.get_opponents_list_player()
        else:
            return self.get_opponents_list_team()

    def get_opponents_list_player(self):
        list_match = list()
        all_players = self.player_adapter.list_all()
        for player in all_players:
            if self.check_opponent_player(player):
                list_match.append(player)
        return list_match

    def get_opponents_list_team(self):
        list_match = list()
        all_teams = self.team_adapter.list_all()
        for team in all_teams:
            if self.check_opponent_team(team):
                list_match.append(team)
        return list_match

    def check_opponent_player(self, opponent_player: Player):
        opponent_is_me = opponent_player.entity_id == self.me_player.entity_id
        check_console = \
            not self.request.duel_console or \
            self.check_opponent_console(opponent_player)
        opponent_is_invalid = \
            opponent_player.is_blocked or not opponent_player.terms
        return check_console and \
            not opponent_is_me and \
            not opponent_is_invalid

    def check_opponent_team(self, opponent_team: Team):
        opponent_is_me = opponent_team.entity_id == self.me_team.entity_id
        i_am_captain = \
            opponent_team.captain.player_id == self.me_player.entity_id
        i_am_on_members = \
            next((x for x in opponent_team.members
                  if x.player_id == self.me_player.entity_id),
                 None)
        check_console = \
            not self.request.duel_console or \
            self.check_opponent_console(opponent_team)
        has_only_captain = \
            len(opponent_team.members) == 1 and \
            opponent_team.members[0].player_id == \
            opponent_team.captain.player_id

        return not i_am_captain and \
            not i_am_on_members and \
            check_console and \
            not opponent_is_me and \
            not has_only_captain

    def check_opponent_console(self, opponent_candidate):
        return self.check_opponent_console_player(opponent_candidate) \
            if self.request.member_type == 'PLAYER' \
            else self.check_opponent_console_team(opponent_candidate)

    def check_opponent_console_player(self, opponent_player: Player):
        console_found = next((x for x in opponent_player.consoles
                              if x.console_id == self.request.duel_console),
                             None)
        return console_found is not None

    def check_opponent_console_team(self, opponent_team: Team):
        return opponent_team.console_id == self.request.duel_console

    def run(self):
        try:
            self.initial_tasks()
            opponent_list = self.get_opponents_list()
            response = GetMatchListResponseModel(opponent_list)
            return response
        except (EntityNotFoundException, Exception) as exc:
            msg = 'Error during recovery match list: {0}'.format(str(exc))
            self.logger.error(msg)
            raise GetMatchListException(msg)
