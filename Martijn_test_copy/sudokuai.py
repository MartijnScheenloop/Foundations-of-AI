#  (C) Copyright Wieger Wesselink 2021. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

import random
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

        # def emptyList(board):
        #     """
        #     Returns a list with all the empty squares
        #          @param board: the board with N**2 entries.
        #     """

        #     empty_list = []
        #     for a in range(N**2):
        #         i,j = SudokuBoard.f2rc(board, a)
        #         if board.get(i,j) == SudokuBoard.empty:
        #             empty_list.append([i,j])
        #     # print(empty_list)
        #     return empty_list           
        
        def extractPossibleMoves(game_state):
            """
            Returns the possible moves for a certain game state.
            @param state: the current game state in a SudokuBoard object
            """

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

            # Determine if action is legal (not already present in section, row or column)
            def legal(i: int,j: int, value: int, data):
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

            return possible_moves
             
        def countFunction(move, game_state):
            """
            Calculates a score for a given move and gamestate.
                @param move: an object with a position and value 
            """
            # Create a list of the gamestate board's rows and a list of its columns (used in legal function)
            board_str = game_state.board.squares
            rows = []
            N = game_state.board.N
            for i in range(N):
                rows.append(board_str[i*N : (i+1)*N])
            columns = np.transpose(rows)
            current_rows = deepcopy(rows)
            current_columns = deepcopy(columns)

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

            # Assign a score for the given count
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

        def evaluate(state):
            """Evaluates the best move for the given state.
            """
            best_score = 0
            best_move = random.choice(extractPossibleMoves(state))
            for move in extractPossibleMoves(state):
                score = countFunction(move, state)
                if score > best_score:
                    best_move = move
                    best_score = score
            return best_move, best_score

        def minimax(state, isMax, max_depth, curr_depth = 0, curr_score = 0):
            
            if len(extractPossibleMoves(state)) == 0:
                if isMax:
                    return None, float("-inf")
                return None, float("inf")

            if len(extractPossibleMoves(state)) == 1 or curr_depth == max_depth:
                move, value = evaluate(state)
                if isMax:
                    return move, value
                return move, -value

            scores = []

            possible_moves = extractPossibleMoves(state)

            if isMax:
                maxEval = float("-inf")
                x=0
                for move in possible_moves:
                    current_state = deepcopy(game_state)
                    x += 1
                    score = countFunction(move, current_state)
                    print('Max', move, 'Gets a score of:', score, '  |   Iteration:', x)
                    total_score = curr_score + score
                    current_state.board.put(move.i, move.j, move.value)

                    next_move, next_value = minimax(current_state, not isMax, max_depth, curr_depth + 1, total_score)
                    total_score = total_score + next_value
                    print('Min', next_move, 'Gets a score of:', next_value, '  |   Iteration:', x)
                    scores.append((move, total_score))
                    # state.board.put(move.i, move.j, SudokuBoard.empty)

                print(scores)
                move, value = max(scores, key=lambda score:score[1])
                return move, value + curr_score

            else: 
                maxEval = float("inf")
                for move in possible_moves:
                    current_state = deepcopy(game_state)
                    score = countFunction(move, current_state)
                    print(move, '(min) Gets a score of:', score)
                    total_score = curr_score - score
                    current_state.board.put(move.i, move.j, move.value)

                    final_move, final_value = minimax(current_state, isMax, max_depth, curr_depth + 1, total_score)
                    
                    scores.append((move, final_value))
                    state.board.put(move.i, move.j, SudokuBoard.empty)

                move, value = min(scores, key=lambda score: score[1])
                return move
                # , (value + curr_score)

                



        # def minimax(state, isMax, max_depth, curr_depth = 0, curr_score = 0):
        #     """Creates a tree with a given depth and returns a move.
        #         @param isMax: boolean value that is True if it is the maximizing player
        #         @param max_depth: the maximum depth of the tree
        #         @param curr_depth: the current depth
        #         @param curr_score: the count of the parent node
        #     """ 

        #     if len(extractPossibleMoves(state)) == 0:
        #         if isMax:
        #             return None, float("-inf")
        #         return None, float("inf")

        #     if len(extractPossibleMoves(state)) == 1 or curr_depth == max_depth:
        #         move, value = evaluate(state)
        #         if isMax:
        #             return move, value
        #         return move, -value

        #     scores = []
        #     for move in extractPossibleMoves(state):
        #         score = countFunction(move, state)
        #         if isMax:
        #             total_score = curr_score + score
        #         else: 
        #             total_score = curr_score - score
        #         state.board.put(move.i, move.j, move.value)


        #         final_move, final_value = minimax(state, not isMax, max_depth, curr_depth + 1, total_score)
        #         scores.append((move, final_value))
        #         state.board.put(move.i, move.j, SudokuBoard.empty)

        #     [print((str(i[0]))+ " scores a value of " + str(i[1])) for i in scores]

        #     if isMax:
        #         move, value = max(scores, key=lambda score:score[1])

        #         print(" Optimal move for depth " + str(curr_depth+1) + " is " + str(move) + " with a total reward of " + str(value))

        #         return move, (value + curr_score)
        #     move, value = min(scores, key=lambda score: score[1])

        #     print("Optimal move for depth " + str(curr_depth+1) + " is " + str(move) + " with a total reward of " + str(value))

        #     return move, (value + curr_score)

        self.propose_move(extractPossibleMoves(game_state)[0])

        _, move_depth_2 = minimax(game_state, True, 2)
        self.propose_move(move_depth_2)
        # #Iterative Deepening
        # for d in range(1, game_state.board.squares.count(SudokuBoard.empty)+1):
        #     d_move, _ = minimax(game_state, True, d)
        #     self.propose_move(d_move)

