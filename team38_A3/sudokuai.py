#  (C) Copyright Wieger Wesselink 2021. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

import random
# import time
from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove, print_board
import competitive_sudoku.sudokuai

# Extra packages:
import numpy as np
from copy import deepcopy

class SudokuAI(competitive_sudoku.sudokuai.SudokuAI):
    """
    Sudoku AI that computes a move for a given sudoku configuration, based on minimax algo.
    """
    def __init__(self):
        super().__init__()

    def compute_best_move(self, game_state: GameState) -> None:
        """Computes the best move for the given gamestate.
        @param game_state: the current gamestate of the board.
        """
        N = game_state.board.N

        def emptyList(board) -> list:
            """Returns a list with all the empty squares.
            @param board: the board with N**2 entries.
            """

            board = game_state.board
            empty_list = []
            for a in range(N**2):
                i,j = SudokuBoard.f2rc(board, a)
                if board.get(i,j) == SudokuBoard.empty:
                    empty_list.append([i,j])
            return empty_list 

        def extractPossibleMoves 

        def getChildren(state, isMaximisingPlayer):
            """Returns for each move the new board, score and the move itself.
            @param state: 
            """
            pairs = []
            for move in extractPossibleMoves(state):
                child_board = deepcopy(state)
                child_board.board.put(move.i, move.j, move.value)
                new_score = scoreFunction(move, child_board)
                list = [child_board, new_score, move]
                pairs.append(list)
            return pairs
