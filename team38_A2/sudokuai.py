#  (C) Copyright Wieger Wesselink 2021. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

import random
import time
from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove, print_board
import competitive_sudoku.sudokuai

# Extra packages:
import numpy as np
import math
from copy import deepcopy

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
            
            root_row = np.sqrt(len(data))
            size_row = int(root_row // 1)
            
            root_col = np.sqrt(len(data))
            size_col = int(-1 * root_col // 1 * -1)
         
            prep_row = move.i/size_row
            row = int(prep_row // 1)

            prep_col = move.j/size_col
            col = int(prep_col // 1)

            # size_row = math.floor(np.sqrt(len(data)))
            # size_col = math.ceil(np.sqrt(len(data)))
            # row = math.floor(i/size_row)
            # col = math.floor(j/size_col)

            y= np.vstack([xi for xi in data])
            return not value in np.array(y[row*size_row:row*size_row+size_row,col*size_col \
                :col*size_col+size_col]).reshape(-1,).tolist() and not value in rows[i] and not value in columns[j]
   
        # Generate a list of all possible moves (legal AND non-taboo)
        possible_moves = []

        for i in range(N):
            for j in range(N):
                for value in range(1, N+1):
                    if non_taboo(i, j, value):
                        if legal(i, j, value, rows):
                            possible_moves.append(Move(i, j, value))

        self.propose_move(random.choice(possible_moves))

        # Create copies of the current board's rows and columns, for use in the for loop below
        current_rows = deepcopy(rows)
        current_columns = deepcopy(columns)
        best_count = 0

        # Select the move that leads to the maximal score
        for move in possible_moves:

            # Check if a row, column, or both are completed by a certain move
            # and if so: add 1 to the counter
            current_row_complete = not 0 in current_rows[move.i]
            current_column_complete = not 0 in current_columns[move.j]

            new_rows = deepcopy(current_rows)
            new_rows[move.i][move.j] = move.value
            new_columns = np.transpose(new_rows)

            new_row_complete = not 0 in new_rows[move.i]
            new_column_complete = not 0 in new_columns[move.j]
            
            count = 0
            if new_row_complete and not current_row_complete:
                count += 1
            if new_column_complete and not current_column_complete: 
                count += 1

            # Check if a section is completed, and if so add 1 to the counter
            root_row = np.sqrt(len(current_rows))
            size_row = int(root_row // 1)
            # size_row_old = math.floor(np.sqrt(len(current_rows)))
            # print("size row", size_row, size_row_old)

            root_col = np.sqrt(len(current_rows))
            size_col = int(-1 * root_col // 1 * -1)
            # size_col_old = math.ceil(np.sqrt(len(current_rows)))
            # print("size col", size_col, size_col_old)

            prep_row = move.i/size_row
            row = int(prep_row // 1)
            # row_old = math.floor(move.i/size_row)
            # print("size row", row, row_old)

            prep_col = move.j/size_col
            col = int(prep_col // 1)
            # col_old = math.floor(move.j/size_col) 
            # print("size row", col, col_old)

            y= np.vstack([xi for xi in current_rows])           
            current_section = np.array(y[row*size_row:row*size_row+size_row,col*size_col:col*size_col+size_col]).reshape(-1,).tolist()
                    
            if current_section.count(0) == 1:
                count += 1

            # Select the move with the highest count, which results in the highest score
            if count > best_count:
                best_count = count
                self.propose_move(move)