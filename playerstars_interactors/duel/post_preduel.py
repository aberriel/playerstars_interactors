from playerstars_adapters import PreDuelAdapter, PlayerAdapter, TeamAdapter
from playerstars_domain import (
    CoinType, DuelMemberType, Player, PreDuel)
from playerstars_domain.duel.pre_duel import Status as PreDuelStatus
from playerstars_interactors.utils.message import send_message

import logging


class PlayerNotFoundException(Exception):
    pass


class PostPreDuelException(Exception):
    pass


class PostPreDuelRequestModel:
    def __init__(self, json_data):
        self.player_id = json_data.get('player_id')
        self.team_id = json_data.get('team_id', None)
        self.game_id = json_data.get('game_entity_id')
        self.console_id = json_data.get('console_entity_id')
        self.star_amount = json_data.get('star_amount', None)
        self.star_type = CoinType(json_data.get('star_type'))
        self.member_type = DuelMemberType(json_data.get('duel_type'))


class PostPreDuelResponseModel:
    def __init__(self, preduel_id, status):
        self.preduel_id = preduel_id
        self.status = status

    def __call__(self):
        return self.preduel_id, self.status


class PostPreDuelInteractor:
    def __init__(self,
                 request: PostPreDuelRequestModel,
                 preduel_adapter: PreDuelAdapter,
                 player_adapter: PlayerAdapter,
                 team_adapter: TeamAdapter):
        self.request = request
        self.preduel_adapter = preduel_adapter
        self.player_adapter = player_adapter
        self.team_adapter = team_adapter
        self.logger = logging.getLogger(__name__)

    def get_player_balance(self, player):
        if self.request.star_type == CoinType.GOLDEN_STAR:
            return player.golden_star_balance
        return player.red_star_balance

    def validate_player_requirements(self, player):
        msg = None
        if not player.game_exists(self.request.game_id):
            msg = f'Player {player.entity_id} não tem o jogo ' \
                f'{self.request.game_id} para criar esse duelo'

        balance = self.get_player_balance(player)

        star_amount = self.request.star_amount \
            if self.request.star_amount else 10
        if balance < star_amount:
            msg = f'Player {player.entity_id} não tem ' \
                f'{self.request.star_type.value} suficientes para criar' \
                f' o duelo.'
        if msg:
            raise PostPreDuelException(msg)

    def validate_request(self):
        if self.request.star_type == CoinType.GOLDEN_STAR \
                and not self.request.star_amount:
            msg = f'Preduels with golden stars need to inform star amount'
            raise PostPreDuelException(msg)
        if self.request.star_type == CoinType.RED_STAR \
                and self.request.star_amount:
            msg = f'Preduels with red stars should not inform star amount'
            raise PostPreDuelException(msg)
        if self.request.member_type == DuelMemberType.TEAM \
                and not self.request.team_id:
            msg = "Preduels for teams should have the team id in the request"
            raise PostPreDuelException(msg)

    def create_preduel(self):
        star_amount = self.request.star_amount \
            if self.request.star_amount else 5
        challenger = {
            DuelMemberType.PLAYER: self.request.player_id,
            DuelMemberType.TEAM: self.request.team_id
        }
        return PreDuel(
            status=PreDuelStatus.AWAITING,
            game_entity_id=self.request.game_id,
            console_entity_id=self.request.console_id,
            challenged=None,
            challenger=challenger[self.request.member_type],
            star_amount=star_amount,
            star_type=self.request.star_type,
            duel_type=self.request.member_type,
            ack=False)

    def check_conditions(self, preduel):
        if preduel.status == PreDuelStatus.AWAITING \
                and preduel.duel_type == self.request.member_type:
            if preduel.star_type == CoinType.RED_STAR \
                    and preduel.star_type == self.request.star_type:
                return True
            if preduel.star_type == CoinType.GOLDEN_STAR \
                    and preduel.star_type == self.request.star_type \
                    and preduel.star_amount == self.request.star_amount:
                return True
        return False

    def check_player(self, preduel):
        if self.request.player_id == preduel.challenger:
            preduel.status = PreDuelStatus.REFUSED
            preduel.set_adapter(self.preduel_adapter)
            preduel.save()
            return False
        return True

    def get_first_preduel(self, preduels):
        for preduel in preduels:
            if self.check_conditions(preduel) and self.check_player(preduel):
                return preduel
        return None

    def fill_first_preduel(self, preduel):
        challenged = {
            DuelMemberType.PLAYER: self.request.player_id,
            DuelMemberType.TEAM: self.request.team_id
        }
        preduel.challenged = challenged[self.request.member_type]
        preduel.status = PreDuelStatus.CONFIRM
        return preduel

    def warn_challenger(self, preduel):
        # Criar aviso que o challenger deve atualizar
        # os dados do duelo
        queue_name = preduel.challenger \
            if preduel.duel_type == DuelMemberType.PLAYER \
            else self.get_other_captain_id(preduel.challenger)
        message_response = send_message(
            f'{preduel.challenged} deu match no preduel {preduel.entity_id}',
            queue_name)
        self.logger.info(message_response)

    def get_other_captain_id(self, team_id):
        team = self.team_adapter.get_by_id(team_id)
        return team.captain.player_id

    def run(self):
        try:
            self.validate_request()
            player: Player = self.player_adapter.get_by_id(
                self.request.player_id)

            self.validate_player_requirements(player)

            preduels = self.preduel_adapter.filter(
                game_entity_id__eq=self.request.game_id)
            preduel = self.get_first_preduel(preduels)
            if not preduel:
                preduel = self.create_preduel()
                preduel.set_adapter(self.preduel_adapter)
                preduel.save()
                status = 'created'
            else:
                preduel = self.fill_first_preduel(preduel)
                preduel.set_adapter(self.preduel_adapter)
                preduel.save()
                status = 'joined'
                self.warn_challenger(preduel)

            response = PostPreDuelResponseModel(preduel.entity_id, status)
            return response
        except BaseException as exc:
            msg = 'Error during preduel creation: {}'.format(exc)
            self.logger.error(msg)
            raise PostPreDuelException(msg)
