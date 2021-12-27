"""Search Algos: MiniMax, AlphaBeta
"""
from math import inf
#TODO: you can import more modules, if needed
#TODO: update ALPHA_VALUE_INIT, BETA_VALUE_INIT in utils
import time
import numpy as np
ALPHA_VALUE_INIT = -np.inf
BETA_VALUE_INIT = np.inf # !!!!!

class SearchAlgos:
    def __init__(self, utility, succ, perform_move=None, goal=None):
        """The constructor for all the search algos.
        You can code these functions as you like to, 
        and use them in MiniMax and AlphaBeta algos as learned in class
        :param utility: The utility function.
        :param succ: The succesor function.
        :param perform_move: The perform move function.
        :param goal: function that check if you are in a goal state.
        """
        self.utility = utility
        self.succ = succ
        self.perform_move = perform_move
        self.goal = goal

    def search(self, state, depth, maximizing_player):
        pass


class MiniMax(SearchAlgos):

    def search(self, state, depth, maximizing_player):
        """Start the MiniMax algorithm.
        :param state: The state to start from.
        :param depth: The maximum allowed depth for the algorithm.
        :param maximizing_player: Whether this is a max node (True) or a min node (False).
        :return: A tuple: (The min max algorithm value, The direction in case of max node or None in min mode)
        """
        # state = (board,turn,player_pos,rival_pos)
        board = state[0]
        if self.goal(board) or depth == 0:
            if maximizing_player:
                return self.utility(state), state ## state needs to be direction ?
            else:
                return self.utility(state), None
        if maximizing_player:
            curr_max = -np.inf
            for c in self.succ(state):
                curr = self.search(c, depth-1, False)
                curr_max = max(curr[0], curr_max[0])
            return curr_max
        else:
            curr_min = np.inf
            for c in self.succ(state):
                curr = self.search(c, depth-1, True)
                curr_min = min(curr[0], curr_min[0])
            return curr_min

class AlphaBeta(SearchAlgos):

    def search(self, state, depth, maximizing_player, alpha=ALPHA_VALUE_INIT, beta=BETA_VALUE_INIT):
        """Start the AlphaBeta algorithm.
        :param state: The state to start from.
        :param depth: The maximum allowed depth for the algorithm.
        :param maximizing_player: Whether this is a max node (True) or a min node (False).
        :param alpha: alpha value
        :param: beta: beta value
        :return: A tuple: (The min max algorithm value, The direction in case of max node or None in min mode)
        """
        # state = (board,turn,player_pos)
        board = state[0]
        if self.goal(board) or depth == 0:
            if maximizing_player:
                return self.utility(state), state ## state needs to be direction ?
            else:
                return self.utility(state), None
        if maximizing_player:
            curr_max = -np.inf
            for c in self.succ(state):
                curr = self.search(c, depth-1, False, alpha, beta)
                curr_max = max(curr[0], curr_max[0])
                alpha = max(curr_max[0], alpha)
                if curr_max >= beta:
                    return np.inf, None
            return curr_max

        else:
            curr_min = np.inf
            for c in self.succ(state):
                curr = self.search(c, depth-1, True, alpha, beta)
                curr_min = min(curr[0], curr_min[0])
                beta = min(curr_min[0], beta)
                if curr_min <= alpha:
                    return -np.inf, None
            return curr_min
