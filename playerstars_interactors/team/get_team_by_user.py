from playerstars_adapters import ConsoleAdapter, TeamAdapter
from playerstars_domain import MemberStatus, Team
import logging
from playerstars_domain.team.team import TeamStatus


class GetTeamByUserRequestModel:
    def __init__(self, json_data):
        self.logger = logging.getLogger(__name__)
        self.logger.info(json_data)
        self.player_id = json_data['player_id']
        self.get_actives = json_data.get('get_actives', True)
        self.get_inactives = json_data.get('get_inactives', True)
        self.get_invited = json_data.get('get_invited', True)
        self.get_accepted = json_data.get('get_accepted', True)
        self.logger.info(self.player_id)
        self.logger.info(self.get_inactives)
        self.logger.info(self.get_actives)
        self.logger.info(self.get_invited)
        self.logger.info(self.get_accepted)


class GetTeamByUserResponseModel:
    def __init__(self, team_list):
        self.team_list = team_list

    def __call__(self):
        return self.team_list


class GetTeamByUserInteractor:
    def __init__(self,
                 request: GetTeamByUserRequestModel,
                 team_adapter: TeamAdapter,
                 console_adapter: ConsoleAdapter):
        self.request = request
        self.team_adapter = team_adapter
        self.console_adapter = console_adapter
        self.logger = logging.getLogger(__name__)

    def format_team_list(self, captain_teams, member_teams):
        team_list = list()
        for team in captain_teams:
            team_list.append(self.format_item(team, 'CAPTAIN'))

        for team in member_teams:
            team_list.append(self.format_item(team, 'MEMBER'))

        return team_list

    def format_item(self, team, member_type):
        team_console = self.get_console_by_id(team.console_id)
        team_json = team.to_json()
        team_json['console'] = team_console.to_json()
        return {
            'membership_type': member_type,
            'team': team_json
        }

    def get_console_by_id(self, console_id):
        console_data = self.console_adapter.get_by_id(console_id)
        return console_data

    @staticmethod
    def team_active(team):
        return True if team.status == TeamStatus.ACTIVE else False

    def get_member_captain_teams(self, teams):
        member_teams = list()
        captain_teams = list()

        for team in teams:
            if self.request.player_id == team.captain.player_id \
                    and self.team_active(team):
                captain_teams.append(team)
            else:
                members_list = [membro.player_id for membro in team.members]
                if self.request.player_id in members_list \
                        and self.team_active(team):
                    member_teams.append(team)

        return member_teams, captain_teams

    def filter_member_teams(self, teams):
        filtered_teams = list()
        for team in teams:
            if self.request.get_accepted and\
                    self.filter_by_member_status(
                        team, MemberStatus.ACCEPTED):
                filtered_teams.append(team)
            if self.request.get_invited and\
                    self.filter_by_member_status(
                        team, MemberStatus.INVITED):
                filtered_teams.append(team)

        return filtered_teams

    def filter_by_member_status(self, team, status):
        for member in team.members:
            if self.request.player_id == member.player_id and \
                    member.status == status:
                return True
        return False

    def filter_captain_teams(self, teams):
        filtered_teams = list()
        for team in teams:
            if self.request.get_actives and self.check_active_team(team):
                filtered_teams.append(team)
            if self.request.get_inactives and not self.check_active_team(team):
                filtered_teams.append(team)

        return filtered_teams

    @staticmethod
    def check_active_team(team: Team):
        for member in team.members:
            if member.player_id != team.captain.player_id and \
                    member.status == MemberStatus.ACCEPTED:
                return True
        return False

    def run(self):
        self.logger.info('Começando Run')
        all_teams = self.team_adapter.list_all()
        member_teams, captain_teams = self.get_member_captain_teams(all_teams)
        self.logger.info('TEAMS: ', member_teams, ' ', captain_teams)
        filtered_member_teams = self.filter_member_teams(member_teams)
        filtered_captain_teams = self.filter_captain_teams(captain_teams)
        player_team_list = self.format_team_list(
            filtered_captain_teams, filtered_member_teams)
        response = GetTeamByUserResponseModel(player_team_list)
        return response()
