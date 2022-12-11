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
        print(N)

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
        
        def extractPossibleMoves(state):
            """
            Returns the possible moves for a certain game state.
            @param state: the current game state in a SudokuBoard object
            """

            def possible(i,j,value):

                def checkColumn(i,j,value):
                    for element_col in range(N):
                        if state.board.get(element_col, j) == value:
                            return False
                    return True

                

                def checkRow(i,j,value):
                    for element_row in range(N):
                        if state.board.get(i, element_row) == value:
                            return False
                    return True
            
                def checkRegion(i,j,value):
                    """Checks if the region is completed.
                    """
                    x = i - (i % state.board.m)
                    y = j - (j % state.board.n)

                    for element_col in range(state.board.m):
                        for element_row in range(state.board.n):
                            if state.board.get(x+element_col, y+element_row) == value:
                                return False
                    return True

                return not TabooMove(i,j,value) in state.taboo_moves \
                        and checkColumn(i,j,value) and checkRow(i,j,value) and checkRegion(i,j,value)


            return [Move(a[0], a[1], value) for a in emptyList(state.board) for value in range(1, N+1) if possible(a[0], a[1], value)]
             
        def countFunction(move, state):
            """
            Calculates a score for each possible move.
                @param move: an object with a position and value 
            """
            
            def colFill(i,j):
                """Checks if the column is completed.
                """
                for element_col in range(state.board.m):
                    if state.board.get(element_col, j) == SudokuBoard.empty and element_col!=i:
                        return False
                return True
            
            def rowFill(i,j):
                """Checks if the row is completed.
                """
                for element_row in range(state.board.n):
                    if state.board.get(i, element_row) == SudokuBoard.empty and element_row!=j:
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

            if isMax:
                maxEval = float("-inf")
                for move in extractPossibleMoves(state):
                    score = countFunction(move, state)
                    total_score = curr_score + score
                    state.board.put(move.i, move.j, move.value)

                    final_move, final_value = minimax(state, not isMax, max_depth, curr_depth + 1, total_score)
                    scores.append((move, final_value))
                    state.board.put(move.i, move.j, SudokuBoard.empty)

                [print((str(i[0]))+ " scores a value of " + str(i[1])) for i in scores]
                move, value = max(scores, key=lambda score:score[1])
                print(" Optimal move for depth " + str(curr_depth+1) + " is " + str(move) + " with a total reward of " + str(value))
                return move, (value + curr_score)

            else: 
                maxEval = float("inf")
                for move in extractPossibleMoves(state):
                    score = countFunction(move, state)
                    total_score = curr_score - score
                    state.board.put(move.i, move.j, move.value)

                    final_move, final_value = minimax(state, isMax, max_depth, curr_depth + 1, total_score)
                    
                    scores.append((move, final_value))
                    state.board.put(move.i, move.j, SudokuBoard.empty)

                [print((str(i[0]))+ " scores a value of " + str(i[1])) for i in scores]
                move, value = min(scores, key=lambda score: score[1])
                print("Optimal move for depth " + str(curr_depth+1) + " is " + str(move) + " with a total reward of " + str(value))
                return move, (value + curr_score)

                



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

        #Iterative Deepening
        for d in range(1, game_state.board.squares.count(SudokuBoard.empty)+1):
            d_move, _ = minimax(game_state, True, d)
            self.propose_move(d_move)

