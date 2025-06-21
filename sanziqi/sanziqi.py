import tkinter as tk
from tkinter import messagebox, font
import numpy as np
import os

class TicTacToe:
    def __init__(self, master):
        self.master = master
        self.master.title("一字棋游戏 - 人机对弈")
        self.master.resizable(False, False)
        
        # 设置窗口位置居中
        window_width = 400
        window_height = 500
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.master.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # 设置背景色
        self.master.configure(bg="#f0f0f0")
        
        # 创建字体
        self.create_fonts()
        
        # 初始化游戏
        self.board = np.full((3, 3), ' ')
        self.player_marker = 'X'
        self.ai_marker = 'O'
        self.current_player = self.player_marker
        self.game_over = False
        self.buttons = []
        
        # 创建界面元素
        self.create_widgets()
    
    def create_fonts(self):
        """创建字体，确保支持中文"""
        # 尝试使用系统中可能的中文字体
        chinese_font_names = [
            "WenQuanYi Zen Hei", 
            "WenQuanYi Micro Hei", 
            "Noto Sans CJK SC", 
            "Source Han Sans SC",
            "Microsoft YaHei",
            "SimHei",
            "KaiTi"
        ]
        
        # 获取系统可用字体
        available_fonts = list(font.families())
        
        # 查找可用的中文字体
        selected_font = "Helvetica"  # 默认字体
        for font_name in chinese_font_names:
            if font_name in available_fonts:
                selected_font = font_name
                break
        
        # 创建字体对象
        self.title_font = font.Font(family=selected_font, size=18, weight="bold")
        self.status_font = font.Font(family=selected_font, size=14)
        self.button_font = font.Font(family=selected_font, size=24, weight="bold")
        self.reset_font = font.Font(family=selected_font, size=12)
        
        # 打印使用的字体（调试用）
        print(f"使用字体: {selected_font}")
    
    def create_widgets(self):
        """创建界面元素"""
        # 创建标题
        self.title_label = tk.Label(self.master, text="一字棋游戏", 
                                  font=self.title_font, bg="#f0f0f0", fg="#2c3e50")
        self.title_label.grid(row=0, column=0, columnspan=3, pady=10)
        
        # 创建说明标签
        self.info_label = tk.Label(self.master, text="玩家: X    AI: O", 
                                  font=self.status_font, bg="#f0f0f0")
        self.info_label.grid(row=1, column=0, columnspan=3, pady=(0, 10))
        
        # 创建棋盘按钮框架
        self.board_frame = tk.Frame(self.master, bg="#f0f0f0")
        self.board_frame.grid(row=2, column=0, columnspan=3, padx=10, pady=10)
        
        # 创建棋盘按钮
        self.buttons = []
        for i in range(3):
            row_buttons = []
            for j in range(3):
                button = tk.Button(
                    self.board_frame, text=" ", font=self.button_font,
                    width=3, height=1, bg="#3498db", fg="white", relief="ridge",
                    command=lambda i=i, j=j: self.player_move(i, j)
                )
                button.grid(row=i, column=j, padx=5, pady=5)
                row_buttons.append(button)
            self.buttons.append(row_buttons)
        
        # 创建状态标签
        self.status_var = tk.StringVar()
        self.status_var.set("你的回合 (X)")
        self.status_label = tk.Label(self.master, textvariable=self.status_var, 
                                    font=self.status_font, bg="#f0f0f0", height=2)
        self.status_label.grid(row=3, column=0, columnspan=3, pady=(10, 0))
        
        # 创建重新开始按钮
        self.reset_button = tk.Button(self.master, text="重新开始", command=self.reset, 
                                    font=self.reset_font, bg="#2ecc71", fg="white",
                                    width=15, height=1)
        self.reset_button.grid(row=4, column=0, columnspan=3, pady=10)
        
        # 配置网格权重，确保元素居中
        for i in range(5):
            self.master.grid_rowconfigure(i, weight=1)
        for i in range(3):
            self.master.grid_columnconfigure(i, weight=1)
    
    def player_move(self, row, col):
        """玩家移动"""
        if self.board[row][col] == ' ' and not self.game_over and self.current_player == self.player_marker:
            self.board[row][col] = self.player_marker
            self.buttons[row][col].config(text=self.player_marker, fg="#2c3e50", state=tk.DISABLED)
            
            # 检查游戏状态
            if self.is_winner(self.player_marker):
                self.game_over = True
                self.status_var.set("你赢了!")
                messagebox.showinfo("游戏结束", "恭喜你赢了!")
            elif self.is_board_full():
                self.game_over = True
                self.status_var.set("平局!")
                messagebox.showinfo("游戏结束", "平局!")
            else:
                # 切换玩家
                self.current_player = self.ai_marker
                self.status_var.set("AI思考中...")
                self.master.update()  # 立即更新界面显示状态
                self.master.after(500, self.ai_move)
    
    def ai_move(self):
        """AI移动"""
        if not self.game_over and self.current_player == self.ai_marker:
            row, col = self.get_best_move()
            if row is not None and col is not None:
                self.board[row][col] = self.ai_marker
                self.buttons[row][col].config(text=self.ai_marker, fg="#e74c3c", state=tk.DISABLED)
                
                # 检查游戏状态
                if self.is_winner(self.ai_marker):
                    self.game_over = True
                    self.status_var.set("AI赢了!")
                    messagebox.showinfo("游戏结束", "AI赢了!")
                elif self.is_board_full():
                    self.game_over = True
                    self.status_var.set("平局!")
                    messagebox.showinfo("游戏结束", "平局!")
                else:
                    # 切换玩家
                    self.current_player = self.player_marker
                    self.status_var.set("你的回合 (X)")
    
    def is_winner(self, marker):
        """检查指定标记是否获胜"""
        # 检查行
        for i in range(3):
            if all(self.board[i][j] == marker for j in range(3)):
                return True
        
        # 检查列
        for j in range(3):
            if all(self.board[i][j] == marker for i in range(3)):
                return True
        
        # 检查对角线
        if all(self.board[i][i] == marker for i in range(3)):
            return True
        if all(self.board[i][2-i] == marker for i in range(3)):
            return True
        
        return False
    
    def is_board_full(self):
        """检查棋盘是否已满"""
        return all(self.board[i][j] != ' ' for i in range(3) for j in range(3))
    
    def get_empty_cells(self):
        """获取所有空位置"""
        return [(i, j) for i in range(3) for j in range(3) if self.board[i][j] == ' ']
    
    def evaluate(self):
        """
        估价函数：评估当前棋盘状态
        - 计算机获胜: +10
        - 玩家获胜: -10
        - 平局: 0
        - 其他情况: 根据可能的获胜路径评估
        """
        if self.is_winner(self.ai_marker):
            return 10
        elif self.is_winner(self.player_marker):
            return -10
        elif self.is_board_full():
            return 0
        
        # 启发式评估：计算可能的获胜路径
        ai_paths = 0
        player_paths = 0
        
        # 检查行
        for i in range(3):
            if any(self.board[i][j] == self.ai_marker for j in range(3)) and \
               not any(self.board[i][j] == self.player_marker for j in range(3)):
                ai_paths += 1
            if any(self.board[i][j] == self.player_marker for j in range(3)) and \
               not any(self.board[i][j] == self.ai_marker for j in range(3)):
                player_paths += 1
        
        # 检查列
        for j in range(3):
            col = [self.board[i][j] for i in range(3)]
            if any(c == self.ai_marker for c in col) and not any(c == self.player_marker for c in col):
                ai_paths += 1
            if any(c == self.player_marker for c in col) and not any(c == self.ai_marker for c in col):
                player_paths += 1
        
        # 检查对角线
        diag1 = [self.board[i][i] for i in range(3)]
        if any(c == self.ai_marker for c in diag1) and not any(c == self.player_marker for c in diag1):
            ai_paths += 1
        if any(c == self.player_marker for c in diag1) and not any(c == self.ai_marker for c in diag1):
            player_paths += 1
        
        diag2 = [self.board[i][2-i] for i in range(3)]
        if any(c == self.ai_marker for c in diag2) and not any(c == self.player_marker for c in diag2):
            ai_paths += 1
        if any(c == self.player_marker for c in diag2) and not any(c == self.ai_marker for c in diag2):
            player_paths += 1
        
        return ai_paths - player_paths
    
    def minimax(self, depth, is_maximizing, alpha=-float('inf'), beta=float('inf')):
        """极大极小搜索算法（带Alpha-Beta剪枝）"""
        if self.is_winner(self.ai_marker):
            return 10 - depth
        if self.is_winner(self.player_marker):
            return depth - 10
        if self.is_board_full():
            return 0
        
        if is_maximizing:
            best_score = -float('inf')
            for i, j in self.get_empty_cells():
                self.board[i][j] = self.ai_marker
                score = self.minimax(depth + 1, False, alpha, beta)
                self.board[i][j] = ' '
                best_score = max(score, best_score)
                alpha = max(alpha, best_score)
                if beta <= alpha:
                    break
            return best_score
        else:
            best_score = float('inf')
            for i, j in self.get_empty_cells():
                self.board[i][j] = self.player_marker
                score = self.minimax(depth + 1, True, alpha, beta)
                self.board[i][j] = ' '
                best_score = min(score, best_score)
                beta = min(beta, best_score)
                if beta <= alpha:
                    break
            return best_score
    
    def get_best_move(self):
        """获取AI的最佳移动位置"""
        best_score = -float('inf')
        best_move = None
        
        # 如果是第一步，选择中心位置
        if len(self.get_empty_cells()) == 9:
            return (1, 1)
        
        # 如果只有一步可走，直接返回
        empty_cells = self.get_empty_cells()
        if len(empty_cells) == 0:
            return (None, None)
        if len(empty_cells) == 1:
            return empty_cells[0]
        
        for i, j in empty_cells:
            self.board[i][j] = self.ai_marker
            score = self.minimax(0, False)
            self.board[i][j] = ' '
            
            if score > best_score:
                best_score = score
                best_move = (i, j)
        
        return best_move
    
    def reset(self):
        """重置游戏"""
        self.board = np.full((3, 3), ' ')
        self.current_player = self.player_marker
        self.game_over = False
        self.status_var.set("你的回合 (X)")
        
        # 重置按钮
        for i in range(3):
            for j in range(3):
                self.buttons[i][j].config(text=" ", state=tk.NORMAL, bg="#3498db", fg="white")

if __name__ == "__main__":
    # 设置环境变量确保中文支持
    os.environ['LANG'] = 'zh_CN.UTF-8'
    os.environ['LC_ALL'] = 'zh_CN.UTF-8'
    
    root = tk.Tk()
    game = TicTacToe(root)
    root.mainloop()