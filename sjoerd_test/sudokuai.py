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
               
        def getMoves(state):
            """
            Returns the possible moves for a certain game state.
            @param state: the current game state in a SudokuBoard object
            """

            def possible(i,j,value):

                def checkColumn(i,j,value):
                    """Checks if the region is completed.
                    """
                    for element_col in range(N):
                        if state.board.get(element_col, j) == value:
                            return False
                    return True

                def checkRow(i,j,value):
                    """Checks if the row is completed.
                    """
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
        
        for move in getMoves(game_state):
            print("possible moves: ", move)
            
            
        def scoreFunction(move, state):
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
                return int(0)
            if partsFilled == 1:
                return int(1)
            if partsFilled == 2:
                return int(3)
            if partsFilled == 3:
                return int(7)
    
        # for move in extractPossibleMoves(game_state):
        #     print("output count function: ", move, "reward ", countFunction(move, game_state))

        # def evaluate(state):
        #     """Evaluates the score for the given state.
        #     """
            
        #     for move in getMoves(state):
        #         score = scoreFunction(move, state)
        #     return move, score

        def getChildren(state):

            for move in getMoves(state):
                listed = [state, scoreFunction(move, state), move]
                return listed

        print(getChildren(game_state))
            # best_value = 0
            # best_move = random.choice(extractPossibleMoves(state))
            # for move in extractPossibleMoves(state):
            #     value = countFunction(move, state)
            #     if value > best_value:
            #         best_move = move
            #         best_value = value
            # return best_move, best_value
        
        # optimal_move = evaluate(game_state)[0]
        # self.propose_move(optimal_move)

        # def minimax(state, depth: int, isMaximisingPlayer: bool) -> int:
        #     """Creates a tree with a given depth and returns a move.
        #         @param isMax: boolean value that is True if it is the maximizing player
        #         @param max_depth: the maximum depth of the tree
        #         @param curr_depth: the current depth
        #         @param curr_score: the count of the parent node
        #     """ 

        #     if len(getMoves(state)) == 0 or depth == 0:
        #         return evaluate(state)

        #     children = getChildren(state)
        #     if isMaximisingPlayer:
        #         maxEval = float("-inf")
        #         for child in children:
        #             new_state = deepcopy(state)
        #             new_state_put = new_state.put(child)
        #             score = scoreFunction(child, state)
        #             maxEval = max(maxEval, minimax(new_state_put, depth-1, False))
        #         return the_move, maxEval
            
        #     else:
        #         minEval = float("inf")
        #         for child in children:
        #             new_state = deepcopy(state)
        #             new_state_put = new_state.put(child)
        #             minEval = min(minEval, minimax(new_state_put, depth-1, True))
        #         return the_move, minEval


        # for d in range(1, game_state.board.squares.count(SudokuBoard.empty)+1):
        #     d_move, _ = minimax(game_state, d, True)
        #     self.propose_move(d_move)

        #     if len(extractPossibleMoves(state)) == 1 or curr_depth == max_depth:
        #         move, value = evaluate(state)
        #         if isMaxiPlayer:
        #             return move, value
        #         return move, -value

        #     scores = []
        #     for move in extractPossibleMoves(state):
        #         score = countFunction(move, state)
        #         if isMaxiPlayer:
        #             total_score = curr_score + score
        #         else: 
        #             total_score = curr_score - score
        #         state.board.put(move.i, move.j, move.value)
        #         _, final_value = minimax(state, False, max_depth, curr_depth + 1, total_score)
        #         scores.append((move, final_value))
        #         state.board.put(move.i, move.j, SudokuBoard.empty)

        #     if isMaxiPlayer:
        #         move, value = max(scores, key=lambda score:score[1])
        #         return move, (value + curr_score)
        #     move, value = min(scores, key=lambda score: score[1])
        #     return move, (value + curr_score)

        # for d in range(1, game_state.board.squares.count(SudokuBoard.empty)+1):
        #     d_move, _ = minimax(game_state, True, d)
        #     self.propose_move(d_move)

            
         # Move for the final depth
            # if len(extractPossibleMoves(state)) == 1 or current_depth == max_depth:
            #     eval_move, eval_value = evaluate(state)
            #     if isMaxiPlayer:
            #         return eval_move, eval_value
            #     return eval_move, -eval_value    

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

        #     if isMax:
        #         move, value = max(scores, key=lambda score:score[1])
        #         return move, (value + curr_score)
        #     move, value = min(scores, key=lambda score: score[1])
        #     return move, (value + curr_score)

        # self.propose_move(extractPossibleMoves(game_state)[0])

        # Move if there are no possible moves
            # if len(extractPossibleMoves(state)) == 0 or depth == 0:
            #     return None, score
            
            # if isMaxiPlayer:
            #     maxEval = float('-inf')
            #     for moves in extractPossibleMoves(state):
            #         score += countFunction(moves, state)
            #         _, eval = minimax(state, depth+1, False, score, alpha, beta)
            #         if maxEval < eval:
            #             maxEval = eval
            #             new_move_max = moves 
            #         alpha = max(alpha, eval)
            #         if beta <= alpha:
            #             break
            #         score -= countFunction(moves, state)
            #     return new_move_max, maxEval
            
            # else:
            #     minEval = float('inf')
            #     for moves in extractPossibleMoves(state):
            #         score += countFunction(moves, state)
            #         _, eval = minimax(state, depth+1, True, score, alpha, beta)
            #         if minEval > eval:
            #             minEval = eval
            #             new_move_min = moves 
            #         minEval = min(minEval, eval)
            #         if beta <= alpha:
            #             break
            #         score -= countFunction(moves, state)
            #     return new_move_min
