#  (C) Copyright Wieger Wesselink 2021. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)
#  python simulate_game.py --first=team38_A3 --second=greedy_player --board=boards/easy-2x2.txt --time=1.0
#  python simulate_game.py --first=greedy_player --second=team38_A3 --board=boards/empty-2x2.txt --time=5.0
#  python simulate_game.py --first=greedy_player --second=team38_A3 --board=boards/random-3x3.txt --time=5.0

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
            """Returns a list with all the empty squares
            @param board: the board with N**2 entries.
            """

            board = game_state.board
            empty_list = []
            for a in range(N**2):
                i,j = SudokuBoard.f2rc(board, a)
                if board.get(i,j) == SudokuBoard.empty:
                    empty_list.append([i,j])
            return empty_list    
               
        def extractPossibleMoves(game_state: GameState):
            """Returns the possible moves for a certain game state.
            @param game_state: the current game state 
            """

            def possible(i,j,value):
                """Checks the move for the columns, rows and regions.
                @param i: the row index
                @param j: the column index
                @param value: the value of the move
                """
                
                def checkColumn(i, j,value):
                    """Checks if the column already contains the value.
                    @param i: the row index
                    @param j: the column index
                    @param value: the value of the move
                    """
                    for element_col in range(N):
                        if game_state.board.get(element_col, j) == value:
                            return False
                    return True

                def checkRow(i, j, value):
                    """Checks if the row already contains the value.
                    @param i: the row index
                    @param j: the column index
                    @param value: the value of the move
                    """
                    for element_row in range(N):
                        if game_state.board.get(i, element_row) == value:
                            return False
                    return True
            
                def checkRegion(i,j,value):
                    """Checks if the region already contains the value.
                    @param i: the row index
                    @param j: the column index
                    @param value: the value of the move
                    """
                    x = i - (i % game_state.board.m)
                    y = j - (j % game_state.board.n)

                    for element_col in range(game_state.board.m):
                        for element_row in range(game_state.board.n):
                            if game_state.board.get(x+element_col, y+element_row) == value:
                                return False
                    return True

                return not TabooMove(i,j,value) in game_state.taboo_moves \
                        and checkColumn(i,j,value) and checkRow(i,j,value) and checkRegion(i,j,value)


            return [Move(a[0], a[1], value) for a in emptyList(game_state) for value in range(1, N+1) if possible(a[0], a[1], value)]         

        def countFunction(move, state):
            """
            Calculates a score for each possible move.
                @param move: an object with a position and value 
            """
            
            def colFill(i,j):
                """Checks if the column is completed.
                """
                for element_col in range(N):
                    if state.board.get(element_col, j) == SudokuBoard.empty and element_col!=i:
                        return False
                return True
            
            def rowFill(i,j):
                """Checks if the row is completed.
                """
                for element_row in range(N):
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
            elif partsFilled == 1:
                return int(1)
            elif partsFilled == 2:
                return int(3)
            elif partsFilled == 3:
                return int(7)

        def getChildren(state, isMaximisingPlayer):
            """Returns for each move the new board, score and the move itself.
            @param state: 
            """
            pairs = []
            for move in extractPossibleMoves(state):
                child_board = deepcopy(state)
                child_board.board.put(move.i, move.j, move.value)

                if isMaximisingPlayer:
                    new_score = countFunction(move, state)
                else:
                    new_score = countFunction(move, state) *(-1)

                list = [child_board, new_score, move]
                pairs.append(list)
            return pairs
        
        def minimax(game_state, depth: int, isMaximisingPlayer: bool, score: int, alpha: float, beta: float):
            """Creates a tree with a given depth and returns a move.
                @param state: the current state of the sudoku
                @param depth: an integer indicating the depth of the tree
                @param isMaximisingPlayer: a boolean that returns True if it is the maximising player
                @param score: an integer that is used to continiously calculate the score
                @param alpha: a float used for inplementing A-B Pruning
                @param beta: a float used for inplementing A-B Pruning
            """ 
            if len(extractPossibleMoves(game_state)) == 0 or depth == 0:
                return score, None

            children = getChildren(game_state, isMaximisingPlayer)
            if isMaximisingPlayer:
                maxEval = float('-inf')
                for pairs in children:
                    score += pairs[1]
                    eval, _ = minimax(pairs[0], depth-1, False, score, alpha, beta)
                    if maxEval < eval:
                        maxEval = eval
                        end_move = pairs[2]
                    alpha = max(alpha, eval)
                    if beta <= alpha:
                         break
                    score -= pairs[1]
                print("maxEval: ", maxEval, "end_move: ", end_move, "depth: ", depth)
                return maxEval, end_move
            
            else:
                minEval = float('inf')
                for pairs in children:
                    score += pairs[1]
                    eval, _ = minimax(pairs[0], depth-1, True, score, alpha, beta)
                    if minEval > eval:
                        minEval = eval
                        end_move = pairs[2]
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break
                    score -= pairs[1]
                print("minEval: ", minEval, "end_move: ", end_move, "depth: ", depth)
                return minEval, end_move

        #initially proposing random move 
        self.propose_move(random.choice(extractPossibleMoves(game_state)))
            
        for d in range(1, game_state.board.squares.count(SudokuBoard.empty)+1):
            _, do_move = minimax(game_state, d, True, 0, float('-inf'), float('inf'))
            self.propose_move(do_move)