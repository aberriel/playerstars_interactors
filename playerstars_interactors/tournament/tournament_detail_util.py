from playerstars_domain.utils.datetime_helper import aware_now


def format_tournament(tournament, duel_type, player_adapter, review_time):
    creator = player_adapter.get_by_id(tournament.creator_id)
    return {
        "tournament_id": tournament.entity_id,
        "game_image": tournament.game.logo_path,
        "game_name": tournament.game.name,
        "console_name": tournament.console.name,
        "duel_type": duel_type.value,
        "star_amount": tournament.star_amount,
        "start_datetime": tournament.start_datetime.isoformat(),
        "phase_duration": tournament.level_duration,
        "phases_per_day": tournament.levels_per_day,
        "member_amount": tournament.member_amount,
        "finish_datetime": tournament.finish_datetime.isoformat(),
        "tournament_review_time": review_time,
        "tournament_phases": tournament.phases,
        "tournament_status": tournament.status.value,
        "confirmed_members": tournament.confirmed_members,
        "current_server_time": aware_now().isoformat(),
        "time_ref": aware_now().isoformat(),
        "creator": {
            "name": creator.user.nickname,
            "photo": creator.user.profile_image,
            "entity_id": creator.entity_id
        },
        "prize": {
            "first_place": tournament.first_place_prize,
            "second_place": tournament.second_place_prize,
            "third_place": tournament.third_place_prize
        },
        "members": get_members_data(tournament.members, player_adapter),
        "winners": get_winners(tournament)
    }


def get_members_data(members, player_adapter):
    member_list = list()
    for member in members:
        player_data = player_adapter.get_by_id(member.member_id)
        member_list.append({
            "player_id": member.member_id,
            "player_name": player_data.user.nickname,
            "player_photo": player_data.user.profile_image,
            "invite_status": member.status.value
        })
    return member_list


def get_winners(tournament):
    # [{
    # "player_id": str,
    # "player_name": str,
    # "player_photo": str,
    # "place": str
    # }]
    return []
