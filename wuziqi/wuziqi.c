#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <curses.h>
#include <unistd.h>
#include <math.h>
#include <locale.h>

#define BOARD_SIZE 15
#define MAX_DEPTH 3
#define PLAYER 1
#define AI 2
#define EMPTY 0

// 方向：水平、垂直、对角线（左上到右下）、对角线（左下到右上）
const int directions[4][2] = {{0, 1}, {1, 0}, {1, 1}, {1, -1}};

int board[BOARD_SIZE][BOARD_SIZE];
int cursor_x = BOARD_SIZE / 2, cursor_y = BOARD_SIZE / 2;
int game_over = 0;
int winner = 0;
int current_player = PLAYER;

// 初始化棋盘
void init_board() {
    for (int i = 0; i < BOARD_SIZE; i++) {
        for (int j = 0; j < BOARD_SIZE; j++) {
            board[i][j] = EMPTY;
        }
    }
    game_over = 0;
    winner = 0;
    current_player = PLAYER;
    cursor_x = BOARD_SIZE / 2;
    cursor_y = BOARD_SIZE / 2;
}

// 绘制棋盘（解决错位问题）
void draw_board() {
    clear();
    
    // 打印列号（顶部）
    printw("    ");
    for (int i = 0; i < BOARD_SIZE; i++) {
        printw("%2d", i);
    }
    printw("\n");
    
    // 上边框
    printw("   ┌");
    for (int j = 0; j < BOARD_SIZE - 1; j++) {
        printw("──┬");
    }
    printw("──┐\n");
    
    for (int i = 0; i < BOARD_SIZE; i++) {
        // 行号
        printw("%2d │", i);
        
        for (int j = 0; j < BOARD_SIZE; j++) {
            if (i == cursor_y && j == cursor_x) {
                attron(A_REVERSE);
            }
            
            // 使用固定宽度的字符表示棋子
            if (board[i][j] == EMPTY) {
                printw("  ");
            } else if (board[i][j] == PLAYER) {
                attron(COLOR_PAIR(1));
                printw(" O");
                attroff(COLOR_PAIR(1));
            } else if (board[i][j] == AI) {
                attron(COLOR_PAIR(2));
                printw(" X");
                attroff(COLOR_PAIR(2));
            }
            
            if (i == cursor_y && j == cursor_x) {
                attroff(A_REVERSE);
            }
            
            // 列分隔符
            printw("│");
        }
        printw("\n");
        
        // 行分隔符（最后一行不同）
        if (i < BOARD_SIZE - 1) {
            printw("   ├");
            for (int j = 0; j < BOARD_SIZE - 1; j++) {
                printw("──┼");
            }
            printw("──┤\n");
        }
    }
    
    // 下边框
    printw("   └");
    for (int j = 0; j < BOARD_SIZE - 1; j++) {
        printw("──┴");
    }
    printw("──┘\n");
    
    // 打印状态信息
    attron(A_BOLD);
    printw("当前状态: ");
    if (game_over) {
        if (winner == PLAYER) {
            printw("玩家胜利! ");
        } else if (winner == AI) {
            printw("AI胜利! ");
        } else {
            printw("平局! ");
        }
    } else {
        if (current_player == PLAYER) {
            printw("玩家回合 ");
        } else {
            printw("AI思考中 ");
        }
    }
    attroff(A_BOLD);
    
    // 显示操作提示
    printw("\n操作: 方向键移动, 空格键落子, R重新开始, Q退出\n");
    
    // 显示当前玩家
    printw("当前玩家: ");
    if (current_player == PLAYER) {
        attron(COLOR_PAIR(1));
        printw("O (你)");
        attroff(COLOR_PAIR(1));
    } else {
        attron(COLOR_PAIR(2));
        printw("X (AI)");
        attroff(COLOR_PAIR(2));
    }
    
    refresh();
}

// 检查在位置(x,y)落子后是否获胜
int check_win(int x, int y, int player) {
    for (int d = 0; d < 4; d++) {
        int count = 1; // 当前位置的棋子
        
        // 正向检查
        int dx = directions[d][0];
        int dy = directions[d][1];
        int nx = x + dx;
        int ny = y + dy;
        while (nx >= 0 && nx < BOARD_SIZE && ny >= 0 && ny < BOARD_SIZE && board[ny][nx] == player) {
            count++;
            nx += dx;
            ny += dy;
        }
        
        // 反向检查
        nx = x - dx;
        ny = y - dy;
        while (nx >= 0 && nx < BOARD_SIZE && ny >= 0 && ny < BOARD_SIZE && board[ny][nx] == player) {
            count++;
            nx -= dx;
            ny -= dy;
        }
        
        if (count >= 5) {
            return 1;
        }
    }
    return 0;
}

// 检查棋盘是否已满
int is_board_full() {
    for (int i = 0; i < BOARD_SIZE; i++) {
        for (int j = 0; j < BOARD_SIZE; j++) {
            if (board[i][j] == EMPTY) {
                return 0;
            }
        }
    }
    return 1;
}

// 生成可行的落子点（只考虑有棋子周围的位置）
// moves数组用于存储可行点，返回可行点数量
int get_available_moves(int moves[][2]) {
    int count = 0;
    int has_stone = 0;

    // 先检查棋盘上是否有棋子
    for (int i = 0; i < BOARD_SIZE; i++) {
        for (int j = 0; j < BOARD_SIZE; j++) {
            if (board[i][j] != EMPTY) {
                has_stone = 1;
                break;
            }
        }
        if (has_stone) break;
    }

    if (!has_stone) {
        // 没有棋子，返回中心点
        moves[count][0] = BOARD_SIZE / 2;
        moves[count][1] = BOARD_SIZE / 2;
        return 1;
    }

    // 标记可行点：空位且周围两格内有棋子
    for (int i = 0; i < BOARD_SIZE; i++) {
        for (int j = 0; j < BOARD_SIZE; j++) {
            if (board[i][j] != EMPTY) continue;

            int found = 0;
            for (int dy = -2; dy <= 2; dy++) {
                for (int dx = -2; dx <= 2; dx++) {
                    if (dx == 0 && dy == 0) continue;
                    int ni = i + dy;
                    int nj = j + dx;
                    if (ni >= 0 && ni < BOARD_SIZE && nj >= 0 && nj < BOARD_SIZE && board[ni][nj] != EMPTY) {
                        found = 1;
                        break;
                    }
                }
                if (found) break;
            }

            if (found) {
                moves[count][0] = j; // x
                moves[count][1] = i; // y
                count++;
            }
        }
    }
    return count;
}

// 评估棋型
int evaluate_pattern(int pattern[5], int player) {
    int count = 0;
    int opponent = player == PLAYER ? AI : PLAYER;
    int empty_ends = 0;

    // 计算连续棋子和空端
    for (int i = 0; i < 5; i++) {
        if (pattern[i] == player) {
            count++;
        } else if (pattern[i] == EMPTY) {
            empty_ends++;
        } else if (pattern[i] == opponent) {
            break;
        }
    }

    // 根据连续棋子和空端评分
    if (count == 5) return 100000; // 五连
    if (count == 4 && empty_ends >= 1) return 10000; // 活四
    if (count == 4) return 5000; // 冲四
    if (count == 3 && empty_ends >= 2) return 2000; // 活三
    if (count == 3) return 500; // 眠三
    if (count == 2 && empty_ends >= 2) return 200; // 活二
    if (count == 2) return 50; // 眠二
    if (count == 1) return 10; // 单子
    
    return 0;
}

// 评估位置得分
int evaluate_point(int x, int y, int player) {
    int score = 0;
    int opponent = player == PLAYER ? AI : PLAYER;

    // 四个方向
    for (int d = 0; d < 4; d++) {
        int pattern[5] = {0}; // 取5个连续位置
        int dx = directions[d][0];
        int dy = directions[d][1];

        // 取以(x,y)为中心，5个点的模式
        for (int i = -2; i <= 2; i++) {
            int nx = x + i * dx;
            int ny = y + i * dy;
            if (nx < 0 || nx >= BOARD_SIZE || ny < 0 || ny >= BOARD_SIZE) {
                // 边界外视为对手棋子（阻挡）
                pattern[i+2] = opponent;
            } else {
                pattern[i+2] = board[ny][nx];
            }
        }

        // 评估这个模式
        score += evaluate_pattern(pattern, player);
    }

    // 中心位置加成
    int center_x = abs(x - BOARD_SIZE/2);
    int center_y = abs(y - BOARD_SIZE/2);
    int center_bonus = 10 - (center_x + center_y);
    if (center_bonus > 0) {
        score += center_bonus;
    }

    return score;
}

// 评估整个棋盘的得分
int evaluate_board(int player) {
    int score = 0;
    int opponent = player == PLAYER ? AI : PLAYER;

    for (int i = 0; i < BOARD_SIZE; i++) {
        for (int j = 0; j < BOARD_SIZE; j++) {
            if (board[i][j] == player) {
                score += evaluate_point(j, i, player);
            }
        }
    }
    return score;
}

// 极小极大搜索，带α-β剪枝
int minimax(int depth, int alpha, int beta, int maximizing_player) {
    // 检查是否结束
    if (depth == 0) {
        return evaluate_board(AI) - evaluate_board(PLAYER); // AI视角：AI得分减去玩家得分
    }

    int moves[BOARD_SIZE*BOARD_SIZE][2];
    int num_moves = get_available_moves(moves);

    if (num_moves == 0) {
        return 0; // 平局
    }

    if (maximizing_player) { // AI层
        int max_eval = -1000000;
        for (int i = 0; i < num_moves; i++) {
            int x = moves[i][0];
            int y = moves[i][1];

            // 落子
            board[y][x] = AI;
            int eval = minimax(depth-1, alpha, beta, 0);
            board[y][x] = EMPTY; // 撤销

            if (eval > max_eval) {
                max_eval = eval;
            }

            if (eval > alpha) {
                alpha = eval;
            }

            if (beta <= alpha) {
                break; // 剪枝
            }
        }
        return max_eval;
    } else { // 玩家层
        int min_eval = 1000000;
        for (int i = 0; i < num_moves; i++) {
            int x = moves[i][0];
            int y = moves[i][1];

            board[y][x] = PLAYER;
            int eval = minimax(depth-1, alpha, beta, 1);
            board[y][x] = EMPTY;

            if (eval < min_eval) {
                min_eval = eval;
            }

            if (eval < beta) {
                beta = eval;
            }

            if (beta <= alpha) {
                break;
            }
        }
        return min_eval;
    }
}

// AI进行移动
void ai_move() {
    int best_move[2] = {-1, -1};
    int best_eval = -1000000;
    int moves[BOARD_SIZE*BOARD_SIZE][2];
    int num_moves = get_available_moves(moves);

    if (num_moves == 0) {
        return; // 没有可行步
    }

    for (int i = 0; i < num_moves; i++) {
        int x = moves[i][0];
        int y = moves[i][1];

        board[y][x] = AI;
        int eval = minimax(MAX_DEPTH, -1000000, 1000000, 0); // 注意：AI落子后，下一层是玩家（min层）
        board[y][x] = EMPTY;

        if (eval > best_eval) {
            best_eval = eval;
            best_move[0] = x;
            best_move[1] = y;
        }
    }

    if (best_move[0] != -1) {
        board[best_move[1]][best_move[0]] = AI;
        // 检查AI是否获胜
        if (check_win(best_move[0], best_move[1], AI)) {
            game_over = 1;
            winner = AI;
        } else if (is_board_full()) {
            game_over = 1;
        }
    }
}

// 玩家移动光标并落子
void player_move(int key) {
    if (key == KEY_UP) {
        if (cursor_y > 0) cursor_y--;
    } else if (key == KEY_DOWN) {
        if (cursor_y < BOARD_SIZE-1) cursor_y++;
    } else if (key == KEY_LEFT) {
        if (cursor_x > 0) cursor_x--;
    } else if (key == KEY_RIGHT) {
        if (cursor_x < BOARD_SIZE-1) cursor_x++;
    } else if (key == ' ') {
        if (board[cursor_y][cursor_x] == EMPTY && !game_over) {
            board[cursor_y][cursor_x] = PLAYER;
            
            // 检查玩家是否获胜
            if (check_win(cursor_x, cursor_y, PLAYER)) {
                game_over = 1;
                winner = PLAYER;
            } else if (is_board_full()) {
                game_over = 1;
            } else {
                // 立即更新界面显示玩家落子
                draw_board();
                refresh();
                
                // 添加短暂延迟让玩家看到自己的落子
                napms(300); // 300毫秒延迟
                
                // AI回合
                current_player = AI;
                ai_move();
                current_player = PLAYER;
            }
        }
    } else if (key == 'r' || key == 'R') {
        // 重新开始
        init_board();
    } else if (key == 'q' || key == 'Q') {
        // 退出
        endwin();
        exit(0);
    }
}

int main() {
    // 设置locale以支持中文
    setlocale(LC_ALL, "");
    
    // 初始化Ncurses
    initscr();
    cbreak();
    keypad(stdscr, TRUE);
    noecho();
    curs_set(0); // 隐藏光标
    
    // 初始化颜色
    if (has_colors()) {
        start_color();
        init_pair(1, COLOR_GREEN, COLOR_BLACK); // 玩家：绿色棋子
        init_pair(2, COLOR_RED, COLOR_BLACK);   // AI：红色棋子
    }
    
    // 显示欢迎信息
    printw("五子棋游戏 - 人机对战\n");
    printw("按任意键开始游戏...");
    refresh();
    getch();
    
    // 初始化棋盘
    init_board();
    
    // 主循环
    int ch;
    while (1) {
        draw_board();
        
        if (!game_over && current_player == AI) {
            // AI回合
            ai_move();
            current_player = PLAYER;
            // 检查游戏是否结束
            if (is_board_full()) {
                game_over = 1;
            }
        } else {
            ch = getch();
            player_move(ch);
        }
    }
    
    endwin();
    return 0;
}