#  (C) Copyright Wieger Wesselink 2021. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

import random
import time
from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove, print_board
import competitive_sudoku.sudokuai


# Check if numpy can be used!
import numpy as np
import math
import math

class SudokuAI(competitive_sudoku.sudokuai.SudokuAI):
    """
    Sudoku AI that computes a move for a given sudoku configuration, based on minimax algo.
    """
    def __init__(self):
        super().__init__()

    def compute_best_move(self, game_state: GameState) -> None:
        N = game_state.board.N

        # Determine if a certain move is non-taboo in a certain gamestate
        def non_taboo(i, j, value):
            return game_state.board.get(i, j) == SudokuBoard.empty \
                   and not Move(i, j, value) in game_state.taboo_moves
    
        # Create a list of the gamestate board's rows and a list of its columns (used in legal function)
        board_str = game_state.board.squares
        rows = []

        for i in range(N):
            rows.append(board_str[i*N : (i+1)*N])
        
        columns = np.transpose(rows)

        # Determine if action is legal (not already present in section, row or column)
        def legal(i,j,value,data):
            size = int(np.sqrt(len(rows)))
            row = math.floor(i / size)
            col = math.floor(j/size)
            y= np.vstack([xi for xi in data])
            return not value in np.array(y[row*size:row*size+size,col*size:col*size+size]).reshape(-1,).tolist() and not value in rows[i] and not value in columns[j]
   
        non_taboo_moves = []
        possible_moves = []

        for i in range(N):
            for j in range(N):
                for value in range(1, N+1):
                    if non_taboo(i, j, value):
                        non_taboo_moves.append(Move(i, j, value))
                        if legal(i, j, value, rows):
                            possible_moves.append(Move(i, j, value))
        
        #Getting the output 
        current_board = game_state.board
        x = print(current_board)

        for i in range(N):
            for j in range(N):
                for value in range(1, N+1):
                    if non_taboo(i, j, value):
                        non_taboo_moves.append(Move(i, j, value))
                        if legal(i, j, value, rows):
                            game_state.board.put(i,j,value)
                            board_str = game_state.board
                            print(board_str)

        # print('NON-TABOO MOVES:')
        # for move in non_taboo_moves:
        #     print(move)        
        print('TABOO MOVES:')
        for move in game_state.taboo_moves:
            print(move)
        print('POSSIBLE MOVES (LEGAL AND NON-TABOO):')
        for move in possible_moves:
            print(move)
        print('CURRENT SCORE')
        for move in game_state.scores:
            print(move)
        print('historic moves')
        for move in game_state.moves:
            print(move)

        move = random.choice(possible_moves)
        self.propose_move(move)

        # Randomly repick the move from the list every 0.2 seconds until the time runs out
        while True:
            time.sleep(0.2)
            self.propose_move(random.choice(possible_moves))
