#  (C) Copyright Wieger Wesselink 2021. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

import random
import time
from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove
import competitive_sudoku.sudokuai


class SudokuAI(competitive_sudoku.sudokuai.SudokuAI):
    """
    Sudoku AI that computes a move for a given sudoku configuration, based on minimax algo.
    """

    def __init__(self):
        super().__init__()

    def compute_best_move(self, game_state: GameState) -> None:
        N = game_state.board.N
        m = game_state.board.m
        n = game_state.board.n

        # Determine if a certain move is possible (non-taboo AND legal) in a certain gamestate
        def possible(i, j, value):
            return game_state.board.get(i, j) == SudokuBoard.empty \
                   and not TabooMove(i, j, value) in game_state.taboo_moves \
                    and not game_state.board.get(i, j) in SudokuBoard[i,:] \
                    and not game_state.board.get(i, j) in SudokuBoard[:,j] \
                    # check if value does not occur in region below:
   
        # Compute a list of all possible (non-taboo AND legal) moves for a certain gamestate
        possible_moves = [Move(i, j, value) for i in range(N) for j in range(N)
                     for value in range(1, N+1) if possible(i, j, value)]

        # Pick a random move from the list of possible moves
        move = random.choice(possible_moves)
        self.propose_move(move)

        # Randomly repick the move from the list every 0.2 seconds until the time runs out
        while True:
            time.sleep(0.2)
            self.propose_move(random.choice(possible_moves))

