#  (C) Copyright Wieger Wesselink 2021. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

import random
import time
from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove, print_board
import competitive_sudoku.sudokuai
import numpy as np


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

        # Determine if a certain move is non-taboo in a certain gamestate
        def non_taboo(i, j, value):

            return game_state.board.get(i, j) == SudokuBoard.empty \
                and not TabooMove(i, j, value) in game_state.taboo_moves \
    
        # Create a list of the gamestate board's rows and a list of its columns (used in legal function)
        board_str = game_state.board.squares
        rows = []

        for i in range(N):
            rows.append(board_str[i*N : (i+1)*N])
        
        columns = np.transpose(rows)

        # !!! CREATE A LIST OF THE BOARD'S SECTIONS AND ADD THIS CHECK TO THE LEGAL FUNCTION BELOW !!!

        # Determine if a certain move is legal in a certain gamestate
        def legal(i, j, value):
            
            return not value in rows[i] and not value in columns[j]
   
        # Compute a list of all possible (non-taboo AND legal) moves for a certain gamestate
        possible_moves = [Move(i, j, value) for i in range(N) for j in range(N)
                     for value in range(1, N+1) if ((non_taboo(i, j, value) and legal(i, j, value)))]
            
        print(possible_moves)
        # Pick a random move from the list of possible moves
        move = random.choice(possible_moves)
        self.propose_move(move)

        # Randomly repick the move from the list every 0.2 seconds until the time runs out
        while True:
            time.sleep(0.2)
            self.propose_move(random.choice(possible_moves))

