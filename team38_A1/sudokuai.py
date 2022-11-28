#  (C) Copyright Wieger Wesselink 2021. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

import random
import time
from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove
import competitive_sudoku.sudokuai

#test

class SudokuAI(competitive_sudoku.sudokuai.SudokuAI):
    """
    Sudoku AI that computes a move for a given sudoku configuration.
    """

    def __init__(self):
        super().__init__()

    # N.B. This is a very naive implementation.
    def compute_best_move(self, game_state: GameState) -> None:
        N = game_state.board.N

    def possible(i, j, value):
        return game_state.board.get(i, j) == SudokuBoard.empty \
            and not TabooMove(i, j, value) in game_state.taboo_moves

        # all_moves = [Move(i, j, value) for i in range(N) for j in range(N)
        #              for value in range(1, N+1) if possible(i, j, value)]
        # move = random.choice(all_moves)
        # self.propose_move(move)

        # while True:
        #     time.sleep(0.2)
        #     self.propose_move(random.choice(all_moves))

    def minimax_player(board, depth, maxiPlayer, score, alpha, beta):
        if depth > board.squares.count(Sudokuboard.empty) or depth == 0 or board.squares.count(SudokuBoard.empty) == 0 or not getChildren(board, maxiPlayer):
            return score, None
                
            #determining the step for the max_player
        if maxiPlayer:
            best_max_score = float('-inf')
                for pairs in getChildren(board, maxiPlayer):
                    score += pairs[1]
                    evaluation, _ = minimax_player(pairs[0], depth-1, False, score, alpha, beta)
                    if best_max_score < evaluation:
                        best_max_score = evaluation
                        final_move = pairs[2]
                    alpha = max(alpha, evaluation)
                    if beta <= alpha:
                        break
                    score -= pairs[1]
                return best_max_score, final_move
            
            #determining the step for the min_player
            else:
                best_min_score = float('-inf')
                for pairs in getChildren(board, maxiPlayer):
                    score += pairs[1]
                    evaluation, _ = minimax_player(pairs[0], depth-1, True, score, alpha, beta)
                    if best_min_score > evaluation:
                        best_min_score = evaluation
                        final_move = pairs[2]
                    best_min_score = min(best_min_score, evaluation)
                    beta = min(beta, evaluation)
                    score -= pairs[1]
                return best_min_score, final_move



        