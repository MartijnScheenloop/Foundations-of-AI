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

    # def compute_best_move(self, game_state: GameState) -> None:
    #     N = game_state.board.N

    #     # Determine if a certain move is non-taboo in a certain gamestate
    #     def non_taboo(i, j, value):
    #         return game_state.board.get(i, j) == SudokuBoard.empty \
    #                and not Move(i, j, value) in game_state.taboo_moves
    
    #     # Create a list of the gamestate board's rows and a list of its columns (used in legal function)
    #     board_str = game_state.board.squares
    #     rows = []

    #     for i in range(N):
    #         rows.append(board_str[i*N : (i+1)*N])
        
    #     columns = np.transpose(rows)

    #     # Determine if action is legal (not already present in section, row or column)
    #     def legal(i,j,value,data):
    #         size_row = math.floor(np.sqrt(len(data)))
    #         size_col = math.ceil(np.sqrt(len(data)))
    #         row = math.floor(i/size_row)
    #         col = math.floor(j/size_col)
    #         y= np.vstack([xi for xi in data])
    #         return not value in np.array(y[row*size_row:row*size_row+size_row,col*size_col \
    #             :col*size_col+size_col]).reshape(-1,).tolist() and not value in rows[i] and not value in columns[j]
   
    #     # Generate a list of all possible moves (legal AND non-taboo)
    #     possible_moves = []

    #     for i in range(N):
    #         for j in range(N):
    #             for value in range(1, N+1):
    #                 if non_taboo(i, j, value):
    #                     if legal(i, j, value, rows):
    #                         possible_moves.append(Move(i, j, value))

    #     self.propose_move(random.choice(possible_moves))

    #     # Create copies of the current board's rows and columns, for use in the for loop below
    #     current_rows = deepcopy(rows)
    #     current_columns = deepcopy(columns)
    #     best_count = 0

    #     # Select the move that leads to the maximal score
    #     for move in possible_moves:

    #         # Check if a row, column, or both are completed by a certain move
    #         # and if so: add 1 to the counter
    #         current_row_complete = not 0 in current_rows[move.i]
    #         current_column_complete = not 0 in current_columns[move.j]

    #         new_rows = deepcopy(current_rows)
    #         new_rows[move.i][move.j] = move.value
    #         new_columns = np.transpose(new_rows)

    #         new_row_complete = not 0 in new_rows[move.i]
    #         new_column_complete = not 0 in new_columns[move.j]
            
    #         count = 0
    #         if new_row_complete and not current_row_complete:
    #             count += 1
    #         if new_column_complete and not current_column_complete: 
    #             count += 1

    #         # Check if a section is completed, and if so add 1 to the counter
    #         size_row = math.floor(np.sqrt(len(current_rows)))
    #         size_col = math.ceil(np.sqrt(len(current_rows)))
    #         row = math.floor(move.i/size_row)
    #         col = math.floor(move.j/size_col) 
    #         y= np.vstack([xi for xi in current_rows])           
    #         current_section = np.array(y[row*size_row:row*size_row+size_row,col*size_col:col*size_col+size_col]).reshape(-1,).tolist()
                    
    #         if current_section.count(0) == 1:
    #             count += 1

    #         # Select the move with the highest count, which results in the highest score
    #         if count > best_count:
    #             best_count = count
    #             self.propose_move(move)


##################################################################################################

    def compute_best_move(self, game_state: GameState) -> None:

        # Quantify stage of the game and based on that pick a move selection tactic

        N = game_state.board.N
        N_empty_squares = game_state.board.squares.count(0)
        N_total_squares = N*N
        fraction_filled = 1 - N_empty_squares/N_total_squares
        print(fraction_filled)

        # # If board is relatively empty (define):

        # if fraction_filled <= 0.2:
            


        #     self.propose_move(x)

        # If board is partly filled but far from totally filled, use Last Possible Number:

        if fraction_filled >= 0:
        # and fraction_filled < 0.5:
            board = game_state.board
            board_str = board.squares

            rows = []
            N = game_state.board.N
            for i in range(N):
                rows.append(board_str[i*N : (i+1)*N])
            columns = list(np.transpose(rows))

            sections = np.vstack([xi for xi in rows])

            print(rows)
            print(columns)
            print(sections)

            def not_possible(i, j):
                row_i = set(rows[i])
                col_j = set(columns[j])

                root_row = np.sqrt(len(rows))
                size_row = int(root_row // 1)
                root_col = np.sqrt(len(rows))
                size_col = int(-1 * root_col // 1 * -1)
                prep_row = i/size_row
                row = int(prep_row // 1)
                prep_col = j/size_col
                col = int(prep_col // 1)

                section = set(np.array(sections[row*size_row:row*size_row+size_row,col*size_col:col*size_col+size_col]).reshape(-1,).tolist())

                print('\n', row_i, col_j, section)
                print('\n', type(row_i), type(col_j), type(section))
                total_set = row_i.union(col_j)
                total_set = total_set.union(section)
                # total_set = total_set.remove(0)
                print(total_set)

                return total_set

            for i in range(N):
                for j in range(N):
                    if len(not_possible(i,j)) == 8:
                        move_value = {1,2,3,4,5,6,7,8,9} - not_possible(i,j)
                        move = Move(i, j, move_value)
                        self.propose_move(move)
                        print('We got a single possibility! Proposed move:', move)


        # # If board is over x% filled, use Minimax:

        #     #Iterative Deepening
        # for d in range(1, game_state.board.squares.count(SudokuBoard.empty)+1):
        #     d_move, _ = minimax(game_state, True, d)
        #     self.propose_move(d_move)