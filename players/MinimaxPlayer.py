"""
MiniMax Player
"""
from players.AbstractPlayer import AbstractPlayer
#TODO: you can import more modules, if needed

class Player(AbstractPlayer):
    def __init__(self, game_time):
        AbstractPlayer.__init__(self, game_time)  # keep the inheritance of the parent's (AbstractPlayer) __init__()
        self.board
        self.turn_count = 0   # increase when make moves

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
        # raise NotImplementedError
        
        self.board = board

    def make_move(self, time_limit):
        """Make move with this Player.
        input:
            - time_limit: float, time limit for a single turn.
        output:
            - direction: tuple, specifing the Player's movement
            :return: move = (pos, soldier, dead_opponent_pos)
        """
        #TODO: erase the following line and implement this function.

        raise NotImplementedError

    def set_rival_move(self, move):
        """Update your info, given the new position of the rival.
        input:
            - move: tuple, the new position of the rival.
        No output is expected
        """
        # TODO: erase the following line and implement this function.
        raise NotImplementedError



    ########## helper functions in class ##########
    # TODO: add here helper functions in class, if needed

    def calculate_state_heuristic(self, board):
        mill_num = 0
        rival_mill_num = 0
        incomplete_mills = 0
        rival_incomplete_mills = 0
        blocked_soldiers = 0
        rival_blocked_soldiers = 0
        incomplete_mills_that_player_cant_block = 0
        incomplete_mills_that_rival_cant_block = 0
        for cell in board:
            if cell is 1:
                if self.is_mill(cell):
                    mill_num += 1
                if self.check_if_blocked(cell, 1, board):
                    blocked_soldiers += 1
                if self.check_next_mill(cell, 1):
                    incomplete_mills += 1
                if self.is_unblocked_mill(cell, 1, board):
                    incomplete_mills_that_rival_cant_block += 1
            elif cell is 2:
                if self.is_mill(cell):
                    rival_mill_num += 1
                if self.check_if_blocked(cell, 2, board):
                    rival_blocked_soldiers += 1
                if self.check_next_mill(cell, 2):
                    rival_incomplete_mills += 1
                if self.is_unblocked_mill(cell, 2, board):
                    incomplete_mills_that_player_cant_block += 1
        return 0.15 * incomplete_mills + \
               0.1 * (incomplete_mills - rival_incomplete_mills) + \
               0.3 * (mill_num - rival_mill_num) + \
               0.2 * (rival_blocked_soldiers - blocked_soldiers) + \
               0.25 * (incomplete_mills_that_rival_cant_block - incomplete_mills_that_player_cant_block)


    ########## helper functions for AlphaBeta algorithm ##########
    # TODO: add here the utility, succ, an

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
        blocked = [
            (self.is_player(rival, 1, 3, board)),                                             # 0
            (self.is_player(rival, 0, 2, board) and self.is_player(rival, 9, 0, board)),      # 1
            (self.is_player(rival, 1, 4, board)),                                             # 2
            (self.is_player(rival, 0, 5, board) and self.is_player(rival, 11, 5, board)),     # 3
            (self.is_player(rival, 2, 7, board) and self.is_player(rival, 12, 7, board)),     # 4
            (self.is_player(rival, 3, 6, board)),                                             # 5
            (self.is_player(rival, 5, 7, board) and self.is_player(rival, 14, 5, board)),     # 6
            (self.is_player(rival, 4, 6, board)),                                             # 7
            (self.is_player(rival, 9, 11, board)),                                            # 8
            (self.is_player(rival, 8, 10, board) and self.is_player(rival, 10, 17, board)),   # 9
            (self.is_player(rival, 9, 12, board)),                                            # 10
            (self.is_player(rival, 3, 19, board) and self.is_player(rival, 8, 13, board)),    # 11
            (self.is_player(rival, 20, 4, board) and self.is_player(rival, 10, 15, board)),   # 12
            (self.is_player(rival, 11, 14, board)),                                           # 13
            (self.is_player(rival, 13, 15, board) and self.is_player(rival, 6, 22, board)),   # 14
            (self.is_player(rival, 12, 14, board)),                                           # 15
            (self.is_player(rival, 17, 19, board)),                                           # 16
            (self.is_player(rival, 16, 9, board) and self.is_player(rival, 16, 18, board)),   # 17
            (self.is_player(rival, 20, 17, board)),                                           # 18
            (self.is_player(rival, 16, 21, board) and self.is_player(rival, 16, 11, board)),  # 19
            (self.is_player(rival, 12, 18, board) and self.is_player(rival, 18, 23, board)),  # 20
            (self.is_player(rival, 22, 19, board)),                                           # 21
            (self.is_player(rival, 21, 14, board) and self.is_player(rival, 21, 23, board)),  # 22
            (self.is_player(rival, 22, 20, board))                                            # 23
        ]

        return blocked[position]
    
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
            (board[0] is 0 and (self.is_player(player, 3, 5, board) and self.is_player(player, 1, 3, board) or \
             self.is_player(player, 1, 2, board) and self.is_player(player, 1, 3, board))),
             
            (board[1] is 0 and (self.is_player(player, 0, 2, board) and self.is_player(player, 0, 9, board) or \
             self.is_player(player, 9, 17, board) and self.is_player(player, 0, 2, board))),
            
            (board[2] is 0 and (self.is_player(player, 4, 7, board) and self.is_player(player, 1, 4, board) or \
            self.is_player(player, 0, 1, board) and self.is_player(player, 1, 4, board))),

            (board[3] is 0 and (self.is_player(player, 0, 11, board) and self.is_player(player, 0, 5, board) or \
            self.is_player(player, 11, 19, board) and self.is_player(player, 0, 5, board))),

            (board[4] is 0 and (self.is_player(player, 2, 7, board) and self.is_player(player, 2, 12, board) or \
            self.is_player(player, 2, 7, board) and self.is_player(player, 12, 20, board))),

            (board[5] is 0 and (self.is_player(player, 6, 7, board) and self.is_player(player, 3, 6, board) or \
            self.is_player(player, 0, 3, board) and self.is_player(player, 3, 6, board))),

            (board[6] is 0 and (self.is_player(player, 5, 7, board) and self.is_player(player, 5, 14, board) or \
            self.is_player(player, 14, 22, board) and self.is_player(player, 5, 14, board))),

            (board[7] is 0 and (self.is_player(player, 5, 6, board) and self.is_player(player, 6, 4, board) or \
            self.is_player(player, 2, 4, board) and self.is_player(player, 6, 4, board))),

            (board[8] is 0 and (self.is_player(player, 9, 10, board) and self.is_player(player, 10, 11, board) or \
            self.is_player(player, 11, 13, board) and self.is_player(player, 10, 11, board))),

            (board[9] is 0 and (self.is_player(player, 1, 17, board) and self.is_player(player, 8, 10, board))),

            (board[10] is 0 and (self.is_player(player, 8, 9, board) and self.is_player(player, 9, 12, board) or \
            self.is_player(player, 12, 15, board) and self.is_player(player, 9, 12, board))),

            (board[11] is 0 and (self.is_player(player, 3, 19, board) and self.is_player(player, 8, 13, board))),

            (board[12] is 0 and (self.is_player(player, 4, 20, board) and self.is_player(player, 10, 15, board))),

            (board[13] is 0 and (self.is_player(player, 8, 11, board) and self.is_player(player, 11, 14, board) or \
            self.is_player(player, 14, 15, board) and self.is_player(player, 11, 14, board))),

            (board[14] is 0 and (self.is_player(player, 6, 22, board) and self.is_player(player, 13, 15, board))),

            (board[15] is 0 and (self.is_player(player, 13, 14, board) and self.is_player(player, 12, 14, board) or \
            self.is_player(player, 10, 12, board) and self.is_player(player, 12, 14, board))),

            (board[16] is 0 and (self.is_player(player, 17, 18, board) and self.is_player(player, 18, 19, board) or \
            self.is_player(player, 19, 21, board) and self.is_player(player, 18, 19, board))),

            (board[17] is 0 and (self.is_player(player, 16, 18, board) and self.is_player(player, 16, 9, board) or \
            self.is_player(player, 1, 9, board) and self.is_player(player, 16, 18, board))),

            (board[18] is 0 and (self.is_player(player, 16, 17, board) and self.is_player(player, 17, 20, board) or \
            self.is_player(player, 20, 23, board) and self.is_player(player, 17, 20, board))),

            (board[19] is 0 and (self.is_player(player, 16, 21, board) and self.is_player(player, 16, 11, board) or \
            self.is_player(player, 3, 11, board) and self.is_player(player, 16, 21, board))),

            (board[20] is 0 and (self.is_player(player, 18, 23, board) and self.is_player(player, 12, 18, board) or \
            self.is_player(player, 4, 12, board) and self.is_player(player, 18, 23, board))),

            (board[21] is 0 and (self.is_player(player, 16, 19, board) and self.is_player(player, 19, 22, board) or \
            self.is_player(player, 22, 23, board) and self.is_player(player, 19, 22, board))),

            (board[22] is 0 and (self.is_player(player, 21, 23, board) and self.is_player(player, 14, 21, board) or \
            self.is_player(player, 6, 14, board) and self.is_player(player, 21, 23, board))),

            (board[23] is 0 and (self.is_player(player, 18, 20, board) and self.is_player(player, 20, 22, board) or \
            self.is_player(player, 21, 22, board) and self.is_player(player, 20, 22, board)))
        ]

        return blocked[position]