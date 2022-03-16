from PIV_Dota.piv_dota import PivDota, DotaPlayerInfo
from PIV_FifaUltimate.piv_fifa_ultimate import (
    FifaUltimatePlayerInfo,
    PivFifaUltimate)
from PIV_LOL.piv_lol import LolPlayerInfo, PivLol
from PIV_Valorant.piv_valorant import PivValorant, ValorantPlayerInfo
from playerstars_domain import DuelComponentResult, ImageValidity
import logging


def check_image(player_result: DuelComponentResult, tag_name,
                validator_class_name,
                logger=logging.getLogger(__name__)):
    map_piv = {
        'PivDota': (PivDota, DotaPlayerInfo),
        'PivFifaUltimate': (PivFifaUltimate, FifaUltimatePlayerInfo),
        'PivLol': (PivLol, LolPlayerInfo),
        'PivValorant': (PivValorant, ValorantPlayerInfo)
    }
    if validator_class_name not in map_piv.keys():
        return ImageValidity.NOT_SENT
    player_info = map_piv[validator_class_name][1](
        image_path=player_result.result_image,
        name=tag_name,
        report=player_result.result.value
    )
    image_without_http = player_result.result_image.split('//')[1]
    logger.info('tag name')
    logger.info(tag_name)
    logger.info('player result')
    logger.info(player_result.to_json())
    logger.info('image without http')
    logger.info(image_without_http)
    bucket_region, _, key = image_without_http.partition('/')
    bucket = bucket_region.split('.s3')[0]
    logger.info('bucket - key')
    logger.info(bucket + " - " + key)
    piv = map_piv[validator_class_name][0](
        player_info=player_info,
        bucket=bucket,
        key=key)
    result = piv()
    logger.info('piv dota result')
    logger.info(result)
    return result
