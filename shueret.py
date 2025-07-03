import tkinter as tk
import random
import time

class SchulteGrid:
    def __init__(self, root, size=5):
        self.root = root
        self.size = size  # 方格大小 (size x size)
        self.cell_size = 60  # 每个格子的大小
        self.buttons = []
        self.current_number = 1
        self.start_time = 0
        self.elapsed_time = 0
        self.game_active = False
        
        # 设置窗口
        self.root.title("舒尔特方格")
        self.setup_ui()
        
    def setup_ui(self):
        # 控制面板
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)
        
        self.size_var = tk.IntVar(value=self.size)
        size_label = tk.Label(control_frame, text="方格大小:")
        size_label.pack(side=tk.LEFT, padx=5)
        
        size_options = [2, 3, 4, 5, 6, 7, 8, 9, 10]
        size_menu = tk.OptionMenu(control_frame, self.size_var, *size_options)
        size_menu.pack(side=tk.LEFT, padx=5)
        
        start_button = tk.Button(control_frame, text="开始游戏", command=self.start_game)
        start_button.pack(side=tk.LEFT, padx=5)
        
        self.time_label = tk.Label(control_frame, text="用时: 0.00秒")
        self.time_label.pack(side=tk.LEFT, padx=10)
        
        # 游戏区域
        self.game_frame = tk.Frame(self.root)
        self.game_frame.pack(pady=10)
        
    def start_game(self):
        # 清除旧游戏
        for widget in self.game_frame.winfo_children():
            widget.destroy()
        self.buttons.clear()
        
        # 获取新设置
        self.size = self.size_var.get()
        self.current_number = 1
        self.game_active = True
        self.start_time = time.time()
        self.update_time()
        
        # 生成数字序列并打乱
        numbers = list(range(1, self.size**2 + 1))
        random.shuffle(numbers)
        
        # 创建按钮网格
        for i in range(self.size):
            for j in range(self.size):
                index = i * self.size + j
                num = numbers[index]
                btn = tk.Button(
                    self.game_frame,
                    text=str(num),
                    width=4,
                    height=2,
                    font=('Arial', 14),
                    command=lambda n=num: self.on_click(n)
                )
                btn.grid(row=i, column=j, padx=2, pady=2)
                self.buttons.append(btn)
    
    def on_click(self, number):
        if not self.game_active:
            return
            
        if number == self.current_number:
            # 正确点击
            for btn in self.buttons:
                if btn['text'] == str(number):
                    btn.config(state=tk.DISABLED, relief=tk.SUNKEN)
                    break
            
            self.current_number += 1
            
            # 检查游戏是否结束
            if self.current_number > self.size**2:
                self.game_active = False
                self.elapsed_time = time.time() - self.start_time
                self.time_label.config(text=f"完成! 用时: {self.elapsed_time:.2f}秒")
                
                # 显示祝贺信息
                result_label = tk.Label(
                    self.game_frame,
                    text=f"恭喜完成!\n用时: {self.elapsed_time:.2f}秒",
                    font=('Arial', 14),
                    fg='green'
                )
                result_label.grid(row=self.size//2, columnspan=self.size)
    
    def update_time(self):
        if self.game_active:
            self.elapsed_time = time.time() - self.start_time
            self.time_label.config(text=f"用时: {self.elapsed_time:.2f}秒")
            self.root.after(100, self.update_time)

if __name__ == "__main__":
    root = tk.Tk()
    game = SchulteGrid(root)
    root.mainloop()