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

            board = game_state.board
            empty_list = []
            for a in range(N**2):
                i,j = SudokuBoard.f2rc(board, a)
                if board.get(i,j) == SudokuBoard.empty:
                    empty_list.append([i,j])
            return empty_list  

        print(emptyList(game_state.board))         
               
        def extractPossibleMoves(game_state: GameState):
            """
            Returns the possible moves for a certain game state.
            @param state: the current game state in a SudokuBoard object
            """

            def possible(i,j,value):

                def checkColumn(i,j,value):
                    """Checks if the region is completed.
                    """
                    for element_col in range(N):
                        if game_state.board.get(element_col, j) == value:
                            return False
                    return True

                def checkRow(i,j,value):
                    """Checks if the row is completed.
                    """
                    for element_row in range(N):
                        if game_state.board.get(i, element_row) == value:
                            return False
                    return True
            
                def checkRegion(i,j,value):
                    """Checks if the region is completed.
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
            
        for move in extractPossibleMoves(game_state):
            print(move)

        def scoreFunction(move, game_state):
            """
            Calculates a score for each possible move.
                @param move: an object with a position and value 
            """

            board_str = game_state.board.squares
            rows = []
            N = game_state.board.N
            for i in range(N):
                rows.append(board_str[i*N : (i+1)*N])
            columns = np.transpose(rows)
            current_rows = deepcopy(rows)
            current_columns = deepcopy(columns)

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
    
        for move in extractPossibleMoves(game_state):
            print("output count function: ", move, "reward ", scoreFunction(move, game_state))

        # self.propose_move(random.choice(extractPossibleMoves(game_state)))

        def getChildren(game_state):
            """Returns for each move the new board, score and the move itself.
                @param state: 
                """

            pairs = []
            for move in extractPossibleMoves(game_state):
                child_board = deepcopy(game_state.board)
                child_board.put(move.i, move.j, move.value)
                new_score = scoreFunction(move, game_state)
                list = child_board, new_score, move
                pairs.append(list)
            return pairs
        
        print(getChildren(game_state))
        
        def minimax(game_state, depth: int, isMaximisingPlayer: bool, score: int, alpha: float, beta: float):
            """Creates a tree with a given depth and returns a move.
                @param state: the current state of the sudoku
                @param depth: the depth of the tree
                @param isMaximisingPlayer: a boolean that returns True if it is the maximising player
            """ 
            if len(extractPossibleMoves(game_state)) == 0 or depth == 0:
                return score, None

            children = getChildren(game_state)
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
                # print("maxEval: ", maxEval, "end_move: ", end_move)
                return maxEval, end_move
            
            else:
                minEval = float('inf')
                for pairs in children:
                    score += pairs[1]
                    eval, _ = minimax(pairs[0], depth-1, True, score, alpha, beta)
                    if minEval > eval:
                        minEval = eval
                        end_move = pairs[2]
                    minEval = min(minEval, eval)
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break
                    score -= pairs[1]
                # print("minEval: ", minEval, "end_move: ", end_move)
                return minEval, end_move
            
        for d in range(1, game_state.board.squares.count(SudokuBoard.empty)+1):
            _, do_move = minimax(game_state, d, True, 0, float("-inf"), float("inf"))
            self.propose_move(do_move)