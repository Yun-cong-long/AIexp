import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'  # 强制使用纯软件渲染
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'  # 隐藏Pygame欢迎信息

import pygame
import sys
import numpy as np
import time
from collections import defaultdict

# 初始化pygame
pygame.init()

# 游戏常量 - 使用更小的窗口尺寸以适应可能的渲染限制
BOARD_SIZE = 15
GRID_SIZE = 30  # 减小格子大小
MARGIN = 30     # 减小边距
WIDTH = BOARD_SIZE * GRID_SIZE + 2 * MARGIN
HEIGHT = BOARD_SIZE * GRID_SIZE + 2 * MARGIN
LINE_COLOR = (0, 0, 0)  # 黑色
BACKGROUND_COLOR = (220, 179, 92)  # 木质背景
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# 创建游戏窗口 - 使用纯软件渲染
try:
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SWSURFACE)
    pygame.display.set_caption("五子棋游戏 - 人机对弈")
except pygame.error as e:
    print(f"无法创建游戏窗口: {e}")
    print("尝试使用更简单的渲染模式...")
    # 尝试使用更基本的渲染方式
    try:
        screen = pygame.display.set_mode((800, 600), pygame.SWSURFACE)
        pygame.display.set_caption("五子棋游戏 - 兼容模式")
    except:
        print("无法初始化图形界面，退出程序")
        sys.exit(1)

class GomokuGame:
    def __init__(self):
        self.board = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=int)  # 0:空, 1:黑, 2:白
        self.current_player = 1  # 黑棋先行
        self.game_over = False
        self.winner = None
        self.last_move = None
        self.depth = 2  # 减小搜索深度以提高性能
        
        # 方向：水平、垂直、对角线（左上到右下）、对角线（左下到右上）
        self.directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        
        # 简化的棋型评分 - 避免复杂计算
        self.pattern_scores = {
            'five': 100000,       # 五连
            'open_four': 10000,   # 活四
            'half_four': 5000,    # 冲四
            'open_three': 2000,   # 活三
            'half_three': 500,    # 眠三
            'open_two': 200,      # 活二
            'half_two': 50,       # 眠二
            'single': 10          # 单子
        }
    
    def reset(self):
        """重置游戏"""
        self.board = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=int)
        self.current_player = 1
        self.game_over = False
        self.winner = None
        self.last_move = None
    
    def make_move(self, row, col):
        """在指定位置落子"""
        if self.is_valid_move(row, col):
            self.board[row][col] = self.current_player
            self.last_move = (row, col)
            
            # 检查是否获胜
            if self.check_win(row, col):
                self.game_over = True
                self.winner = self.current_player
            # 检查是否平局
            elif np.count_nonzero(self.board) == BOARD_SIZE * BOARD_SIZE:
                self.game_over = True
            else:
                # 切换玩家
                self.current_player = 3 - self.current_player  # 1->2, 2->1
            
            return True
        return False
    
    def is_valid_move(self, row, col):
        """检查落子是否有效"""
        return (0 <= row < BOARD_SIZE and 
                0 <= col < BOARD_SIZE and 
                self.board[row][col] == 0)
    
    def check_win(self, row, col):
        """检查是否有玩家获胜"""
        player = self.board[row][col]
        
        for dx, dy in self.directions:
            count = 1  # 当前位置的棋子
            
            # 正向检查
            r, c = row + dx, col + dy
            while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and self.board[r][c] == player:
                count += 1
                r += dx
                c += dy
            
            # 反向检查
            r, c = row - dx, col - dy
            while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and self.board[r][c] == player:
                count += 1
                r -= dx
                c -= dy
            
            if count >= 5:
                return True
        
        return False
    
    def evaluate_position(self, row, col, player):
        """评估单个位置的得分 - 简化版本"""
        score = 0
        
        # 简化的评估函数，只检查四个方向
        for dx, dy in self.directions:
            count = 0
            empty_ends = 0
            
            # 正向检查
            r, c = row + dx, col + dy
            while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
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
            while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
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
                score += self.pattern_scores['five']  # 五连
            elif count == 3:
                if empty_ends == 2:
                    score += self.pattern_scores['open_four']  # 活四
                elif empty_ends == 1:
                    score += self.pattern_scores['half_four']   # 冲四
            elif count == 2:
                if empty_ends == 2:
                    score += self.pattern_scores['open_three']  # 活三
                elif empty_ends == 1:
                    score += self.pattern_scores['half_three']  # 眠三
            elif count == 1:
                if empty_ends == 2:
                    score += self.pattern_scores['open_two']   # 活二
                elif empty_ends == 1:
                    score += self.pattern_scores['half_two']   # 眠二
        
        return score
    
    def evaluate_board(self, player):
        """评估整个棋盘的得分 - 简化版本"""
        score = 0
        
        # 只评估有棋子的位置
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.board[r][c] == player:
                    # 中心位置加成
                    dist_to_center = abs(r - BOARD_SIZE//2) + abs(c - BOARD_SIZE//2)
                    center_value = max(0, 10 - dist_to_center)
                    score += center_value
                    
                    # 评估单个位置的得分
                    score += self.evaluate_position(r, c, player)
        
        return score
    
    def get_available_moves(self):
        """获取所有可行的落子位置（只考虑有棋子周围的点）"""
        moves = []
        
        # 如果有棋子，只考虑棋子周围的点
        if np.any(self.board):
            for r in range(BOARD_SIZE):
                for c in range(BOARD_SIZE):
                    if self.board[r][c] == 0:
                        # 检查周围是否有棋子
                        for dr in range(-1, 2):
                            for dc in range(-1, 2):
                                if dr == 0 and dc == 0:
                                    continue
                                nr, nc = r + dr, c + dc
                                if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
                                    if self.board[nr][nc] != 0:
                                        moves.append((r, c))
                                        break
        else:
            # 棋盘为空，选择中心点
            moves.append((BOARD_SIZE//2, BOARD_SIZE//2))
        
        return moves
    
    def minimax(self, depth, alpha, beta, maximizing_player):
        """极小极大算法，带α-β剪枝 - 简化版本"""
        # 游戏结束或达到搜索深度
        if depth == 0 or self.game_over:
            player_score = self.evaluate_board(2)  # 电脑是白棋(2)
            opponent_score = self.evaluate_board(1)  # 玩家是黑棋(1)
            return player_score - opponent_score, None
        
        moves = self.get_available_moves()
        if not moves:
            return 0, None
        
        best_move = None
        
        if maximizing_player:  # 电脑（最大化）
            max_eval = float('-inf')
            for move in moves:
                r, c = move
                self.board[r][c] = 2  # 电脑落白棋
                prev_game_over = self.game_over
                self.game_over = self.check_win(r, c)
                
                eval_score, _ = self.minimax(depth - 1, alpha, beta, False)
                
                self.board[r][c] = 0  # 撤销落子
                self.game_over = prev_game_over
                
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = move
                
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break  # α-β剪枝
            
            return max_eval, best_move
        
        else:  # 玩家（最小化）
            min_eval = float('inf')
            for move in moves:
                r, c = move
                self.board[r][c] = 1  # 玩家落黑棋
                prev_game_over = self.game_over
                self.game_over = self.check_win(r, c)
                
                eval_score, _ = self.minimax(depth - 1, alpha, beta, True)
                
                self.board[r][c] = 0  # 撤销落子
                self.game_over = prev_game_over
                
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = move
                
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break  # α-β剪枝
            
            return min_eval, best_move
    
    def ai_move(self):
        """AI进行移动 - 简化版本"""
        start_time = time.time()
        _, move = self.minimax(self.depth, float('-inf'), float('inf'), True)
        
        if move:
            r, c = move
            self.make_move(r, c)
            print(f"AI思考时间: {time.time() - start_time:.2f}秒")
            return True
        return False

# 创建游戏实例
game = GomokuGame()

# 绘制棋盘
def draw_board():
    try:
        screen.fill(BACKGROUND_COLOR)
    except pygame.error:
        return
    
    try:
        # 绘制网格线
        for i in range(BOARD_SIZE):
            # 横线
            pygame.draw.line(screen, LINE_COLOR, 
                            (MARGIN, MARGIN + i * GRID_SIZE), 
                            (MARGIN + (BOARD_SIZE - 1) * GRID_SIZE, MARGIN + i * GRID_SIZE), 
                            2)
            # 竖线
            pygame.draw.line(screen, LINE_COLOR, 
                            (MARGIN + i * GRID_SIZE, MARGIN), 
                            (MARGIN + i * GRID_SIZE, MARGIN + (BOARD_SIZE - 1) * GRID_SIZE), 
                            2)
    except pygame.error:
        pass
    
    # 绘制棋子
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            try:
                if game.board[r][c] == 1:  # 黑棋
                    pygame.draw.circle(screen, BLACK, 
                                    (MARGIN + c * GRID_SIZE, MARGIN + r * GRID_SIZE), 
                                    GRID_SIZE // 2 - 2)
                elif game.board[r][c] == 2:  # 白棋
                    pygame.draw.circle(screen, WHITE, 
                                    (MARGIN + c * GRID_SIZE, MARGIN + r * GRID_SIZE), 
                                    GRID_SIZE // 2 - 2)
                    pygame.draw.circle(screen, BLACK, 
                                    (MARGIN + c * GRID_SIZE, MARGIN + r * GRID_SIZE), 
                                    GRID_SIZE // 2 - 2, 1)  # 白色棋子加黑色边框
            except pygame.error:
                pass
    
    # 标记最后一步
    if game.last_move:
        r, c = game.last_move
        try:
            pygame.draw.circle(screen, RED, 
                            (MARGIN + c * GRID_SIZE, MARGIN + r * GRID_SIZE), 
                            5)
        except pygame.error:
            pass
    
    # 显示游戏状态
    try:
        font = pygame.font.SysFont(None, 30)
        if game.game_over:
            if game.winner == 1:
                text = font.render("玩家胜利! 按R重新开始", True, BLUE)
            elif game.winner == 2:
                text = font.render("AI胜利! 按R重新开始", True, BLUE)
            else:
                text = font.render("平局! 按R重新开始", True, BLUE)
        else:
            if game.current_player == 1:
                text = font.render("玩家回合 (黑棋)", True, BLUE)
            else:
                text = font.render("AI思考中...", True, BLUE)
        
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 15))
    except pygame.error:
        pass

# 主游戏循环
def main():
    global game
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  # 按R重置游戏
                    game.reset()
            
            if not game.game_over and game.current_player == 1:  # 玩家回合
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = pygame.mouse.get_pos()
                    col = round((x - MARGIN) / GRID_SIZE)
                    row = round((y - MARGIN) / GRID_SIZE)
                    
                    if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
                        if game.make_move(row, col):
                            # 玩家移动后，如果是AI回合，AI立即移动
                            if not game.game_over and game.current_player == 2:
                                pygame.display.flip()  # 更新显示
                                pygame.time.delay(300)  # 延迟一下，让玩家看到自己的落子
                                game.ai_move()
        
        # AI回合
        if not game.game_over and game.current_player == 2:
            game.ai_move()
        
        try:
            draw_board()
            pygame.display.flip()
        except pygame.error as e:
            print(f"渲染错误: {e}")
            pygame.quit()
            sys.exit(1)
        
        pygame.time.delay(50)

if __name__ == "__main__":
    main()