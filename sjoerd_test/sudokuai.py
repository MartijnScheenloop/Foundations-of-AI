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
        N = game_state.board.N

        def emptyList(board):
            """
            Returns a list with all the empty squares
                @param board: the board with N**2 entries.
            """

            empty_list = []
            for a in range(N**2):
                i,j = SudokuBoard.f2rc(board, a)
                if board.get(i,j) == SudokuBoard.empty:
                    empty_list.append([i,j])
            return empty_list           
        
        def isNonTaboo(i: int, j: int, value: int):
            """
            Checks for all moves if it is non-taboo.
                @param i: the index for the row
                @param j: the index for the column
                @param value: the value of the square
            """
            return not Move(i, j, value) in game_state.taboo_moves
        
        def extractPossibleMoves(state):
            """
            Returns the possible moves for a certain game state.
                @param state: the current game state in a SudokuBoard object
            """

            #Extract the rows, columns and regions
            board_string = state.board.squares
            rows = []
            for i in range(N):
                rows.append(board_string[i*N : (i+1)*N]) 
            columns = np.transpose(rows)

            def possibleMoves(i: int, j: int, value):
                """
                Checks for a given move if it is correct in the row, column and region.
                """

                #Determining the sizes of the regions 
                root_row_region = np.sqrt(len(rows))
                size_row_region = int(root_row_region // 1)

                root_col_region = np.sqrt(len(rows))
                size_col_region = int(-1 * root_col_region // 1 * -1)  
                
                prep_row_region = i/size_row_region
                row_region = int(prep_row_region // 1)
                prep_col_region = j/size_col_region
                col_region = int(prep_col_region // 1)
                y = np.vstack([xi for xi in rows])
                region = np.array(y[row_region*size_row_region:row_region*size_row_region+size_row_region,\
                    col_region*size_col_region:col_region*size_col_region+size_col_region]).reshape(-1,).tolist()
                
                #Checking for row, column and region
                row_check = not value in rows[i]
                column_check = not value in columns[j]
                region_check = not value in region

                return isNonTaboo(i, j, value) and row_check and column_check and region_check
        
            # new_list = []
            # for square in emptyList(state.board):
            #     for value in range(1,N+1):
            #         if possibleMoves(square[0], square[1], value):
            #             new_list.append(Move(square[0],square[1], value))
            #             return new_list

            return [Move(a[0], a[1], value) for a in emptyList(state.board) for value \
                in range(1, N+1) if possibleMoves(a[0], a[1], value)]
            
            
        def countFunction(move, state):
            """
            Calculates a score for each possible move.
                @param move: an object with a position and value 
            """
            
            def colFill(i,j):
                """Checks if the column is completed.
                """
                for a in range(N):
                    if state.board.get(a, j) == SudokuBoard.empty and a!=i:
                        return False
                return True
            
            def rowFill(i,j):
                """Checks if the row is completed.
                """

                for b in range(N):
                    if state.board.get(i, b) == SudokuBoard.empty and b!=j:
                        return False
                return True
            
            def regionFill(i,j):
                """Checks if the region is completed.
                """
                x = i - (i % state.board.m)
                y = j - (j % state.board.n)

                for a in range(state.board.m):
                    for b in range(state.board.n):
                        if state.board.get(x+a, y+b) == SudokuBoard.empty and \
                            (x+a !=i or y+b !=j):
                            return False
                return True

            partsFilled = colFill(move.i, move.j) + rowFill(move.i, move.j) + regionFill(move.i, move.j)
            
            if partsFilled == 0:
                return 0
            if partsFilled == 1:
                return 1
            if partsFilled == 2:
                return 3
            if partsFilled == 3:
                return 7

        def evaluate(state):
            """Evaluates the best move for the given state.
            """

            best_value = 0
            best_move = random.choice(extractPossibleMoves(state))
            for move in extractPossibleMoves(state):
                value = countFunction(move, state)
                if value > best_value:
                    best_move = move
                    best_value = value
            return best_move, best_value

        def minimax(state, isMax, max_depth, curr_depth = 0, curr_score = 0):
            """Creates a tree with a given depth and returns a move.
                @param isMax: boolean value that is True if it is the maximizing player
                @param max_depth: the maximum depth of the tree
                @param curr_depth: the current depth
                @param curr_score: the count of the parent node
            """ 

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
            for move in extractPossibleMoves(state):
                score = countFunction(move, state)
                if isMax:
                    total_score = curr_score + score
                else: 
                    total_score = curr_score - score
                state.board.put(move.i, move.j, move.value)
                final_move, final_value = minimax(state, not isMax, max_depth, curr_depth + 1, total_score)
                scores.append((move, final_value))
                state.board.put(move.i, move.j, SudokuBoard.empty)

            if isMax:
                move, value = max(scores, key=lambda score:score[1])
                return move, (value + curr_score)
            move, value = min(scores, key=lambda score: score[1])
            return move, (value + curr_score)

        self.propose_move(extractPossibleMoves(game_state)[0])

        #Iterative Deepening
        for d in range(1, game_state.board.squares.count(SudokuBoard.empty)+1):
            d_move, _ = minimax(game_state, True, d)
            self.propose_move(d_move)