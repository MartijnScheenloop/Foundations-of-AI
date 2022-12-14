#  (C) Copyright Wieger Wesselink 2021. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

import random
# import time
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

        # HEURISTIC 1; move based one fraction board filled

        # Quantify stage of the game and based on that pick a move selection tactic

        N = game_state.board.N

        def possible(i, j, value):
            return game_state.board.get(i, j) == SudokuBoard.empty \
                and not TabooMove(i, j, value) in game_state.taboo_moves

        all_moves = [Move(i, j, value) for i in range(N) for j in range(N)
                    for value in range(1, N+1) if possible(i, j, value)]
        move = all_moves[0]
        self.propose_move(move)

        N_empty_squares = game_state.board.squares.count(0)
        N_total_squares = N*N
        fraction_filled = 1 - N_empty_squares/N_total_squares
        print('Filled:', fraction_filled, '\n')


        ##############################

        # Determine if a certain move is non-taboo in a certain gamestate
        def non_taboo(i, j, value):
            return game_state.board.get(i, j) == SudokuBoard.empty \
                and not Move(i, j, value) in game_state.taboo_moves

        def legal(i,j,value,rows):
            root_row = np.sqrt(len(rows))
            size_row = int(root_row // 1)
            root_col = np.sqrt(len(rows))
            size_col = int(-1 * root_col // 1 * -1)
            prep_row = move.i/size_row
            prep_col = move.j/size_col
            row = int(prep_row // 1)
            col = int(prep_col // 1)
            y= np.vstack([xi for xi in rows])
            return not value in np.array(y[row*size_row:row*size_row+size_row,col*size_col \
                :col*size_col+size_col]).reshape(-1,).tolist() and not value in rows[i] and not value in columns[j]

        def scoreFunction(move, game_state):
            """Calculates a score for a given move.
            """
            # Make copies of the board's rows, columns and sections
            columns = np.transpose(rows)
            current_rows = deepcopy(rows)
            current_columns = deepcopy(columns)

            # Check if current rows and columns are already completed
            current_row_complete = not 0 in current_rows[move.i]
            current_column_complete = not 0 in current_columns[move.j]

            # Fill in the move and define the new rows and columns
            new_rows = deepcopy(current_rows)
            new_rows[move.i][move.j] = move.value
            new_columns = np.transpose(new_rows)

            # Check if the new rows and columns are completed
            new_row_complete = not 0 in new_rows[move.i]
            new_column_complete = not 0 in new_columns[move.j]

            # Check if a row and/or column has been completed by the current move
            count = 0
            if new_row_complete and not current_row_complete:
                count += 1
            if new_column_complete and not current_column_complete: 
                count += 1

            # Define the move's sections
            root_row = np.sqrt(len(current_rows))
            root_col = np.sqrt(len(current_rows))
            size_row = int(root_row // 1)
            size_col = int(-1 * root_col // 1 * -1)
            prep_row = move.i/size_row
            prep_col = move.j/size_col
            row = int(prep_row // 1)
            col = int(prep_col // 1)
            y= np.vstack([xi for xi in current_rows])           
            current_section = np.array(y[row*size_row:row*size_row+size_row,col*size_col:col*size_col+size_col]).reshape(-1,).tolist()
                
            # Check if the move completes a section
            if current_section.count(0) == 1:
                count += 1
                
            # Appoint a score to the move and return an integer
            score = 0
            if count == 0:
                score = 0
            elif count == 1:
                score = 1
            elif count == 2:
                score = 3
            elif count == 3:
                score = 7

            return int(score)

        def not_possible(i, j):
            """For a given square check what numbers can not be filled in.
            """
            # Define the row and column of the square
            row_i = set(rows[i])
            col_j = set(columns[j])

            # Define the section of the square
            root_row = np.sqrt(len(rows))
            size_row = int(root_row // 1)
            root_col = np.sqrt(len(rows))
            size_col = int(-1 * root_col // 1 * -1)
            prep_row = i/size_row
            row = int(prep_row // 1)
            prep_col = j/size_col
            col = int(prep_col // 1)

            section = set(np.array(sections[row*size_row:row*size_row+size_row,col*size_col:col*size_col+size_col]).reshape(-1,).tolist())

            # Define the total set of numbers that are not possible and return it
            total_set = row_i.union(col_j)
            total_set = total_set.union(section)
            total_set.remove(0)

            return total_set

        def compute_possible_moves(game_state):
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
                print(possible_moves_scores.append(scoreFunction(move, game_state)))
                possible_moves_scores.append(scoreFunction(move, game_state))

            return [possible_moves, possible_moves_scores]

        
        board_str = game_state.board.squares
        rows = []
        N = game_state.board.N
        for i in range(N):
            rows.append(board_str[i*N : (i+1)*N])
        columns = np.transpose(rows)
            
        #1 If board is relatively empty, pick a random possible move:
        if fraction_filled >=0 and fraction_filled <0.2:
            possible_moves = []
            for i in range(N):
                for j in range(N):
                    for value in range(1, N+1):
                        if non_taboo(i, j, value):
                            if legal(i, j, value, rows):
                                possible_moves.append(Move(i, j, value))
            self.propose_move(possible_moves[0])

        #2 If board is partly filled but far from totally filled, use best Last Possible Number move:
        if fraction_filled >=0.2 and fraction_filled <0.4:
            print('LAST POSSIBLE NUMBER HEURISTIC\n')
            # Define the rows, columns and sections of the current board
            board = game_state.board
            board_str = board.squares

            rows = []
            N = game_state.board.N
            # print('N=', N)
            for i in range(N):
                rows.append(board_str[i*N : (i+1)*N])
            columns = list(np.transpose(rows))

            sections = np.vstack([xi for xi in rows])

            single_possibility_moves = []
            for i in range(N):
                for j in range(N):
                    if game_state.board.get(i, j) == SudokuBoard.empty:
                        if len(not_possible(i,j)) == N-1:
                            set_possible_values = set()
                            for number in range(1,N+1):
                                set_possible_values.add(number)
                            move_value = set_possible_values - not_possible(i,j)
                            move_value = list(move_value)[0]
                            print('Coordinates:', f'({i},{j})')
                            print('Not possible values:', not_possible(i,j))
                            print('Remaining value:', move_value)
                            move = Move(i, j, move_value)
                            score = scoreFunction(move, game_state)
                            print(move, 'Score', score,'\n')
                            single_possibility_moves.append((move, score))
                            # print('We got a single possibility! Proposed move:', move)
            
        # Propose the single possibility move that gets the highest reward
            max_score = 0
            best_move = Move(0, 0, 0)
            for move in single_possibility_moves:
                if move[1] >= max_score:
                    max_score = move[1]
                    best_move = move[0]

            if best_move.value == 0:
                print('No single possibility! Picking first possible move')
                for i in range(N):
                    for j in range(N):
                        for value in range(1, N+1):
                            if non_taboo(i, j, value):
                                if legal(i, j, value, rows):
                                    move = Move(i, j, value)
                                    self.propose_move(move)
            else:
                self.propose_move(best_move)
        
        if fraction_filled >= 0.4:
            print('MINIMAX DEPTH=2\n')
            current_game_state = deepcopy(game_state)
            possible_moves_scores = compute_possible_moves(current_game_state)
            possible_moves_scores = possible_moves_scores[1]

            # Select first possible move
            self.propose_move(possible_moves_scores[0][0])

            # if depth == 0:
            #     print("Game Over")

            best_count = 0
            d = 0
            possible_moves_new_scores = []
            for move in possible_moves_scores:
                print('\nPLAYER 1 MOVE:', move[0], 'Score:', move[1])
                # count = move[1]
                # if count > best_count:
                #     best_count = count
                #     proposed_move = move[0]
                
                new_game_state = deepcopy(current_game_state)
                new_game_state.board.put(move[0].i, move[0].j, move[0].value)

                # Compute possible moves for opponent based on new board
                opp_possible_moves_scores = compute_possible_moves(new_game_state)
                opp_possible_moves_scores = opp_possible_moves_scores[1]

                max_opp_score = 0
                for opp_move in opp_possible_moves_scores:
                    print('Player 2 possible move:', f'({opp_move[0].i},{opp_move[0].j}) -> {opp_move[0].value}', 'Score:', opp_move[1])
                    if opp_move[1] > max_opp_score:
                        max_opp_score = opp_move[1]
                
                move = list(move)
                move[1] = move[1] - max_opp_score
                possible_moves_new_scores.append(tuple(move))
                print('New score:', move[1])
            
            # print(f'\n{possible_moves_new_scores}')

            # Select the move with the highest score difference
            best_score = -math.inf
            for move in possible_moves_new_scores:
                score = move[1]
                if score > best_score:
                    best_score = score
                    self.propose_move(move[0])
            print('\nBest new score:', best_score)