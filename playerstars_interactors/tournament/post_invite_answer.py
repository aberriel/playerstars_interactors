from playerstars_domain import DuelMemberType as MemberType
from playerstars_domain import TournamentMemberStatus


class PostInviteAnswerError(BaseException):
    pass


class PostInviteAnswerRequestModel:
    def __init__(self, player_id, member_type,
                 data, answer, team_id=None):
        self.player_id = player_id
        self.member_type: MemberType = member_type
        self.tournament_id = data.get('tournament_id')
        self.answer = answer
        self.team_id = team_id


class PostInviteAnswerResponseModel:
    def __init__(self, tournament):
        self.tournament = tournament

    def __call__(self, *args, **kwargs):
        return self.tournament.to_json() if self.tournament else None


class PostInviteAnswerAdapters:
    def __init__(self,
                 player_adapter,
                 team_adapter,
                 player_tournament_adapter,
                 team_tournament_adapter):
        self.player_adapter = player_adapter
        self.team_adapter = team_adapter
        self.player_tournament_adapter = player_tournament_adapter
        self.team_tournament_adapter = team_tournament_adapter


class PostInviteAnswerInteractor:
    def __init__(self, request: PostInviteAnswerRequestModel,
                 adapters: PostInviteAnswerAdapters):
        self.request = request
        self.adapters = adapters

    def get_player(self, _id):
        return self.adapters.player_adapter.get_by_id(_id)

    def get_team(self, _id):
        return self.adapters.team_adapter.get_by_id(_id)

    def subtract_player_stars(self, player, price):
        player.golden_star_balance = player.golden_star_balance - price
        player.set_adapter(self.adapters.player_adapter)
        player.save()

    def check_player_stars(self, price):

        player = self.get_player(self.request.player_id)

        if player.golden_star_balance < price:
            msg = "Player cannot accept invite with less stars than the price"
            raise PostInviteAnswerError(msg)
        self.subtract_player_stars(player, price)

    def check_team_stars(self, price):

        team = self.get_team(self.request.team_id)
        captain = self.get_player(team.captain.player_id)

        if captain.golden_star_balance < price:
            msg = "Team cannot accept invite when the captain has less stars" \
                  " than the price is"
            raise PostInviteAnswerError(msg)
        self.subtract_player_stars(captain, price)

    def check_stars(self, price):
        check_func_map = {
            MemberType.PLAYER: self.check_player_stars,
            MemberType.TEAM: self.check_team_stars
        }
        check_func_map[self.request.member_type](price)

    def check_answer(self):
        return True if self.request.answer == 'ACCEPT' else False

    def accept_invite(self, tournament):
        for x in tournament.members:
            if x.member_id == self.request.player_id:
                x.status = TournamentMemberStatus.ACCEPTED

    def refuse_invite(self, tournament):
        for x in tournament.members:
            if x.member_id == self.request.player_id:
                x.status = TournamentMemberStatus.REJECTED

    def run(self):
        adapter_map = {
            MemberType.PLAYER: self.adapters.player_tournament_adapter,
            MemberType.TEAM: self.adapters.team_tournament_adapter
        }

        tournament_adapter = adapter_map[self.request.member_type]
        tournament = tournament_adapter.get_by_id(self.request.tournament_id)

        if self.check_answer():
            self.check_stars(tournament.price_to_enter)
            self.accept_invite(tournament)
        else:
            self.refuse_invite(tournament)

        tournament.set_adapter(tournament_adapter)
        tournament.save()
        response = PostInviteAnswerResponseModel(tournament)
        return response
