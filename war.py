import pygame
import sys
import random
import math
from pygame.locals import *

# 初始化pygame
pygame.init()

# 游戏常量
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
TILE_SIZE = 40  # 增大格子尺寸
GRID_WIDTH = SCREEN_WIDTH // TILE_SIZE  # 25格
GRID_HEIGHT = (SCREEN_HEIGHT - 100) // TILE_SIZE  # 17格（下方留100像素用于信息面板）

# 尝试加载中文字体
try:
    # 尝试常见的中文字体
    FONT = pygame.font.SysFont("SimHei", 20)
    LARGE_FONT = pygame.font.SysFont("SimHei", 30)
    SMALL_FONT = pygame.font.SysFont("SimHei", 18)
except:
    # 回退到默认字体
    FONT = pygame.font.SysFont(None, 20)
    LARGE_FONT = pygame.font.SysFont(None, 30)
    SMALL_FONT = pygame.font.SysFont(None, 18)

# 颜色
BACKGROUND = (30, 30, 50)
GRID_COLOR = (60, 60, 80)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 80, 80)
GREEN = (80, 255, 80)
BLUE = (80, 150, 255)
YELLOW = (255, 255, 80)
PURPLE = (200, 80, 255)
CYAN = (80, 255, 255)
ORANGE = (255, 165, 0)
PINK = (255, 105, 180)
COLORS = [RED, BLUE, YELLOW, PURPLE, CYAN, ORANGE, PINK]  # 增加更多颜色
HIGHLIGHT = (255, 255, 255, 100)
NEUTRAL_COLOR = (100, 100, 100)  # 中立领土颜色

class Country:
    def __init__(self, color, name, is_player=False):
        self.color = color
        self.name = name
        self.is_player = is_player
        self.current_territory = 0  # 当前拥有的领土数
        self.total_territory = 0    # 总共占领过的领土数（包括失去的）
        self.troops = []  # 存储士兵组的位置坐标
        self.next_reward = 3
        self.defeated = False
    
    def get_troop_count(self):
        """计算国家总兵力（士兵组数量）"""
        return len(self.troops)
    
    def add_territory(self, game):
        """增加领土并检查是否应生成新士兵组"""
        # 每新占领3块领土获得一个新的士兵组（基于总共占领过的领土数）
        if self.total_territory >= self.next_reward:
            # 更新奖励阈值
            self.next_reward += 3
            
            # 在随机领土上生成新士兵组
            if self.troops:
                # 收集所有安全的领土位置（仅限己方领土且无士兵重叠）
                safe_positions = []
                for y in range(GRID_HEIGHT):
                    for x in range(GRID_WIDTH):
                        if game.grid[y][x] and game.grid[y][x]['country'] == self:
                            # 确保不在他国领土上
                            is_safe = True
                            for dx, dy in [(0,0), (0,-1), (0,1), (-1,0), (1,0)]:
                                nx, ny = x + dx, y + dy
                                if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                                    if game.grid[ny][nx] and game.grid[ny][nx]['country'] != self:
                                        is_safe = False
                                        break
                            
                            if is_safe:
                                safe_positions.append((x, y))
                
                if safe_positions:
                    # 随机选择一个安全位置
                    x, y = random.choice(safe_positions)
                    
                    # 创建新士兵组
                    new_troop = [x, y]
                    
                    # 添加到国家士兵列表
                    self.troops.append(new_troop)
                    
                    # 添加到网格
                    game.grid[y][x]['troops'].append(new_troop)
                    return True
        return False

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("war")
        self.clock = pygame.time.Clock()
        
        # 创建国家
        self.countries = []
        self.player_country = Country(GREEN, "玩家", True)
        self.countries.append(self.player_country)
        
        # 创建电脑国家 (使用不同颜色)
        ai_names = ["红国", "蓝国", "黄国", "紫国", "青国"]
        for i in range(5):  # 创建5个电脑国家
            color_idx = i % len(COLORS)
            self.countries.append(Country(COLORS[color_idx], ai_names[i]))
        
        # 初始化网格
        self.grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.selected_tile = None  # 改为选择整个方格
        self.game_over = False
        self.winner = None
        self.turn_count = 0  # 回合计数器
        
        # 初始化领土和士兵
        self.initialize_game()
    
    def initialize_game(self):
        # 为每个国家分配初始领土
        positions = []
        for i in range(len(self.countries)):
            while True:
                x = random.randint(2, GRID_WIDTH - 3)
                y = random.randint(2, GRID_HEIGHT - 3)
                # 确保初始位置不重叠且有一定间距
                too_close = False
                for px, py in positions:
                    if abs(px - x) < 4 and abs(py - y) < 4:
                        too_close = True
                        break
                if not too_close and (x, y) not in positions:
                    positions.append((x, y))
                    self.grid[y][x] = {
                        'country': self.countries[i],
                        'troops': [[x, y]]  # 初始士兵组
                    }
                    self.countries[i].current_territory = 1
                    self.countries[i].total_territory = 1
                    self.countries[i].troops = [[x, y]]
                    self.countries[i].next_reward = 3
                    break
    
    def draw_grid(self):
        # 绘制网格背景
        self.screen.fill(BACKGROUND)
        
        # 绘制网格线
        for x in range(0, SCREEN_WIDTH, TILE_SIZE):
            pygame.draw.line(self.screen, GRID_COLOR, (x, 0), (x, GRID_HEIGHT * TILE_SIZE))
        for y in range(0, GRID_HEIGHT * TILE_SIZE, TILE_SIZE):
            pygame.draw.line(self.screen, GRID_COLOR, (0, y), (SCREEN_WIDTH, y))
        
        # 绘制领土和士兵
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                tile = self.grid[y][x]
                if tile:
                    # 确保国家对象存在
                    if tile['country']:
                        rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                        pygame.draw.rect(self.screen, tile['country'].color, rect)
                        
                        # 绘制士兵组
                        troop_count = len(tile['troops'])
                        if troop_count > 0:
                            pygame.draw.circle(self.screen, WHITE, 
                                            (x * TILE_SIZE + TILE_SIZE//2, y * TILE_SIZE + TILE_SIZE//2),
                                            TILE_SIZE//3)
                            text = FONT.render(str(troop_count), True, BLACK)
                            text_rect = text.get_rect(center=(x * TILE_SIZE + TILE_SIZE//2, y * TILE_SIZE + TILE_SIZE//2))
                            self.screen.blit(text, text_rect)
                    else:
                        # 绘制中立领土
                        rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                        pygame.draw.rect(self.screen, NEUTRAL_COLOR, rect)
        
        # 绘制选中的方格
        if self.selected_tile:
            x, y = self.selected_tile
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(self.screen, HIGHLIGHT, rect, 3)
            
            # 绘制可移动范围 (距离2格)
            for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0),  # 相邻格子
                          (0, -2), (0, 2), (-2, 0), (2, 0)]:  # 距离2格
                nx, ny = x + dx, y + dy
                if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                    rect = pygame.Rect(nx * TILE_SIZE, ny * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    pygame.draw.rect(self.screen, (255, 255, 255, 100), rect, 2)
        
        # 绘制信息面板
        info_panel_y = GRID_HEIGHT * TILE_SIZE
        info_panel_height = SCREEN_HEIGHT - info_panel_y
        pygame.draw.rect(self.screen, (40, 40, 60), (0, info_panel_y, SCREEN_WIDTH, info_panel_height))
        pygame.draw.line(self.screen, WHITE, (0, info_panel_y), (SCREEN_WIDTH, info_panel_y), 2)
        
        # 绘制玩家信息
        player_text = LARGE_FONT.render(f"玩家: {self.player_country.current_territory}领土 {self.player_country.get_troop_count()}兵力", True, GREEN)
        self.screen.blit(player_text, (20, info_panel_y + 10))
        
        # 绘制电脑国家信息
        ai_info = []
        for country in self.countries:
            if not country.is_player and not country.defeated:
                # 显示国家名、领土数和兵力
                ai_info.append(f"{country.name}: {country.current_territory}领土 {country.get_troop_count()}兵力")
        
        # 第一列
        if len(ai_info) > 0:
            ai_text1 = SMALL_FONT.render("电脑国家: " + ", ".join(ai_info[:3]), True, YELLOW)
            self.screen.blit(ai_text1, (20, info_panel_y + 45))
        
        # 第二列
        if len(ai_info) > 3:
            ai_text2 = SMALL_FONT.render(", ".join(ai_info[3:]), True, YELLOW)
            self.screen.blit(ai_text2, (20, info_panel_y + 70))
        
        # 回合计数
        turn_text = SMALL_FONT.render(f"回合: {self.turn_count}", True, CYAN)
        self.screen.blit(turn_text, (500, info_panel_y + 10))
        
        # 绘制游戏结束信息
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))
            
            if self.winner.is_player:
                text = LARGE_FONT.render("恭喜！你赢得了战争！", True, GREEN)
            else:
                text = LARGE_FONT.render(f"{self.winner.name}赢得了战争！", True, self.winner.color)
            
            restart = FONT.render("按R键重新开始游戏", True, WHITE)
            
            self.screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2 - 50))
            self.screen.blit(restart, (SCREEN_WIDTH//2 - restart.get_width()//2, SCREEN_HEIGHT//2 + 20))
    
    def handle_click(self, pos):
        if self.game_over:
            return
        
        grid_x = pos[0] // TILE_SIZE
        grid_y = pos[1] // TILE_SIZE
        
        # 确保点击在网格范围内
        if not (0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT):
            return
        
        # 选择整个方格
        if self.selected_tile is None:
            tile = self.grid[grid_y][grid_x]
            if tile and tile['country'] == self.player_country:
                # 检查该位置是否有玩家士兵组
                if tile['troops']:
                    self.selected_tile = (grid_x, grid_y)
        else:
            # 移动士兵组
            selected_x, selected_y = self.selected_tile
            
            # 检查是否在移动范围内 (曼哈顿距离 <= 2 且在同一行或列)
            dx = abs(grid_x - selected_x)
            dy = abs(grid_y - selected_y)
            
            # 只能水平或垂直移动，距离1-2格
            if ((dx == 1 or dx == 2) and dy == 0) or ((dy == 1 or dy == 2) and dx == 0):
                self.move_troops(selected_x, selected_y, grid_x, grid_y)
            
            self.selected_tile = None
    
    def move_troops(self, from_x, from_y, to_x, to_y):
        # 获取原方格信息
        from_tile = self.grid[from_y][from_x]
        if not from_tile or not from_tile['troops']:
            return
        
        # 获取要移动的所有士兵组
        moving_troops = from_tile['troops'][:]  # 复制列表
        moving_count = len(moving_troops)
        
        # 从原位置移除所有士兵组
        from_tile['troops'] = []
        for troop in moving_troops:
            if troop in self.player_country.troops:
                self.player_country.troops.remove(troop)
        
        # 更新士兵组位置
        for troop in moving_troops:
            troop[0] = to_x
            troop[1] = to_y
        
        # 添加到新位置
        to_tile = self.grid[to_y][to_x]
        
        if not to_tile:
            # 占领新领土
            self.grid[to_y][to_x] = {
                'country': self.player_country,
                'troops': moving_troops
            }
            self.player_country.current_territory += 1
            self.player_country.total_territory += 1
            self.player_country.troops.extend(moving_troops)
            # 检查是否应获得新士兵组（基于总占领领土数）
            self.player_country.add_territory(self)
        else:
            if to_tile['country'] == self.player_country:
                # 合并到友方领土
                to_tile['troops'].extend(moving_troops)
                self.player_country.troops.extend(moving_troops)
            else:
                # 与敌方发生战斗
                self.resolve_battle(to_x, to_y, moving_troops, moving_count)
        
        # 电脑回合
        self.ai_turn()
        self.turn_count += 1
        
        # 检查游戏是否结束
        self.check_game_over()
    
    def resolve_battle(self, x, y, attacking_troops, attacking_count):
        tile = self.grid[y][x]
        defending_country = tile['country']
        defending_troops = tile['troops']
        defending_count = len(defending_troops)
        
        # 计算战斗结果
        if attacking_count >= defending_count:
            # 攻击方胜利
            tile['country'] = self.player_country
            
            # 保留差值数量的士兵组
            remaining_attacking_troops = attacking_troops[:attacking_count - defending_count] if attacking_count > defending_count else []
            
            # 设置领土上的士兵组
            tile['troops'] = remaining_attacking_troops
            
            # 更新玩家士兵列表
            self.player_country.troops.extend(remaining_attacking_troops)
            
            # 领土变更
            self.player_country.current_territory += 1
            self.player_country.total_territory += 1
            if defending_country:
                defending_country.current_territory -= 1
                # 检查防御方是否被击败
                if defending_country.current_territory <= 0:
                    defending_country.defeated = True
                    # 移除所有该国家的领土
                    for y2 in range(GRID_HEIGHT):
                        for x2 in range(GRID_WIDTH):
                            tile2 = self.grid[y2][x2]
                            if tile2 and tile2['country'] == defending_country:
                                tile2['country'] = None
            
            # 检查是否应获得新士兵组（基于总占领领土数）
            self.player_country.add_territory(self)
        else:
            # 防御方胜利 - 保留y-x个士兵组
            # 移除所有进攻方士兵组
            for troop in attacking_troops:
                if troop in self.player_country.troops:
                    self.player_country.troops.remove(troop)
            
            # 计算防御方应保留的士兵组数量
            remaining_defending_count = defending_count - attacking_count
            
            # 随机保留防御方士兵组
            if remaining_defending_count > 0:
                # 随机选择要保留的士兵组
                remaining_troops = random.sample(defending_troops, remaining_defending_count)
                tile['troops'] = remaining_troops
                
                # 更新防御方国家士兵列表
                if defending_country:
                    defending_country.troops = [t for t in defending_country.troops if t in remaining_troops]
            else:
                # 如果防御方士兵全部被消灭
                tile['troops'] = []
                tile['country'] = None
                if defending_country:
                    defending_country.current_territory -= 1
                    if defending_country.current_territory <= 0:
                        defending_country.defeated = True
                        # 移除所有该国家的领土
                        for y2 in range(GRID_HEIGHT):
                            for x2 in range(GRID_WIDTH):
                                t = self.grid[y2][x2]
                                if t and t['country'] == defending_country:
                                    t['country'] = None
    
    def ai_turn(self):
        for country in self.countries:
            if country.is_player or country.defeated:
                continue
            
            # 收集所有可能的移动
            possible_moves = []
            
            # 收集所有边境格子（与敌方或空白相邻的格子）
            border_tiles = []
            for y in range(GRID_HEIGHT):
                for x in range(GRID_WIDTH):
                    tile = self.grid[y][x]
                    if tile and tile['country'] == country and tile['troops']:
                        # 检查是否在边境
                        is_border = False
                        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                                neighbor = self.grid[ny][nx]
                                if not neighbor or (neighbor['country'] and neighbor['country'] != country):
                                    is_border = True
                                    break
                        
                        if is_border:
                            border_tiles.append((x, y))
            
            if not border_tiles:
                # 如果没有边境格子，使用所有有士兵的格子
                for y in range(GRID_HEIGHT):
                    for x in range(GRID_WIDTH):
                        tile = self.grid[y][x]
                        if tile and tile['country'] == country and tile['troops']:
                            border_tiles.append((x, y))
            
            # 尝试每个边境格子
            random.shuffle(border_tiles)
            moved = False
            
            for x, y in border_tiles:
                tile = self.grid[y][x]
                # 检查该格子是否还有士兵（可能在之前的移动中已被移动）
                if not tile or not tile['troops'] or tile['country'] != country:
                    continue
                
                # 收集可能的移动目标
                targets = []
                
                # 检查所有可能的方向（1-2格距离）
                for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0), (0, -2), (0, 2), (-2, 0), (2, 0)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                        targets.append((nx, ny))
                
                # 随机打乱目标顺序
                random.shuffle(targets)
                
                for tx, ty in targets:
                    # 获取目标格子
                    target_tile = self.grid[ty][tx]
                    
                    # 如果是空白格子，直接占领
                    if not target_tile:
                        self.ai_move(country, x, y, tx, ty)
                        moved = True
                        break
                    
                    # 如果是敌方格子，评估实力
                    if target_tile and target_tile['country'] and target_tile['country'] != country:
                        # 获取边境实力
                        my_strength = len(tile['troops'])
                        enemy_strength = len(target_tile['troops'])
                        
                        # 增强策略性 - 只在实力足够时进攻
                        if my_strength >= enemy_strength:
                            self.ai_move(country, x, y, tx, ty)
                            moved = True
                            break
                
                if moved:
                    # 添加延时，让玩家看到电脑操作
                    self.draw_grid()
                    pygame.display.flip()
                    pygame.time.delay(500)  # 0.5秒延时
                    break
    
    def ai_move(self, country, from_x, from_y, to_x, to_y):
        # 获取原方格信息
        from_tile = self.grid[from_y][from_x]
        if not from_tile or not from_tile['troops']:
            return
        
        # 获取要移动的所有士兵组
        moving_troops = from_tile['troops'][:]  # 复制列表
        moving_count = len(moving_troops)
        
        # 从原位置移除所有士兵组
        from_tile['troops'] = []
        for troop in moving_troops:
            if troop in country.troops:
                country.troops.remove(troop)
        
        # 更新士兵组位置
        for troop in moving_troops:
            troop[0] = to_x
            troop[1] = to_y
        
        # 添加到新位置
        to_tile = self.grid[to_y][to_x]
        
        if not to_tile:
            # 占领新领土
            self.grid[to_y][to_x] = {
                'country': country,
                'troops': moving_troops
            }
            country.current_territory += 1
            country.total_territory += 1
            country.troops.extend(moving_troops)
            # 检查是否应获得新士兵组（基于总占领领土数）
            country.add_territory(self)
        else:
            if to_tile['country'] == country:
                # 合并到友方领土
                to_tile['troops'].extend(moving_troops)
                country.troops.extend(moving_troops)
            else:
                # 与敌方发生战斗
                defending_country = to_tile['country'] if to_tile['country'] else None
                defending_troops = to_tile['troops']
                defending_count = len(defending_troops)
                
                if moving_count >= defending_count:
                    # 攻击方胜利
                    to_tile['country'] = country
                    
                    # 保留差值数量的士兵组
                    remaining_attacking_troops = moving_troops[:moving_count - defending_count] if moving_count > defending_count else []
                    
                    # 设置领土上的士兵组
                    to_tile['troops'] = remaining_attacking_troops
                    
                    # 更新国家士兵列表
                    country.troops.extend(remaining_attacking_troops)
                    
                    # 领土变更
                    country.current_territory += 1
                    country.total_territory += 1
                    if defending_country:
                        defending_country.current_territory -= 1
                        if defending_country.current_territory <= 0:
                            defending_country.defeated = True
                            # 移除所有该国家的领土
                            for y2 in range(GRID_HEIGHT):
                                for x2 in range(GRID_WIDTH):
                                    tile2 = self.grid[y2][x2]
                                    if tile2 and tile2['country'] == defending_country:
                                        tile2['country'] = None
                    
                    # 检查是否应获得新士兵组（基于总占领领土数）
                    country.add_territory(self)
                else:
                    # 防御方胜利 - 保留y-x个士兵组
                    # 移除所有进攻方士兵组
                    for troop in moving_troops:
                        if troop in country.troops:
                            country.troops.remove(troop)
                    
                    # 计算防御方应保留的士兵组数量
                    remaining_defending_count = defending_count - moving_count
                    
                    # 随机保留防御方士兵组
                    if remaining_defending_count > 0:
                        # 随机选择要保留的士兵组
                        remaining_troops = random.sample(defending_troops, remaining_defending_count)
                        to_tile['troops'] = remaining_troops
                        
                        # 更新防御方国家士兵列表
                        if defending_country:
                            defending_country.troops = [t for t in defending_country.troops if t in remaining_troops]
                    else:
                        # 如果防御方士兵全部被消灭
                        to_tile['troops'] = []
                        to_tile['country'] = None
                        if defending_country:
                            defending_country.current_territory -= 1
                            if defending_country.current_territory <= 0:
                                defending_country.defeated = True
                                # 移除所有该国家的领土
                                for y2 in range(GRID_HEIGHT):
                                    for x2 in range(GRID_WIDTH):
                                        t = self.grid[y2][x2]
                                        if t and t['country'] == defending_country:
                                            t['country'] = None
    
    def check_game_over(self):
        active_countries = [c for c in self.countries if not c.defeated]
        
        if len(active_countries) == 1:
            self.game_over = True
            self.winner = active_countries[0]
    
    def restart_game(self):
        # 重置游戏状态
        self.grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        for country in self.countries:
            country.current_territory = 0
            country.total_territory = 0
            country.troops = []
            country.next_reward = 3
            country.defeated = False
        
        self.selected_tile = None
        self.game_over = False
        self.winner = None
        self.turn_count = 0
        
        # 重新初始化游戏
        self.initialize_game()
    
    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == MOUSEBUTTONDOWN:
                    if event.button == 1:  # 左键点击
                        self.handle_click(event.pos)
                elif event.type == KEYDOWN:  # 修正此处：添加键盘事件处理
                    if event.key == K_r:  # 按R键重新开始
                        self.restart_game()
            
            self.draw_grid()
            pygame.display.flip()
            self.clock.tick(60)

if __name__ == "__main__":
    game = Game()
    game.run()
"""
这是一个使用python库编写的战略游戏，规则如下：
1.玩家控制一个属于自己的国家，而电脑控制数个国家，所有的国家之间都是敌对关系
2.战争在横纵向的网格上进行，每个国家最初只占1个方格，方格内有一组初始士兵，玩家通过鼠标选中并控制本国士兵占据周围的方格（一次最多移动2格），就能归为自己的领土，每个国家领土都用不同颜色的方格显示
3.每个国家每新占领3格领土，就能在自己的领土上重新生成一组士兵，不同组的士兵可以分别进行控制，且不同组士兵可以停留在同一方格上
4.若某一国家的士兵侵入已被其他任意国家标记的方格，则比较侵入的士兵组数a与该方格上的士兵组数b，计算x=a-b，若x>=0则该方格被划归为入侵国领土，并具有x组入侵国士兵；若x<0则该方格仍属于被入侵国领土，并具有-x组被入侵国士兵
5.电脑控制的每个国家也应具有入侵他国的能力
"""