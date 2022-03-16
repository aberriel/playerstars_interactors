from playerstars_interactors.utils.image_utils import check_image
from playerstars_domain import ComponentResult, ImageValidity
from PIV_Dota.piv_dota import DotaPlayerInfo
from unittest.mock import patch, MagicMock
from playerstars_domain import DuelComponentResult
from datetime import datetime


player_result = DuelComponentResult(
    result=ComponentResult.WINNER,
    submission_datetime=datetime.now(),
    result_image='http://teste/image.png'
)
player_info = DotaPlayerInfo(
    image_path=player_result.result_image,
    name='schrubles',
    report=player_result.result.value
)


@patch('playerstars_interactors.utils.image_utils.PivDota',
       return_value=MagicMock(return_value=ImageValidity.VALID))
@patch('playerstars_interactors.utils.image_utils.DotaPlayerInfo',
       return_value=player_info)
def test_check_image(_info, piv):
    response = check_image(player_result, 'schrubles', 'PivDota')
    bucket, _, key = 'http://teste/image.png'.split('//')[1].partition('/')
    piv.assert_called_with(
        player_info=player_info,
        bucket=bucket,
        key=key)

    assert response == ImageValidity.VALID


def test_check_image_validator_doesnt_exist():
    response = check_image(player_result, 'schrubles', 'schrublinho')
    assert response == ImageValidity.NOT_SENT
