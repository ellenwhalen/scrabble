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
        Try to place the longest possible word from the word list.
        If no valid move is found, attempt a single-tile move.
        If still no move, exchange all tiles.
        """
        words = []
        i = 0
        word_list = sorted(self.word_list, key=len, reverse=True)
        scores = []
        marker = True

        # outer loop just runs everything over and over again until it has checked that 
        # no word of size greater than 2 can be made from the given letters. this means
        # it can check for the highest-scoring word in each length of word until it gets
        # one that is actually playable.
        while marker == True:
            # needs to reset size to 0 before it re-enters the first loop
            size = 0

            # picks out every playable word of the next-longest length and puts them in a list
            while i < len(word_list) - 1:
                word = word_list[i]
                if len(word) < size:
                    break
                if self._can_form_word(word):
                    size = len(word)
                    words.append(word)
                i += 1
            
            # don't know if i need this if anymore tbh. there was a bug and this half-fixed it
            # but then i really fixed the bug
            if words != []:
                # calculates the scores of every word in the word list the first loop gave us
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
                    elif move is None and i != len(word_list) - 1:
                        break
                    else:
                        return move
            # when it's run through every word in the word list it quits out
            if i == len(word_list) - 1:
                marker=False

        # Default to a one-tile move if no valid word placement is found
        one_tile_move = self._find_one_tile_move()
        if one_tile_move:
            return one_tile_move

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
        """
        for row in range(WIDTH):
            for col in range(WIDTH):
                location = Location(row, col)
                for direction in (HORIZONTAL, VERTICAL):
                    try:
                        # Check if the word can be placed starting at this location
                        self._gatekeeper.verify_legality(word, location, direction)
                        return PlayWord(word, location, direction)
                    except:
                        pass  # Move is not legal; skip to the next position
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
