#  (C) Copyright Wieger Wesselink 2021. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

import random
import time
from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove, print_board
import competitive_sudoku.sudokuai

# Extra packages:
import numpy as np
from copy import deepcopy

def compute_possible_moves(game_state):
    # Determine if a certain move is non-taboo in a certain gamestate
    def non_taboo(i, j, value):
        return game_state.board.get(i, j) == SudokuBoard.empty \
               and not Move(i, j, value) in game_state.taboo_moves

    # Create a list of the gamestate board's rows and a list of its columns (used in legal function)
    board_str = game_state.board.squares
    rows = []
    N = game_state.board.N
    for i in range(N):
        rows.append(board_str[i*N : (i+1)*N])
    columns = np.transpose(rows)

    def legal(i: int,j: int, value: int, data) -> None:
        """Return all the legal moves at a given game state.

            Parameters:
                    i (int): the row index
                    j (int): the column index
                    value (int): the value placed in the square

            Returns:
                    binary_sum (str): Binary string of the sum of a and b
        """
        root_row = np.sqrt(len(data))
        size_row = int(root_row // 1)
        root_col = np.sqrt(len(data))
        size_col = int(-1 * root_col // 1 * -1)  
        prep_row = i/size_row
        row = int(prep_row // 1)
        prep_col = j/size_col
        col = int(prep_col // 1)

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

    # Create copies of the current board's rows and columns, for use in the for loop below
    current_rows = deepcopy(rows)
    current_columns = deepcopy(columns)

    possible_moves_scores = []

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
        root_col = np.sqrt(len(current_rows))
        size_col = int(-1 * root_col // 1 * -1)
        prep_row = move.i/size_row
        row = int(prep_row // 1)
        prep_col = move.j/size_col
        col = int(prep_col // 1)
        y= np.vstack([xi for xi in current_rows])           
        current_section = np.array(y[row*size_row:row*size_row+size_row,col*size_col:col*size_col+size_col]).reshape(-1,).tolist()
                    
        if current_section.count(0) == 1:
            count += 1

        # Create a list containing tuples of moves and their score counts
        possible_moves_scores.append((move, count))
        
    return [possible_moves, possible_moves_scores]

class SudokuAI(competitive_sudoku.sudokuai.SudokuAI):
    """
    Sudoku AI that computes a move for a given sudoku configuration, based on minimax algo.
    """
    def __init__(self):
        super().__init__()

    ## This code below assigns a greedy move:

    # def compute_best_move(self, game_state: GameState) -> None:
    #     """
    #     ...
    #     """
    #     moves = compute_possible_moves(game_state)
    #     possible_moves = moves[0]
    #     possible_moves_scores = moves[1]

    #     # Select a random possible move
    #     self.propose_move(random.choice(possible_moves))

    #     # Select the move with the highest count, which results in the highest score
    #     best_count = 0
    #     for move in possible_moves_scores:
    #         count = move[1]
    #         if count > best_count:
    #             best_count = count
    #             self.propose_move(move[0])
            

    # def minimax(self, game_state: GameState, depth: int, maxPlayer: bool) -> None:
    #     """
    #     ...
    #     """
    #     possible_moves_scores = compute_possible_moves(game_state)

    #     # if depth == 0:
    #     #     print("Game Over")

    #     if maxPlayer:
    #         bestCount = 3
    #         proposed_move = None
    #         for move in possible_moves_scores:
    #             count = move[1]
    #             if count >= bestCount:
    #                 proposed_move = move
        
    #     else:
    #         bestCount = 3
    #         proposed_move = None
    #         for move in possible_moves_scores:
    #             count = move[1]
    #             if count <= bestCount:
    #                 proposed_move = move

        # return proposed_move

    def compute_best_move(self, game_state: GameState) -> None:
        """
        ...
        """
        current_game_state = deepcopy(game_state)
        possible_moves_scores = compute_possible_moves(current_game_state)
        possible_moves_scores = possible_moves_scores[1]

        # Select first possible move
        self.propose_move(possible_moves_scores[0][0])

        # if depth == 0:
        #     print("Game Over")

        best_count = 0
        d = 0
        for move in possible_moves_scores:
            print('\nPLAYER 1 MOVE:', move[0])
            # count = move[1]
            # if count > best_count:
            #     best_count = count
            #     proposed_move = move[0]
            
            new_game_state = deepcopy(current_game_state)
            new_game_state.board.put(move[0].i, move[0].j, move[0].value)

            # Compute possible moves for opponent based on new board
            opp_possible_moves_scores = compute_possible_moves(new_game_state)
            opp_possible_moves_scores = opp_possible_moves_scores[1]

            for x in opp_possible_moves_scores:
                print('Player 2 possible move:', f'({x[0].i},{x[0].j}) -> {x[0].value}')

            # opp_possible_moves_scores_min = []
            # for opp_move in opp_possible_moves_scores:
            #     if opp_move[1] == 0:
            #         opp_possible_moves_scores_min.append((opp_move[0], 3))
            #     elif opp_move[1] == 1:
            #         opp_possible_moves_scores_min.append((opp_move[0], 2))
            #     elif opp_move[1] == 2:
            #         opp_possible_moves_scores_min.append((opp_move[0], 1))
            #     elif opp_move[1] == 3:
            #         opp_possible_moves_scores_min.append((opp_move[0], 0))
            
            # print(opp_possible_moves_scores_min)
    