import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib import rcParams
import os

# Ubuntu 22.04 中文字体解决方案
def set_chinese_font():
    try:
        # 尝试常见中文字体路径
        font_dirs = [
            '/usr/share/fonts/truetype/wqy/',  # 文泉驿
            '/usr/share/fonts/truetype/noto/',  # Noto 字体
            '/usr/share/fonts/truetype/msttcorefonts/',  # 微软核心字体
            '/usr/share/fonts/truetype/arphic/'  # 文鼎字体
        ]
        
        # 可能的字体文件名
        possible_fonts = [
            'wqy-microhei.ttc',        # 文泉驿微米黑
            'wqy-zenhei.ttc',           # 文泉驿正黑
            'NotoSansCJK-Regular.ttc',  # Noto Sans CJK
            'uming.ttc',                # 文鼎明体
            'ukai.ttc',                 # 文鼎楷体
            'arphic-uming.ttf',         # 文鼎明体
            'arphic-ukai.ttf'           # 文鼎楷体
        ]
        
        # 查找系统中可用的中文字体
        font_path = None
        for font_dir in font_dirs:
            if os.path.exists(font_dir):
                for font_file in possible_fonts:
                    font_path_candidate = os.path.join(font_dir, font_file)
                    if os.path.exists(font_path_candidate):
                        font_path = font_path_candidate
                        break
                if font_path:
                    break
        
        # 如果找到字体文件，设置它
        if font_path:
            font_prop = fm.FontProperties(fname=font_path)
            rcParams['font.family'] = [font_prop.get_name(), 'sans-serif']
            print(f"使用中文字体: {font_path}")
        else:
            # 使用默认的sans-serif字体作为后备
            rcParams['font.family'] = 'sans-serif'
            print("使用后备sans-serif字体")
        
        # 确保正确显示负号
        rcParams['axes.unicode_minus'] = False
        
    except Exception as e:
        print(f"字体设置错误: {e}")
        print("图表可能无法正确显示中文")

# 设置中文字体
set_chinese_font()

# 目标函数
def fitness_func(x):
    return x + np.sin(10 * np.pi * x) + 1.0

# 二进制编码转换
def binary_to_float(binary, chrom_length, lb, ub):
    max_val = 2**chrom_length - 1
    decimal = int(binary, 2)
    return lb + decimal * (ub - lb) / max_val

# 初始化种群
def init_population(pop_size, chrom_length):
    return [''.join(np.random.choice(['0', '1'], size=chrom_length)) 
            for _ in range(pop_size)]

# 选择操作（轮盘赌）
def selection(population, fitnesses):
    # 确保适应度值为正
    min_fitness = np.min(fitnesses)
    if min_fitness < 0:
        adjusted_fitnesses = fitnesses - min_fitness + 1e-10
    else:
        adjusted_fitnesses = fitnesses + 1e-10
    
    probs = adjusted_fitnesses / np.sum(adjusted_fitnesses)
    selected_indices = np.random.choice(
        len(population), size=len(population), p=probs
    )
    return [population[i] for i in selected_indices]

# 交叉操作（单点交叉）
def crossover(parent1, parent2, pc):
    if np.random.random() < pc:
        point = np.random.randint(1, len(parent1))
        child1 = parent1[:point] + parent2[point:]
        child2 = parent2[:point] + parent1[point:]
        return child1, child2
    return parent1, parent2

# 变异操作
def mutation(individual, pm):
    mutated = list(individual)
    for i in range(len(mutated)):
        if np.random.random() < pm:
            mutated[i] = '0' if mutated[i] == '1' else '1'
    return ''.join(mutated)

# 主遗传算法（带精英保留）
def genetic_algorithm():
    # 参数设置
    pop_size = 100      # 种群规模
    chrom_length = 22   # 染色体长度
    pc = 0.85           # 交叉概率
    pm = 0.02           # 变异概率
    max_generations = 200  # 最大迭代次数
    lb, ub = -1, 2      # x取值范围
    
    # 初始化
    population = init_population(pop_size, chrom_length)
    best_fitness_history = []
    avg_fitness_history = []
    best_individual_history = []  # 记录每代最佳个体
    
    # 记录全局最优解
    global_best_fitness = -np.inf
    global_best_individual = None
    global_best_x = None
    
    # 进化过程
    for generation in range(max_generations):
        # 解码并计算适应度
        x_values = [binary_to_float(ind, chrom_length, lb, ub) 
                   for ind in population]
        fitnesses = np.array([fitness_func(x) for x in x_values])
        
        # 记录统计信息
        best_fitness = np.max(fitnesses)
        avg_fitness = np.mean(fitnesses)
        best_fitness_history.append(best_fitness)
        avg_fitness_history.append(avg_fitness)
        
        # 找到当前最佳个体
        best_index = np.argmax(fitnesses)
        best_individual = population[best_index]
        best_individual_history.append(best_individual)
        
        # 更新全局最优
        if best_fitness > global_best_fitness:
            global_best_fitness = best_fitness
            global_best_individual = best_individual
            global_best_x = x_values[best_index]
        
        # 选择
        selected = selection(population, fitnesses)
        
        # 交叉
        new_population = []
        for i in range(0, pop_size, 2):
            child1, child2 = crossover(
                selected[i], selected[i+1], pc
            )
            new_population.extend([child1, child2])
        
        # 变异
        new_population = [mutation(ind, pm) for ind in new_population]
        
        # 精英保留策略：用上一代的最佳个体替换新一代的最差个体
        # 找到新种群中最差个体的索引
        new_x_values = [binary_to_float(ind, chrom_length, lb, ub) for ind in new_population]
        new_fitnesses = np.array([fitness_func(x) for x in new_x_values])
        worst_index = np.argmin(new_fitnesses)
        
        # 用上一代的最佳个体替换最差个体
        new_population[worst_index] = best_individual
        
        population = new_population
    
    # 最终结果（使用全局最优解）
    best_x = global_best_x
    best_fitness = global_best_fitness
    
    return best_x, best_fitness, best_fitness_history, avg_fitness_history, best_individual_history

# 多次运行获取稳定结果
def run_multiple_times(num_runs=10):
    best_results = []
    
    for i in range(num_runs):
        print(f"运行 {i+1}/{num_runs}...")
        best_x, best_fitness, _, _, _ = genetic_algorithm()
        best_results.append((best_x, best_fitness))
        print(f"  运行结果: x = {best_x:.6f}, f(x) = {best_fitness:.6f}")
    
    # 找到多次运行中的最佳结果
    best_run = max(best_results, key=lambda x: x[1])
    print(f"\n多次运行中的最佳解: x = {best_run[0]:.6f}, f(x) = {best_run[1]:.6f}")
    
    return best_results, best_run

# 运行算法并可视化结果
if __name__ == "__main__":
    # 多次运行获取稳定结果
    all_results, best_result = run_multiple_times(num_runs=10)
    
    # 单独运行一次进行可视化
    best_x, best_fitness, best_hist, avg_hist, best_individuals = genetic_algorithm()
    
    print(f"\n单次运行最优解: x = {best_x:.6f}")
    print(f"函数最大值: f(x) = {best_fitness:.6f}")
    
    # 创建三联图布局
    plt.figure(figsize=(15, 12))
    
    # 图1：函数曲线
    plt.subplot(2, 2, 1)
    x_vals = np.linspace(-1, 2, 1000)
    y_vals = fitness_func(x_vals)
    plt.plot(x_vals, y_vals, 'b-', linewidth=1.5)
    plt.plot(best_x, best_fitness, 'ro', markersize=8)
    
    # 标记已知极值点
    known_peaks = [-0.5, 0.0, 0.5, 1.0, 1.5, 2.0]
    for peak in known_peaks:
        plt.plot(peak, fitness_func(peak), 'gx', markersize=10)
    
    plt.title('函数优化: $f(x) = x + \sin(10\pi x) + 1.0$', fontsize=14)
    plt.xlabel('x值', fontsize=12)
    plt.ylabel('f(x)值', fontsize=12)
    plt.grid(True)
    plt.legend(['函数曲线', '找到的最优解', '已知极值点'], loc='best')
    
    # 图2：适应度变化曲线
    plt.subplot(2, 2, 2)
    generations = range(len(best_hist))
    plt.plot(generations, best_hist, 'g-', linewidth=2, label='最佳适应度')
    plt.plot(generations, avg_hist, 'b--', linewidth=2, label='平均适应度')
    plt.title('适应度进化过程', fontsize=14)
    plt.xlabel('进化代数', fontsize=12)
    plt.ylabel('适应度值', fontsize=12)
    plt.legend(fontsize=12)
    plt.grid(True)
    
    # 图3：多次运行结果分布
    plt.subplot(2, 2, 3)
    x_results = [res[0] for res in all_results]
    fitness_results = [res[1] for res in all_results]
    
    # 绘制散点图
    plt.scatter(x_results, fitness_results, c='r', s=80, alpha=0.7, label='运行结果')
    
    # 标记全局最优解位置
    global_optimum_x = 1.5
    global_optimum_fitness = fitness_func(global_optimum_x)
    plt.axvline(x=global_optimum_x, color='g', linestyle='--', linewidth=2, alpha=0.7, label='全局最优解')
    plt.axhline(y=global_optimum_fitness, color='g', linestyle='--', linewidth=2, alpha=0.7)
    
    plt.title('多次运行结果分布 (10次运行)', fontsize=14)
    plt.xlabel('x值', fontsize=12)
    plt.ylabel('f(x)值', fontsize=12)
    plt.grid(True)
    plt.legend(fontsize=12)
    
    # 调整布局
    plt.tight_layout()
    
    # 保存结果
    plt.savefig('ga_optimization_results.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # 输出最后5代的最佳个体
    print("\n单次运行中最后5代的最佳个体：")
    for i, ind in enumerate(best_individuals[-5:], start=len(best_individuals)-4):
        x_val = binary_to_float(ind, 22, -1, 2)
        fit_val = fitness_func(x_val)
        print(f"第 {i} 代: x={x_val:.6f}, f(x)={fit_val:.6f}")