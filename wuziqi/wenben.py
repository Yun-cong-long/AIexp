import numpy as np
import time

class TerminalGomoku:
    def __init__(self):
        self.board = np.zeros((15, 15), dtype=int)
        self.current_player = 1
        self.game_over = False
        self.winner = None
        self.depth = 3
        self.symbols = {0: '.', 1: 'X', 2: 'O'}
        
        # 方向：水平、垂直、对角线（左上到右下）、对角线（左下到右上）
        self.directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
    
    def reset(self):
        self.board = np.zeros((15, 15), dtype=int)
        self.current_player = 1
        self.game_over = False
        self.winner = None
    
    def print_board(self):
        print("\n" + "="*40)
        print("   " + " ".join([f"{i:2}" for i in range(15)]))
        for i in range(15):
            print(f"{i:2} ", end="")
            for j in range(15):
                print(f" {self.symbols[self.board[i, j]]}", end="")
            print()
        print("="*40)
    
    def make_move(self, row, col):
        if 0 <= row < 15 and 0 <= col < 15 and self.board[row, col] == 0:
            self.board[row, col] = self.current_player
            
            if self.check_win(row, col):
                self.game_over = True
                self.winner = self.current_player
            elif np.count_nonzero(self.board) == 15*15:
                self.game_over = True
            else:
                self.current_player = 3 - self.current_player
            return True
        return False
    
    def check_win(self, row, col):
        player = self.board[row][col]
        
        for dx, dy in self.directions:
            count = 1
            
            # 正向检查
            r, c = row + dx, col + dy
            while 0 <= r < 15 and 0 <= c < 15 and self.board[r][c] == player:
                count += 1
                r += dx
                c += dy
            
            # 反向检查
            r, c = row - dx, col - dy
            while 0 <= r < 15 and 0 <= c < 15 and self.board[r][c] == player:
                count += 1
                r -= dx
                c -= dy
            
            if count >= 5:
                return True
        
        return False
    
    def evaluate_position(self, row, col, player):
        score = 0
        
        for dx, dy in self.directions:
            count = 0
            empty_ends = 0
            
            # 正向检查
            r, c = row + dx, col + dy
            while 0 <= r < 15 and 0 <= c < 15:
                if self.board[r][c] == player:
                    count += 1
                elif self.board[r][c] == 0:
                    empty_ends += 1
                    break
                else:
                    break
                r += dx
                c += dy
            
            # 反向检查
            r, c = row - dx, col - dy
            while 0 <= r < 15 and 0 <= c < 15:
                if self.board[r][c] == player:
                    count += 1
                elif self.board[r][c] == 0:
                    empty_ends += 1
                    break
                else:
                    break
                r -= dx
                c -= dy
            
            # 根据连续棋子数和空端点评分
            if count >= 4:
                score += 10000
            elif count == 3:
                if empty_ends == 2:
                    score += 5000
                elif empty_ends == 1:
                    score += 1000
            elif count == 2:
                if empty_ends == 2:
                    score += 500
                elif empty_ends == 1:
                    score += 100
            elif count == 1:
                if empty_ends == 2:
                    score += 50
        
        return score
    
    def evaluate_board(self, player):
        score = 0
        
        for r in range(15):
            for c in range(15):
                if self.board[r][c] == player:
                    dist = abs(r-7) + abs(c-7)
                    center_bonus = max(0, 10 - dist)
                    score += center_bonus
                    score += self.evaluate_position(r, c, player)
        
        return score
    
    def get_available_moves(self):
        moves = []
        
        if np.any(self.board):
            for r in range(15):
                for c in range(15):
                    if self.board[r][c] == 0:
                        for dr in range(-1, 2):
                            for dc in range(-1, 2):
                                nr, nc = r + dr, c + dc
                                if 0 <= nr < 15 and 0 <= nc < 15 and self.board[nr][nc] != 0:
                                    moves.append((r, c))
                                    break
        else:
            moves.append((7, 7))
        
        return moves
    
    def minimax(self, depth, alpha, beta, maximizing_player):
        if depth == 0 or self.game_over:
            player_score = self.evaluate_board(2)
            opponent_score = self.evaluate_board(1)
            return player_score - opponent_score, None
        
        moves = self.get_available_moves()
        if not moves:
            return 0, None
        
        best_move = None
        
        if maximizing_player:
            max_eval = float('-inf')
            for move in moves:
                r, c = move
                self.board[r][c] = 2
                prev_state = self.game_over
                self.game_over = self.check_win(r, c)
                
                eval_score, _ = self.minimax(depth-1, alpha, beta, False)
                
                self.board[r][c] = 0
                self.game_over = prev_state
                
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = move
                
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            
            return max_eval, best_move
        
        else:
            min_eval = float('inf')
            for move in moves:
                r, c = move
                self.board[r][c] = 1
                prev_state = self.game_over
                self.game_over = self.check_win(r, c)
                
                eval_score, _ = self.minimax(depth-1, alpha, beta, True)
                
                self.board[r][c] = 0
                self.game_over = prev_state
                
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = move
                
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            
            return min_eval, best_move
    
    def ai_move(self):
        start = time.time()
        _, move = self.minimax(self.depth, float('-inf'), float('inf'), True)
        
        if move:
            r, c = move
            self.make_move(r, c)
            print(f"AI落子: ({r}, {c}), 思考时间: {time.time()-start:.2f}秒")
            return True
        return False

def main():
    game = TerminalGomoku()
    
    print("="*50)
    print("五子棋游戏 - 终端版")
    print("玩家: X, AI: O")
    print("输入坐标格式: 行 列 (例如: 7 7)")
    print("="*50)
    
    while True:
        game.print_board()
        
        if game.game_over:
            if game.winner == 1:
                print("恭喜！你赢了！")
            elif game.winner == 2:
                print("AI赢了！")
            else:
                print("平局！")
            
            restart = input("再玩一局? (y/n): ").lower()
            if restart == 'y':
                game.reset()
                continue
            else:
                break
        
        if game.current_player == 1:  # 玩家回合
            try:
                move = input("你的回合 (输入坐标, 例如'7 7'): ")
                row, col = map(int, move.split())
                if not game.make_move(row, col):
                    print("无效落子，请重试!")
            except:
                print("输入格式错误，请使用'行 列'格式")
        else:  # AI回合
            print("AI思考中...")
            game.ai_move()

if __name__ == "__main__":
    main()