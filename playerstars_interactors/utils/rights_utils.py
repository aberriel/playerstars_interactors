from playerstars_adapters import PlayerAdapter
from playerstars_domain import Player
from playerstars_interactors.utils.domain_utils import find_entity_by_id


class AccessDeniedAdminException(BaseException):
    pass


def check_player_is_admin(player_id: str,
                          player_adapter: PlayerAdapter):
    player: Player = find_entity_by_id(
        _id=player_id,
        adapter_instance=player_adapter,
        class_name='Player')
    if not player.is_admin:
        raise AccessDeniedAdminException(
            "Player {0} isn't admin".format(player.user.nickname))
