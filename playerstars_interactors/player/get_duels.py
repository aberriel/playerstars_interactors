from datetime import datetime
from playerstars_domain import Duel, DuelStatus, DuelMemberType, Team
from typing import List


class GetAllPlayerDuelByStatusError(BaseException):
    pass


class GetAllPlayerDuelByStatusRequestModel:
    def __init__(self, played_id, status=None):
        self.player_id = played_id
        self.status = status


class GetAllPlayerDuelByStatusResponseModel:
    def __init__(self, duels):
        self.duels = duels

    def __call__(self):
        return self.duels if self.duels else list()


class GetAllPlayerDuelByStatusInteractor:
    def __init__(self, request: GetAllPlayerDuelByStatusRequestModel,
                 adapter_instance, team_adapter, player_adapter):
        self.request = request
        self.adapter_instance = adapter_instance
        self.team_adapter = team_adapter
        self.player_adapter = player_adapter

    def check_player_in_solo_duel(self, duel):
        if duel.challenged and duel.challenged == self.request.player_id \
                or duel.challenger == self.request.player_id:
            return True

    def check_player_in_team_duel(self, duel):
        team_1: Team = self.team_adapter.get_by_id(duel.challenger)
        team_2: Team = self.team_adapter.get_by_id(duel.challenged)
        player_found = False
        if team_1.check_if_member(self.request.player_id) or \
                team_2.check_if_member(self.request.player_id):
            player_found = True
        return player_found

    def get_participant_duels(self, duels):
        participant_duels = list()
        for duel in duels:
            if duel.member_type == DuelMemberType.TEAM and\
                    self.check_player_in_team_duel(duel):
                participant_duels.append(duel)
            if duel.member_type == DuelMemberType.PLAYER and\
                    self.check_player_in_solo_duel(duel):
                participant_duels.append(duel)
        return participant_duels

    def get_status(self):
        if '-' in self.request.status:
            status = self.request.status.split('-')
            return [DuelStatus(item) for item in status]
        return [DuelStatus(self.request.status)]

    def _filter_duels(self, all_duels):
        default = [
            DuelStatus.FINISHED_BY_VICTORY,
            DuelStatus.FINISHED_BY_RESIGN,
            DuelStatus.FINISHED_BY_TIE,
            DuelStatus.UNDER_REVIEW,
            DuelStatus.CANCELED_BY_INCONSISTENT_RESULT
        ]
        status_to_filter = default if not self.request.status \
            else self.get_status()
        filtered_duels = \
            [duel for duel in all_duels if duel.status in status_to_filter]
        return filtered_duels

    def get_winner_data(self, duel: Duel):
        if duel.winner and duel.status in [DuelStatus.FINISHED_BY_VICTORY,
                                           DuelStatus.FINISHED_BY_RESIGN]:
            winner_data = {
                'i_am_winner': duel.winner == self.request.player_id,
                'winner_id': duel.winner
            }
            return winner_data
        return None

    def format_duel_list(self, duels):
        duel_list = list()
        duel_type_conv = {
            DuelMemberType.PLAYER: 'Individual',
            DuelMemberType.TEAM: 'Entre Times'
        }
        opponent_type_conv = {
            DuelMemberType.PLAYER: 'player',
            DuelMemberType.TEAM: 'team'
        }
        for duel in duels:
            team_name, opponent_team_name = self.get_team_names(duel)
            duel_details = {
                'duel_id': duel.entity_id,
                'gameImage': duel.game.logo_path,
                'gameName': duel.game.name,
                'consoleName': duel.console.name,
                'members': 2,
                'start_date_time':
                    duel.time_start.strftime('%d/%m/%Y %H:%M:%S'),
                'star_type': duel.star_type.value,
                'bet': duel.bet_size,
                'reward': duel.total_reward,
                'winner': self.get_winner_data(duel),
                'matchTitle': duel_type_conv[duel.member_type],
                'matchType': 'duel',
                'ranking': [],
                'opponent_type': opponent_type_conv[duel.member_type],
                'status': duel.status.value,
                'opponent_name': self.get_opponent_nickname(duel),
                'team_name': team_name,
                'opponent_team_name': opponent_team_name,

            }
            duel_list.append(duel_details)

        return duel_list

    def get_opponent_nickname(self, duel):
        if duel.member_type == DuelMemberType.TEAM:
            return None
        if self.request.player_id == duel.challenger:
            player = self.player_adapter.get_by_id(duel.challenged)
            return player.user.nickname
        player = self.player_adapter.get_by_id(duel.challenger)
        return player.user.nickname

    def get_team_names(self, duel):
        if duel.member_type == DuelMemberType.PLAYER:
            return None, None
        team_1: Team = self.team_adapter.get_by_id(duel.challenger)
        team_2: Team = self.team_adapter.get_by_id(duel.challenged)
        team_name = team_2.name
        opponent_team_name = team_1.name
        if team_1.check_if_member(self.request.player_id):
            team_name = team_1.name
            opponent_team_name = team_2.name
        return team_name, opponent_team_name

    @staticmethod
    def sort_duel_list(duels):
        return sorted(
            duels,
            key=lambda x: datetime.strptime(x['start_date_time'],
                                            '%d/%m/%Y %H:%M:%S'),
            reverse=True)

    def run(self):
        all_duels: List[Duel] = self.adapter_instance.list_all()
        filtered_duels = self._filter_duels(all_duels)
        if self.request.status == 'DUELING' and len(filtered_duels) > 1:
            raise GetAllPlayerDuelByStatusError(
                f'Player {self.request.player_id} tem mais de um duelo '
                f'acontecendo ao mesmo tempo')
        player_duels = self.get_participant_duels(filtered_duels)
        formated_duels = self.format_duel_list(player_duels)
        sorted_duels = self.sort_duel_list(formated_duels)
        response = GetAllPlayerDuelByStatusResponseModel(sorted_duels)
        return response()
