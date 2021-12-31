"""
MiniMax Player
"""
from players.AbstractPlayer import AbstractPlayer
# TODO: you can import more modules, if needed
import numpy as np
import utils
import time
import SearchAlgos
import copy


############################# make deep copy for player class - search arg and yield of succ function ##################################################

class Player(AbstractPlayer):
    def __init__(self, game_time):
        AbstractPlayer.__init__(self, game_time)  # keep the inheritance of the parent's (AbstractPlayer) __init__()
        self.turn_count = -1  # increase when make moves
        self.player_pos = np.full(9, -1)
        self.rival_pos = np.full(9, -1)
        self.player_index = -1
        self.rival_index = -1
        self.real_index = -1
        self.AlphaBeta = False
        # TODO: initialize more fields, if needed, and the AlphaBeta algorithm from SearchAlgos.py

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
        if self.turn_count < 1:
            if self.turn_count == -1:
                self.player_index = 1
                self.real_index = 1
                self.rival_index = 2
            else:
                self.player_index = 2
                self.real_index = 2
                self.rival_index = 1
            self.turn_count += 1

        start = time.time()
        end = start + time_limit
        max_value = -np.inf
        # direction (the new cell, soldier - 10 sized array, rival dead soldier - 10 sized array)
        best_move = (-1, -1, -1)
        depth = 1
        # state = (self.board, self.turn_count, self.player_pos, self.rival_pos, 1, best_move)
        if self.AlphaBeta:
            minimax = SearchAlgos.AlphaBeta(self.calculate_state_heuristic, self.succ, None, self.check_end_game)
        else:
            minimax = SearchAlgos.MiniMax(self.calculate_state_heuristic, self.succ, None, self.check_end_game)
        end_phase = 0
        time_condition = 0
        # while end - time.time() > 63 * end_phase:
        # phase 1 : (24-turn)*(24-turn-(depth-1))*...*() => (24-turn-(depth-1)) * int(turn/2)
        while end - time.time() > time_condition * end_phase:
            start_phase = time.time()
            value, direction = minimax.search((copy.deepcopy(self), self.player_index, best_move), depth, True)
            if value > max_value:
                best_move = direction
                max_value = value
            end_phase = time.time() - start_phase
            phase_1_end = (24 - self.turn_count - depth) + 2 * (np.count_nonzero(self.rival_pos > -1))
            phase_2_end = 2.5 * (np.count_nonzero(self.player_pos > -1)) + 1 * (np.count_nonzero(
                self.rival_pos > -1))  ## 2.5 is avg branch of soldier + (avg soldiers able to kill) * kill
            time_condition = phase_1_end if self.turn_count < 18 else phase_2_end
            depth += 1
        # update self values
        cell, my_soldier, rival_soldier_cell = best_move
        self.turn_count += 1

        self.board[self.player_pos[my_soldier]] = 0
        self.board[cell] = self.player_index
        self.player_pos[my_soldier] = cell
        if rival_soldier_cell != -1:
            self.board[rival_soldier_cell] = 0
            dead_soldier = int(np.where(self.rival_pos == rival_soldier_cell)[0][0])
            self.rival_pos[dead_soldier] = -2
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
            self.board[rival_pos] = self.rival_index
            self.rival_pos[rival_soldier] = rival_pos
        else:
            rival_prev_pos = self.rival_pos[rival_soldier]
            self.board[rival_prev_pos] = 0
            self.board[rival_pos] = self.rival_index
            self.rival_pos[rival_soldier] = rival_pos
        if my_dead_pos != -1:
            self.board[my_dead_pos] = 0
            dead_soldier = int(np.where(self.player_pos == my_dead_pos)[0][0])
            self.player_pos[dead_soldier] = -2
        self.turn_count += 1

    ########## helper functions in class ##########
    # TODO: add here helper functions in class, if needed

    def check_end_game(self, player) -> bool:
        if self.player_index == 1:
            dead = np.where(player.player_pos != -2)[0]
        else:
            dead = np.where(player.rival_pos != -2)[0]
        if len(dead) >= 3:
            return False
        for index, x in enumerate(self.rival_pos):
            if x > -1 and not self.check_if_blocked(x):
                return False
        for index, x in enumerate(self.player_pos):
            if x > -1 and not self.check_if_blocked(x):
                return False
        return True

    ########## helper functions for AlphaBeta algorithm ##########
    # TODO: add here the utility, succ, an

    # heuristic of phase 1

    def enable_alpha_beta(self):
        self.AlphaBeta = True

    def calculate_state_heuristic(self, state):
        player = state[0]
        index = state[1]
        return player.heuristic_value()

    def heuristic_value(self):
        player_mill_num = 0
        rival_mill_num = 0
        player_incomplete_mills = 0
        rival_incomplete_mills = 0
        player_blocked_soldiers = 0
        rival_blocked_soldiers = 0
        rival_double_mill = 0
        player_double_mill = 0
        player_winning_config = 1 if self.check_end_game(self.player_index) else 0
        rival_winning_config = 1 if self.check_end_game(self.rival_index) else 0
        player_soldier = np.count_nonzero(self.player_pos > -1)
        rival_soldier = np.count_nonzero(self.rival_pos > -1)
        board = self.board
        for index, x in enumerate(board):
            cell = int(x)
            if cell == self.player_index:
                if self.is_mill(index):
                    player_mill_num += 1 / 3
                if self.check_if_blocked(index, board):
                    player_blocked_soldiers += 1
                if self.is_double_mill(index):
                    player_double_mill += 1
            elif cell == self.rival_index:
                if self.is_mill(index):
                    rival_mill_num += 1 / 3
                if self.is_double_mill(index):
                    rival_double_mill += 1
                if self.check_if_blocked(index, board):
                    rival_blocked_soldiers += 1
            elif cell == 0:
                if self.check_next_mill(index, self.player_index, board):
                    player_incomplete_mills += 1
                if self.check_next_mill(index, self.player_index, board):
                    rival_incomplete_mills += 1
                # if self.is_unblocked_mill(index, player_index, board):
                #     incomplete_mills_that_rival_cant_block += 1
                # if self.is_unblocked_mill(index, rival_index, board):
                #     incomplete_mills_that_player_cant_block += 1
                # if self.is_diagonal(cell):
                #     diagonal_placement += 1
        player_three_config = 1 if player_incomplete_mills >= 2 else 0
        rival_three_config = 1 if rival_incomplete_mills >= 2 else 0
        if self.turn_count < 18:
            return 26 * (player_mill_num - rival_mill_num) + \
                   10 * (player_incomplete_mills - rival_incomplete_mills) + \
                   9 * (player_soldier - rival_soldier) + \
                   1 * (player_blocked_soldiers - rival_blocked_soldiers) + \
                   7 * (player_three_config - rival_three_config) + \
                   100 * (player_winning_config - rival_winning_config)
        else:
            return 43 * (player_mill_num - rival_mill_num) + \
                   11 * (player_soldier - rival_soldier) + \
                   10 * (player_blocked_soldiers - rival_blocked_soldiers) + \
                   100 * (player_winning_config - rival_winning_config)

    # direction = (pos, soldier, dead_opponent_pos)
    def succ(self, player, player_idx, direction):
        if player_idx != player.real_index:
            player.switch_player_rival()
        # PHASE 1
        if player.turn_count < 18:
            soldier_that_moved = int(np.where(player.player_pos == -1)[0][0])
            for i in range(24):
                if (i not in player.rival_pos) and (i not in player.player_pos):
                    player2 = copy.deepcopy(player)
                    player2.player_pos[soldier_that_moved] = i
                    player2.board[i] = player_idx
                    player2.turn_count += 1
                    if player2.is_mill(i):
                        for index, to_kill in enumerate(player2.rival_pos):
                            if to_kill not in [-1, -2]:
                                player3 = copy.deepcopy(player2)
                                kill_index = player3.rival_pos[index]
                                player3.board[kill_index] = 0
                                player3.rival_pos[index] = -2
                                if player_idx != player.real_index:
                                    player3.switch_player_rival()
                                yield player3, 3 - player_idx, (i, soldier_that_moved, kill_index)
                    else:
                        if player_idx != player.real_index:
                            player2.switch_player_rival()
                        yield player2, 3 - player_idx, (i, soldier_that_moved, -1)
        else:
            # PHASE 2
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
                        player2.turn_count += 1
                        if player2.is_mill(d):
                            for index, to_kill in enumerate(player2.rival_pos):
                                if to_kill not in [-1, -2]:
                                    player3 = copy.deepcopy(player2)
                                    kill_index = player3.rival_pos[index]
                                    player3.board[kill_index] = 0
                                    player3.rival_pos[index] = -2
                                    if player_idx != player.real_index:
                                        player3.switch_player_rival()
                                    yield player3, 3 - player_idx, (d, i, kill_index)
                        else:
                            if player_idx != player.real_index:
                                player2.switch_player_rival()
                            yield player2, 3 - player_idx, (d, i, -1)

    def switch_player_rival(self):
        tmp = self.player_pos
        self.player_pos = self.rival_pos
        self.rival_pos = tmp
        self.player_index = self.rival_index
        self.rival_index = 3 - self.player_index

    def check_if_blocked(self, position, board=None):
        """
        Function to check if a player can make a mill in the next move.
        :param position: curren position
        :param board: np.array
        :param player: 1/2
        :return:
        """
        if board is None:
            board = self.board

        for i in utils.get_directions(position):
            if board[i] == 0:  # need to be changed
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

    def is_double_mill(self, position):
        """
        Return True if a player has a mill on the given position
        :param position: 0-23
        :return:
        """
        if position < 0 or position > 23:
            return False
        p = int(self.board[position])

        # The player on that position
        if p != 0:
            # If there is some player on that position
            return self.check_double_mill(position, p, self.board)
        else:

            return False

    def check_double_mill(self, position, player, board):
        mill = [
            (self.is_player(player, 1, 2, board) and self.is_player(player, 3, 5, board)),
            (self.is_player(player, 0, 2, board) and self.is_player(player, 9, 17, board)),
            (self.is_player(player, 0, 1, board) and self.is_player(player, 4, 7, board)),
            (self.is_player(player, 0, 5, board) and self.is_player(player, 11, 19, board)),
            (self.is_player(player, 2, 7, board) and self.is_player(player, 12, 20, board)),
            (self.is_player(player, 0, 3, board) and self.is_player(player, 6, 7, board)),
            (self.is_player(player, 5, 7, board) and self.is_player(player, 14, 22, board)),
            (self.is_player(player, 2, 4, board) and self.is_player(player, 5, 6, board)),
            (self.is_player(player, 9, 10, board) and self.is_player(player, 11, 13, board)),
            (self.is_player(player, 8, 10, board) and self.is_player(player, 1, 17, board)),
            (self.is_player(player, 8, 9, board) and self.is_player(player, 12, 15, board)),
            (self.is_player(player, 3, 19, board) and self.is_player(player, 8, 13, board)),
            (self.is_player(player, 20, 4, board) and self.is_player(player, 10, 15, board)),
            (self.is_player(player, 8, 11, board) and self.is_player(player, 14, 15, board)),
            (self.is_player(player, 13, 15, board) and self.is_player(player, 6, 22, board)),
            (self.is_player(player, 13, 14, board) and self.is_player(player, 10, 12, board)),
            (self.is_player(player, 17, 18, board) and self.is_player(player, 19, 21, board)),
            (self.is_player(player, 1, 9, board) and self.is_player(player, 16, 18, board)),
            (self.is_player(player, 16, 17, board) and self.is_player(player, 20, 23, board)),
            (self.is_player(player, 16, 21, board) and self.is_player(player, 3, 11, board)),
            (self.is_player(player, 12, 4, board) and self.is_player(player, 18, 23, board)),
            (self.is_player(player, 16, 19, board) and self.is_player(player, 22, 23, board)),
            (self.is_player(player, 6, 14, board) and self.is_player(player, 21, 23, board)),
            (self.is_player(player, 18, 20, board) and self.is_player(player, 21, 22, board))
        ]
        return mill[position]
