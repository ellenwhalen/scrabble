
from incrementalist import Incrementalist
from board import Board
from gatekeeper import GateKeeper
from smartscrabble import SmartScrabble
from smartscrabble_v1 import SmartScrabblev1


class ScrabbleTournament:
    """A tournament between AIs."""
    def __init__(self, players):
        self._players = players

    def run(self):
        """
        Plays two games between each pair of contestants, one with each going first. Prints the number of wins for each
        contestant (including 0.5 wins for each tie).
        """
        scores = [0] * len(players)
        for i in range(len(players)):
            for j in range(len(players)):
                if i != j:
                    i_won, j_won = self.play_game(players[i], players[j])
                    scores[i] += i_won
                    scores[j] += j_won
        return(scores)
        # for i, player in enumerate(players):
        #     print(f'{str(player)}: {scores[i]}')

    @staticmethod
    def play_game(a, b):
        """
        Plays a game between AIs a (going first) and b. Returns their tournament scores: (1, 0) if a wins, (0, 1) if
        b wins, or (0.5, 0.5) in case of a tie.
        """
        print(f'{a} vs {b}:')
        board = Board()
        a.set_gatekeeper(GateKeeper(board, 0))
        b.set_gatekeeper(GateKeeper(board, 1))
        while not board.game_is_over():
            ScrabbleTournament.play_move(board, a, 0)
            if not board.game_is_over():
                ScrabbleTournament.play_move(board, b, 1)
        scores = board.get_scores()
        print(board)
        print(f'Final score: {a} {scores[0]}, {b} {scores[1]}\n')
        if scores[0] > scores[1]:
            return 1, 0
        elif scores[0] < scores[1]:
            return 0, 1
        return 0.5, 0.5

    @staticmethod
    def play_move(board, player, player_number):
        """
        Asks player for a move and plays it on board.
        """
        move = player.choose_move()
        move.play(board, player_number)


if __name__ == '__main__':
    players = [SmartScrabble(),
               SmartScrabblev1()]
    tot_scores = [0, 0]
    for i in range(100): 
        scores = ScrabbleTournament(players).run()
        tot_scores[0] += scores[0]
        tot_scores[1] += scores[1]
    if tot_scores[0] == 0:
        print(tot_scores)
        win_rate = 0
    elif tot_scores[1] == 0:
        print(tot_scores)
        win_rate = 1
    else:
        print(tot_scores)
        win_rate = tot_scores[0]/(tot_scores[0] + tot_scores[1])
    print("win rate: " + str(win_rate))