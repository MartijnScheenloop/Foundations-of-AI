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
            size_row = math.floor(np.sqrt(len(data)))
            size_col = math.ceil(np.sqrt(len(data)))
            row = math.floor(i/size_row)
            col = math.floor(j/size_col)
            y= np.vstack([xi for xi in data])
            return not value in np.array(y[row*size_row:row*size_row+size_row,col*size_col:col*size_col+size_col]).reshape(-1,).tolist() and not value in rows[i] and not value in columns[j]
   
        non_taboo_moves = []
        possible_moves = []

        for i in range(N):
            for j in range(N):
                for value in range(1, N+1):
                    if non_taboo(i, j, value):
                        non_taboo_moves.append(Move(i, j, value))
                        if legal(i, j, value, rows):
                            possible_moves.append(Move(i, j, value))
        
        # #Getting the output 
        # current_board = game_state.board
        # x = print(current_board)

        # for i in range(N):
        #     for j in range(N):
        #         for value in range(1, N+1):
        #             if non_taboo(i, j, value):
        #                 non_taboo_moves.append(Move(i, j, value))
        #                 if legal(i, j, value, rows):

        #                     # game_state.board.put(i,j,value)
        #                     # current_row = rows

        #                     # new_state = game_state.board.squares
        #                     # new_rows = []
        #                     # for i in range(N):
        #                     #     new_rows.append(new_state[i*N : (i+1)*N])
        #                     # print(current_row, new_rows)

        #                     # new_row_empty = 0 in new_rows[i]
        #                     # print(new_row_empty)

        # print('NON-TABOO MOVES:')
        # for move in non_taboo_moves:
        #     print(move)        
        # print('TABOO MOVES:')
        # for move in game_state.taboo_moves:
        #     print(move)
        print('POSSIBLE MOVES (LEGAL AND NON-TABOO): \n')

        # current_board = game_state.board.squares
        # current_rows = []
        # for i in range(N):
        #     current_rows.append(current_board[i*N : (i+1)*N])
        # print('Current rows:', rows)
        # print('Current columns:', columns)
        # print(current_rows)
        # print(current_columns)
        current_rows = deepcopy(rows)
        current_columns = deepcopy(columns)
        best_move = Move(0, 0, 0)
        best_count = 0

        for move in possible_moves:
            # print("Current row:   ", current_rows[move.i])
            # print("Current column:", current_columns[move.j])
            current_row_complete = not 0 in current_rows[move.i]
            current_column_complete = not 0 in current_columns[move.j]

            print('The move is:', move)
            new_rows = deepcopy(current_rows)
            new_rows[move.i][move.j] = move.value
            new_columns = np.transpose(new_rows)

            # print("New row:       ", new_rows[move.i])
            # print("New column:    ", new_columns[move.j])
            new_row_complete = not 0 in new_rows[move.i]
            new_column_complete = not 0 in new_columns[move.j]
            
            count = 0
            if new_row_complete and not current_row_complete:
                count += 1
            if new_column_complete and not current_column_complete: 
                count += 1
            # if section_complete:
            #     count +=1
            # print('Final count is:', count, '\n')
            # print('Current row complete:   ', current_row_complete)
            # print('Current column complete:', current_column_complete)
            # print('New row complete:       ', new_row_complete)
            # print('New column complete:    ', new_column_complete, '\n')
            # print('Count:', count)

            size_row = math.floor(np.sqrt(len(current_rows)))
            size_col = math.ceil(np.sqrt(len(current_rows)))
            row = math.floor(move.i/size_row)
            col = math.floor(move.j/size_col) 
            y= np.vstack([xi for xi in current_rows])           
            current_section = np.array(y[row*size_row:row*size_row+size_row,col*size_col:col*size_col+size_col]).reshape(-1,).tolist()
            # print('Current section list:', current_section)
                    
            if current_section.count(0) == 1:
                count += 1
            
            print('Count =', count)

            if count > best_count:
                best_count = count
                self.propose_move(move)

        # print('CURRENT SCORE')
        # for move in game_state.scores:
        #     print(move)
        # print('historic moves')
        # for move in game_state.moves:
        #     print(move)

        # move = random.choice(possible_moves)
        # self.propose_move(move)

        # # Randomly repick the move from the list every 0.2 seconds until the time runs out
        # while True:
        #     time.sleep(0.2)
        #     self.propose_move(random.choice(possible_moves))
