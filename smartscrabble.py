__author__ = "Idalyne Giron Castillo, Jermisha Hinton, Ellen Whalen,  Grace Wiseman"

from location import *
from board import *
from move import *

ALL_TILES = [True] * 7

class SmartScrabble:
    """
    AI that prioritizes placing the longest possible word from the hand on the board.
    Exchanges all tiles if no valid moves are found.
    """

    def __init__(self):
        self._gatekeeper = None
        self.word_list = self._load_word_list('words.txt')

    def _load_word_list(self, file_path):
        with open(file_path, 'r') as file:
            words = {word.strip() for word in file.readlines() if len(word.strip()) <= 7}
        return words

    def set_gatekeeper(self, gatekeeper):
        self._gatekeeper = gatekeeper

    def choose_move(self):
        """
        Try to place the highest-scoring possible word from the word list in the highest-scoring spot.
        If no valid move is found, attempt a single-tile move.
        If still no move, exchange all tiles.
        """
        words = []
        i = 0
        word_list = sorted(self.word_list, key=len, reverse=True)
        scores = []

        # picks out every playable word from the hand and puts them in a list
        while i < len(word_list) - 1:
            word = word_list[i]
            if self._can_form_word(word):
                size = len(word)
                words.append(word)
            i += 1
        
        if words != []:
            # calculates the scores of every word in the word list
            for word in words:
                score = 0
                for letter in word:
                    score += TILE_VALUES[letter]
                scores.append((score, word))
            # sorts the word list by score
            scores.sort()

            # tries to play every word of the given length until it successfully plays one
            # or runs out of words
            while scores != []:
                highest_word = scores[-1][1]
                move = self._place_word(highest_word)
                if not move:
                    scores.pop(-1)
                    continue
                elif not move and i != len(word_list) - 1:
                    break
                else:
                    return move

        # Default to a one-tile move if no valid word placement is found
        one_tile_move = self._find_one_tile_move()
        if one_tile_move:
            return one_tile_move
        
        # if still no move, exchange tiles
        return ExchangeTiles(ALL_TILES)

    def _can_form_word(self, word):
        """
        Check if the word can be formed using the current hand
        each tile is used only once
        """
        hand = self._gatekeeper.get_hand()
        hand_copy = list(hand)  # Make a mutable copy of the hand

        for char in word:
            if char in hand_copy:
                hand_copy.remove(char)  # Use this tile
            elif '_' in hand_copy:  # Use a blank tile
                hand_copy.remove('_')
            else:  
                return False
        return True

    def _place_word(self, word):
        """
        Try to place the given word on the board, checking all possible tiles for valid placements.
        Picks the highest-possible scoring placement.
        """
        placements = []
        for row in range(WIDTH):
            for col in range(WIDTH):
                location = Location(row, col)
                for direction in (HORIZONTAL, VERTICAL):
                    try:
                        # Check if the word can be placed starting at this location
                        self._gatekeeper.verify_legality(word, location, direction)

                        # if it's legal, find the score
                        score = self._gatekeeper.score(word, location, direction)

                        # can't append the direction as it is to the list because you can't compare Location objects lol
                        if direction == HORIZONTAL:
                            dir = 0
                        else:
                            dir = 1
                        
                        # append all the info to a list of possible placements
                        placements.append((score, row, col, dir))
                    except:
                        pass  # Move is not legal; skip to the next position
        if placements != []:
            placements.sort()
            location = Location(placements[-1][1], placements[-1][2])
            if placements[-1][3] == 0:
                direction = HORIZONTAL
            else:
                direction = VERTICAL
            return PlayWord(word, location, direction)
        return None

    def _find_one_tile_move(self):
        """
        Try to play the highest-scoring one-tile move.
        """
        hand = self._gatekeeper.get_hand()
        best_score = -1
        best_move = None
        for tile in hand:
            if tile == '_':
                tile = 'E'  # This could be improved slightly by trying all possibilities for the blank
            for word in tile + ' ', ' ' + tile:
                for row in range(WIDTH):
                    for col in range(WIDTH):
                        location = Location(row, col)
                        for direction in (HORIZONTAL, VERTICAL):
                            try:
                                self._gatekeeper.verify_legality(word, location, direction)
                                score = self._gatekeeper.score(word, location, direction)
                                if score > best_score:
                                    best_score = score
                                    best_move = PlayWord(word, location, direction)
                            except:
                                pass  # This move wasn't legal; skip to the next one
        if best_move:
            return best_move
        return ExchangeTiles(ALL_TILES)