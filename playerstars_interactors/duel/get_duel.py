from playerstars_adapters import (
    DuelAdapter,
    PlayerAdapter,
    TeamAdapter)
from playerstars_domain import Duel, Player, Team, DuelMemberType
from playerstars_domain.utils.datetime_helper import aware_now


class GetDuelRequestModel:
    def __init__(self, json_data: dict):
        self.player_id = json_data['player_id']
        self.duel_id = json_data['duel_id']


class GetDuelResponseModel:
    def __init__(self, duel_data):
        self.duel_data = duel_data

    @property
    def current_server_time(self):
        current_time = aware_now()
        current_time_str = current_time.isoformat()
        return current_time_str

    def __call__(self):
        if not self.duel_data:
            return None
        self.duel_data['current_server_time'] = self.current_server_time
        return self.duel_data


class GetDuelInteractor:
    duel = None

    def __init__(self,
                 request: GetDuelRequestModel,
                 duel_adapter: DuelAdapter,
                 player_adapter: PlayerAdapter,
                 team_adapter: TeamAdapter):
        self.request = request
        self.duel_adapter = duel_adapter
        self.player_adapter = player_adapter
        self.team_adapter = team_adapter

    def get_member(self, adapter_instance, member_id):
        return adapter_instance.get_by_id(member_id)

    def get_challenger(self, adapter_instance):
        return self.get_member(adapter_instance, self.duel.challenger)

    def get_challenged(self, adapter_instance):
        return self.get_member(adapter_instance, self.duel.challenged)

    def add_player_data(self):
        duel_data = self.duel.to_json()
        challenger: Player = self.get_challenger(self.player_adapter)
        duel_data['challenger'] = {
            "entity_id": self.duel.challenger,
            "name": challenger.user.nickname,
            "image": challenger.user.profile_image,
            "tag_name": challenger.get_tag_name(self.duel.console.entity_id)}
        challenged = self.get_challenged(self.player_adapter)
        duel_data['challenged'] = {
            "entity_id": self.duel.challenged,
            "name": challenged.user.nickname,
            "image": challenged.user.profile_image,
            "tag_name": challenged.get_tag_name(self.duel.console.entity_id)}
        return duel_data

    def add_team_data(self):
        duel_data = self.duel.to_json()
        challenger: Team = self.get_challenger(self.team_adapter)
        duel_data['challenger'] = {
            "entity_id": self.duel.challenger,
            "name": challenger.name,
            "image": challenger.logo_path,
            "tag_name": self.player_adapter.get_by_id(
                challenger.captain.player_id).get_tag_name(
                    self.duel.console.entity_id)}
        challenged: Team = self.get_challenged(self.team_adapter)
        duel_data['challenged'] = {
            "entity_id": self.duel.challenged,
            "name": challenged.name,
            "image": challenged.logo_path,
            "tag_name": self.player_adapter.get_by_id(
                challenged.captain.player_id).get_tag_name(
                    self.duel.console.entity_id)}

        if challenger.captain.player_id == self.request.player_id:
            duel_data['player_team'] = challenger.entity_id
        else:
            duel_data['player_team'] = challenged.entity_id

        return duel_data

    def run(self):
        self.duel: Duel = self.duel_adapter.get_by_id(self.request.duel_id)
        if not self.duel:
            response = GetDuelResponseModel(self.duel)
            return response
        adapted_duel = None
        if self.duel.member_type == DuelMemberType.PLAYER:
            adapted_duel = self.add_player_data()
        if self.duel.member_type == DuelMemberType.TEAM:
            adapted_duel = self.add_team_data()
        response = GetDuelResponseModel(adapted_duel)
        return response
