"""
MiniMax Player
"""
from players.AbstractPlayer import AbstractPlayer
#TODO: you can import more modules, if needed
import numpy as np
import utils
import time
import SearchAlgos
import copy
############################# make deep copy for player class - search arg and yield of succ function ##################################################

class Player(AbstractPlayer):
    def __init__(self, game_time):
        AbstractPlayer.__init__(self, game_time)  # keep the inheritance of the parent's (AbstractPlayer) __init__()
        self.turn_count = 0   # increase when make moves
        self.player_pos = np.full(9, -1)
        self.rival_pos = np.full(9, -1)
        #TODO: initialize more fields, if needed, and the AlphaBeta algorithm from SearchAlgos.py

    def set_game_params(self, board):
        """Set the game parameters needed for this player.
        This function is called before the game starts.
        (See GameWrapper.py for more info where it is called)
        input:
            - board: np.array, of the board.
        No output is expected.
        """
        # TODO: erase the following line and implement this function.
        self.board = board

    def make_move(self, time_limit):
        """Make move with this Player.
        input:
            - time_limit: float, time limit for a single turn.
        output:
            - direction: tuple, specifing the Player's movement
            :return: move = (pos, soldier, dead_opponent_pos)
        """
        start = time.time()
        end = start + time_limit
        max_value = -np.inf
        # direction (the new cell, soldier - 10 sized array, rival dead soldier - 10 sized array)
        best_move = (-1, -1, -1)
        depth = 1
        # state = (self.board, self.turn_count, self.player_pos, self.rival_pos, 1, best_move)
        minimax = SearchAlgos.MiniMax(self.calculate_state_heuristic, self.succ, None, self.check_end_game)
        """"########################## check if 1 is enough #########################"""
        while end > time.time() + 1 and depth <= 2:
            value, direction = minimax.search((copy.deepcopy(self), 1, best_move), depth, True)
            if value > max_value:
                best_move = direction
                max_value = value
            depth += 1
        # update self values
        cell, my_soldier, rival_soldier = best_move
        self.turn_count += 1
        self.board[self.player_pos[my_soldier]] = 0
        self.board[cell] = 1
        self.player_pos[my_soldier] = cell
        if rival_soldier != -1:
            self.board[self.rival_pos[rival_soldier]] = 0
            self.rival_pos[rival_soldier] = -2
        return best_move

    def set_rival_move(self, move):
        """Update your info, given the new position of the rival.
        input:
            - move: tuple, the new position of the rival.
        No output is expected
        """
        # direction (the new cell, soldier - 10 sized array, rival dead soldier - 10 sized array)
        rival_pos, rival_soldier, my_dead_pos = move

        if self.turn_count < 9:
            self.board[rival_pos] = 2
            self.rival_pos[rival_soldier] = rival_pos
        else:
            rival_prev_pos = self.rival_pos[rival_soldier]
            self.board[rival_prev_pos] = 0
            self.board[rival_pos] = 2
            self.rival_pos[rival_soldier] = rival_pos
        if my_dead_pos != -1:
            self.board[my_dead_pos] = 0
            dead_soldier = int(np.where(self.player_pos == my_dead_pos)[0][0])
            self.player_pos[dead_soldier] = -2

    ########## helper functions in class ##########
    # TODO: add here helper functions in class, if needed

    def check_end_game(self, player, player_idx : int) -> bool:
        if player_idx == 1:
            dead = np.where(player.player_pos != -2)[0]
        else:
            dead = np.where(player.rival_pos != -2)[0]
        if len(dead) >= 3:
            return False
        for index, x in enumerate(self.rival_pos):
            if x != -1 and not self.check_if_blocked(x, 2):
                return False
        for index, x in enumerate(self.player_pos):
            if x != -1 and not self.check_if_blocked(x, 1):
                return False
        return True


    ########## helper functions for AlphaBeta algorithm ##########
    # TODO: add here the utility, succ, an

    # heuristic of phase 1


    def calculate_state_heuristic(self, state):
        mill_num = 0
        rival_mill_num = 0
        incomplete_mills = 0
        rival_incomplete_mills = 0
        blocked_soldiers = 0
        rival_blocked_soldiers = 0
        incomplete_mills_that_player_cant_block = 0
        incomplete_mills_that_rival_cant_block = 0
        diagonal_placement = 0
        player = state[0]
        board = player.board
        for x in board:
            cell = int(x)
            if cell == 1:
                if player.is_mill(cell):
                    mill_num += 1
                if player.check_if_blocked(cell, 1, board):
                    blocked_soldiers += 1
                if player.check_next_mill(cell, 1):
                    incomplete_mills += 1
                if player.is_unblocked_mill(cell, 1, board):
                    incomplete_mills_that_rival_cant_block += 1
            elif cell == 2:
                if player.is_mill(cell):
                    rival_mill_num += 1
                if player.check_if_blocked(cell, 2, board):
                    rival_blocked_soldiers += 1
                if player.check_next_mill(cell, 2):
                    rival_incomplete_mills += 1
                if player.is_unblocked_mill(cell, 2, board):
                    incomplete_mills_that_player_cant_block += 1
            # elif cell == 0:
            # if player.is_diagonal(cell):
            #     diagonal_placement += 1
        if player.turn_count < 9:
            y = 0.2 * (mill_num - rival_mill_num) + \
                   0 * diagonal_placement + \
                   0.2 * int(incomplete_mills == 2) + \
                   0.2 * int(rival_incomplete_mills == 0) + \
                   0.2 * (rival_blocked_soldiers - blocked_soldiers) + \
                   0.2 * (incomplete_mills_that_rival_cant_block - incomplete_mills_that_player_cant_block)
            return y
        else:
            return 0.2 * incomplete_mills + \
                   0.2 * (incomplete_mills - rival_incomplete_mills) + \
                   0.9 * (mill_num - rival_mill_num) + \
                   0.2 * (rival_blocked_soldiers - blocked_soldiers) + \
                   0.2 * (incomplete_mills_that_rival_cant_block - incomplete_mills_that_player_cant_block)

    def check_if_blocked(self, position, player, board=None):
        """
        Function to check if a player can make a mill in the next move.
        :param position: curren position
        :param board: np.array
        :param player: 1/2
        :return:
        """
        rival = 3 - player
        if board is None:
            board = self.board

        for i in utils.get_directions(position):
            if board[i] == 0:
                return False
        return True

    def is_unblocked_mill(self, position, player, board=None):
        """
        Function to check if a player has an unblocked mill.
        :param position: curren position
        :param board: np.array
        :param player: 1/2
        :return:
        """
        if board is None:
            board = self.board
        blocked = [
            (board[0] == 0 and (self.is_player(player, 3, 5, board) and self.is_player(player, 1, 3, board) or \
             self.is_player(player, 1, 2, board) and self.is_player(player, 1, 3, board))),

            (board[1] == 0 and (self.is_player(player, 0, 2, board) and self.is_player(player, 0, 9, board) or \
             self.is_player(player, 9, 17, board) and self.is_player(player, 0, 2, board))),

            (board[2] == 0 and (self.is_player(player, 4, 7, board) and self.is_player(player, 1, 4, board) or \
            self.is_player(player, 0, 1, board) and self.is_player(player, 1, 4, board))),

            (board[3] == 0 and (self.is_player(player, 0, 11, board) and self.is_player(player, 0, 5, board) or \
            self.is_player(player, 11, 19, board) and self.is_player(player, 0, 5, board))),

            (board[4] == 0 and (self.is_player(player, 2, 7, board) and self.is_player(player, 2, 12, board) or \
            self.is_player(player, 2, 7, board) and self.is_player(player, 12, 20, board))),

            (board[5] == 0 and (self.is_player(player, 6, 7, board) and self.is_player(player, 3, 6, board) or \
            self.is_player(player, 0, 3, board) and self.is_player(player, 3, 6, board))),

            (board[6] == 0 and (self.is_player(player, 5, 7, board) and self.is_player(player, 5, 14, board) or \
            self.is_player(player, 14, 22, board) and self.is_player(player, 5, 14, board))),

            (board[7] == 0 and (self.is_player(player, 5, 6, board) and self.is_player(player, 6, 4, board) or \
            self.is_player(player, 2, 4, board) and self.is_player(player, 6, 4, board))),

            (board[8] == 0 and (self.is_player(player, 9, 10, board) and self.is_player(player, 10, 11, board) or \
            self.is_player(player, 11, 13, board) and self.is_player(player, 10, 11, board))),

            (board[9] == 0 and (self.is_player(player, 1, 17, board) and self.is_player(player, 8, 10, board))),

            (board[10] == 0 and (self.is_player(player, 8, 9, board) and self.is_player(player, 9, 12, board) or \
            self.is_player(player, 12, 15, board) and self.is_player(player, 9, 12, board))),

            (board[11] == 0 and (self.is_player(player, 3, 19, board) and self.is_player(player, 8, 13, board))),

            (board[12] == 0 and (self.is_player(player, 4, 20, board) and self.is_player(player, 10, 15, board))),

            (board[13] == 0 and (self.is_player(player, 8, 11, board) and self.is_player(player, 11, 14, board) or \
            self.is_player(player, 14, 15, board) and self.is_player(player, 11, 14, board))),

            (board[14] == 0 and (self.is_player(player, 6, 22, board) and self.is_player(player, 13, 15, board))),

            (board[15] == 0 and (self.is_player(player, 13, 14, board) and self.is_player(player, 12, 14, board) or \
            self.is_player(player, 10, 12, board) and self.is_player(player, 12, 14, board))),

            (board[16] == 0 and (self.is_player(player, 17, 18, board) and self.is_player(player, 18, 19, board) or \
            self.is_player(player, 19, 21, board) and self.is_player(player, 18, 19, board))),

            (board[17] == 0 and (self.is_player(player, 16, 18, board) and self.is_player(player, 16, 9, board) or \
            self.is_player(player, 1, 9, board) and self.is_player(player, 16, 18, board))),

            (board[18] == 0 and (self.is_player(player, 16, 17, board) and self.is_player(player, 17, 20, board) or \
            self.is_player(player, 20, 23, board) and self.is_player(player, 17, 20, board))),

            (board[19] == 0 and (self.is_player(player, 16, 21, board) and self.is_player(player, 16, 11, board) or \
            self.is_player(player, 3, 11, board) and self.is_player(player, 16, 21, board))),

            (board[20] == 0 and (self.is_player(player, 18, 23, board) and self.is_player(player, 12, 18, board) or \
            self.is_player(player, 4, 12, board) and self.is_player(player, 18, 23, board))),

            (board[21] == 0 and (self.is_player(player, 16, 19, board) and self.is_player(player, 19, 22, board) or \
            self.is_player(player, 22, 23, board) and self.is_player(player, 19, 22, board))),

            (board[22] == 0 and (self.is_player(player, 21, 23, board) and self.is_player(player, 14, 21, board) or \
            self.is_player(player, 6, 14, board) and self.is_player(player, 21, 23, board))),

            (board[23] == 0 and (self.is_player(player, 18, 20, board) and self.is_player(player, 20, 22, board) or \
            self.is_player(player, 21, 22, board) and self.is_player(player, 20, 22, board)))
        ]

        return blocked[position]

    def is_diagonal(self, cell, player, board=None):
        if board == None:
            board = self.board
        diagonal = [
            (board[0] == 0 and (self.is_player(player, 3, 5, board) and self.is_player(player, 1, 3, board) or \
             self.is_player(player, 1, 2, board) and self.is_player(player, 1, 3, board))),

            (board[1] == 0 and (self.is_player(player, 0, 2, board) and self.is_player(player, 0, 9, board) or \
             self.is_player(player, 9, 17, board) and self.is_player(player, 0, 2, board))),

            (board[2] == 0 and (self.is_player(player, 4, 7, board) and self.is_player(player, 1, 4, board) or \
            self.is_player(player, 0, 1, board) and self.is_player(player, 1, 4, board))),

            (board[3] == 0 and (self.is_player(player, 0, 11, board) and self.is_player(player, 0, 5, board) or \
            self.is_player(player, 11, 19, board) and self.is_player(player, 0, 5, board))),

            (board[4] == 0 and (self.is_player(player, 2, 7, board) and self.is_player(player, 2, 12, board) or \
            self.is_player(player, 2, 7, board) and self.is_player(player, 12, 20, board))),

            (board[5] == 0 and (self.is_player(player, 6, 7, board) and self.is_player(player, 3, 6, board) or \
            self.is_player(player, 0, 3, board) and self.is_player(player, 3, 6, board))),

            (board[6] == 0 and (self.is_player(player, 5, 7, board) and self.is_player(player, 5, 14, board) or \
            self.is_player(player, 14, 22, board) and self.is_player(player, 5, 14, board))),

            (board[7] == 0 and (self.is_player(player, 5, 6, board) and self.is_player(player, 6, 4, board) or \
            self.is_player(player, 2, 4, board) and self.is_player(player, 6, 4, board))),

            (board[8] == 0 and (self.is_player(player, 9, 10, board) and self.is_player(player, 10, 11, board) or \
            self.is_player(player, 11, 13, board) and self.is_player(player, 10, 11, board))),

            (board[9] == 0 and (self.is_player(player, 1, 17, board) and self.is_player(player, 8, 10, board))),

            (board[10] == 0 and (self.is_player(player, 8, 9, board) and self.is_player(player, 9, 12, board) or \
            self.is_player(player, 12, 15, board) and self.is_player(player, 9, 12, board))),

            (board[11] == 0 and (self.is_player(player, 3, 19, board) and self.is_player(player, 8, 13, board))),

            (board[12] == 0 and (self.is_player(player, 4, 20, board) and self.is_player(player, 10, 15, board))),

            (board[13] == 0 and (self.is_player(player, 8, 11, board) and self.is_player(player, 11, 14, board) or \
            self.is_player(player, 14, 15, board) and self.is_player(player, 11, 14, board))),

            (board[14] == 0 and (self.is_player(player, 6, 22, board) and self.is_player(player, 13, 15, board))),

            (board[15] == 0 and (self.is_player(player, 13, 14, board) and self.is_player(player, 12, 14, board) or \
            self.is_player(player, 10, 12, board) and self.is_player(player, 12, 14, board))),

            (board[16] == 0 and (self.is_player(player, 17, 18, board) and self.is_player(player, 18, 19, board) or \
            self.is_player(player, 19, 21, board) and self.is_player(player, 18, 19, board))),

            (board[17] == 0 and (self.is_player(player, 16, 18, board) and self.is_player(player, 16, 9, board) or \
            self.is_player(player, 1, 9, board) and self.is_player(player, 16, 18, board))),

            (board[18] == 0 and (self.is_player(player, 16, 17, board) and self.is_player(player, 17, 20, board) or \
            self.is_player(player, 20, 23, board) and self.is_player(player, 17, 20, board))),

            (board[19] == 0 and (self.is_player(player, 16, 21, board) and self.is_player(player, 16, 11, board) or \
            self.is_player(player, 3, 11, board) and self.is_player(player, 16, 21, board))),

            (board[20] == 0 and (self.is_player(player, 18, 23, board) and self.is_player(player, 12, 18, board) or \
            self.is_player(player, 4, 12, board) and self.is_player(player, 18, 23, board))),

            (board[21] == 0 and (self.is_player(player, 16, 19, board) and self.is_player(player, 19, 22, board) or \
            self.is_player(player, 22, 23, board) and self.is_player(player, 19, 22, board))),

            (board[22] == 0 and (self.is_player(player, 21, 23, board) and self.is_player(player, 14, 21, board) or \
            self.is_player(player, 6, 14, board) and self.is_player(player, 21, 23, board))),

            (board[23] == 0 and (self.is_player(player, 18, 20, board) and self.is_player(player, 20, 22, board) or \
            self.is_player(player, 21, 22, board) and self.is_player(player, 20, 22, board)))
        ]

        return diagonal[cell]

    # direction = (pos, soldier, dead_opponent_pos)
    def succ(self, player, player_idx, direction):
        ## direction only has meaning in return
        ## direction (cell,player_soldier,dead_soldier)
        # player_pos[player_soldier] = cell
        # if dead_soldier != -1
        #     rival[dead_soldier] = -1
        if player_idx == 2:
            tmp = player.player_pos
            player.player_pos = player.rival_pos
            player.rival_pos = tmp
        ## PHASE 1
        if player.turn_count < 9:
            for i in range(24):
                if (i not in player.rival_pos) and (i not in player.player_pos):
                    player2 = copy.deepcopy(player)
                    player2.player_pos[player.turn_count-1] = i
                    player2.board[i] = player_idx
                    player2.turn_count += 1
                    if player.is_mill(i):
                        for index, to_kill in enumerate(player.rival_pos):
                            if to_kill != -1 and not player.is_mill(to_kill):
                                player3 = copy.deepcopy(player2)
                                player3.board[player.rival_pos[index]] = 0
                                player3.rival_pos[index] = -2
                                yield player3, 3 - player_idx, (i, player.turn_count, index)
                    else:
                        yield player2, 3 - player_idx, (i, player.turn_count, -1)
        else:
            ## PHASE 2
            for i in range(9):
                if player.player_pos[i] in [-1, -2]:
                    continue
                directions = utils.get_directions(player.player_pos[i])
                for d in directions:
                    if (d not in player.rival_pos) and (d not in player.player_pos):
                        player2 = copy.deepcopy(player)
                        player2.board[player.player_pos[i]] = 0
                        player2.board[d] = player_idx
                        player2.player_pos[i] = d
                        if player2.is_mill(d):
                            for index, to_kill in enumerate(player.rival_pos):
                                if not player.is_mill(to_kill):
                                    player3 = copy.deepcopy(player2)
                                    player3.board[player.rival_pos[index]] = 0
                                    player3.rival_pos[index] = -2
                                    player3.turn_count += 1
                                    yield player3, 3 - player_idx, (d, i, index)
                        else:
                            yield player2, 3 - player_idx, (d, i, -1)


