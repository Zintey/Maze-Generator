import tkinter as tk
import random

class Command:
    def execute(self):
        pass
    def undo(self):
        pass

class PrintMazeCommand(Command):
    def __init__(self, mazeData, x, y, val):
        self.cmdX = x
        self.cmdY = y
        self.cmdMazeData = mazeData
        self.valBefore = self.cmdMazeData.get(self.cmdX, self.cmdY)
        self.val = val

    def execute(self):
        self.cmdMazeData.set(self.cmdX, self.cmdY, self.val)

    def undo(self):
        self.cmdMazeData.set(self.cmdX, self.cmdY, self.valBefore)

class ResetMazeCommand(Command):
    def __init__(self, mazeData):
        self.cmdMazeData = mazeData
        self.dataCopy = mazeData.data
        self.startposCopy = mazeData.startpos
        self.endposCopy = mazeData.endpos

    def execute(self):
        self.cmdMazeData.regenerate_maze()

    def undo(self):
        self.cmdMazeData.data = self.dataCopy
        self.cmdMazeData.startpos = self.startposCopy
        self.cmdMazeData.endpos = self.endposCopy

class MazeData :
    def __init__(self, Row = 11, Col = 11):
        self.generate_maze(Row, Col)

    def generate_maze(self, Row = 11, Col = 11):
        """
        随机生成行列数为row col的迷宫数据,并存储在self.data内
        """

        self.row = int(Row)
        self.col = int(Col)

        def get_random_pos(n, m):
            x = random.randint(0, n - 1)
            y = random.choice([x for x in range(x % 2, m, 2)])
            return (x, y)
        #得到随机的不重叠的起点和终点
        self.startpos = get_random_pos(self.row, self.col)
        self.endpos = get_random_pos(self.row, self.col) 
        while self.startpos == self.endpos:
            self.endpos = get_random_pos(self.row, self.col)

        #通过dfs算法生成随机迷宫数据
        self.data = [[1 for j in range(self.col)] for j in range(self.row)]
        self.set(self.startpos[0], self.startpos[1], 2)

        stack = [self.startpos]
        while stack:
            x, y = stack[-1]
            npos = [(x + dir[0], y + dir[1]) 
                    for dir in [(-2, 0), (0, 2), (2, 0), (0, -2)] 
                    if self.is_in_maze(x + dir[0], y + dir[1]) and self.get(x + dir[0], y + dir[1]) == 1] # 得到四个方向还未连通的点
            if npos:
                nx, ny = random.choice(npos)
                self.set(nx, ny, 0)
                self.set((x + nx) // 2, (y + ny) // 2, 0)
                if (nx,ny) != self.endpos:
                    stack.append((nx, ny))
            else:
                stack.pop()
        self.set(self.endpos[0], self.endpos[1], 3)

    def regenerate_maze(self):
        """
        重新生成该迷宫数据
        """
        self.generate_maze(self.row, self.col)

    def get(self, x, y):
        if self.is_in_maze(x, y):
            return self.data[x][y]
        print(f"Error in MazeData.get(self, x:{x}, y:{y})")
        return -1

    def set(self, x, y, val):
        if self.is_in_maze(x, y):
            self.data[x][y] = val
        else:
            print(f"Error in MazeData.set(self, x:{x}, y:{y}, val:{val}), this maze row:{self.row} col:{self.col}")

    def is_in_maze(self, cx, cy):
        return not(cx < 0 or cy < 0 or cx >= self.row or cy >= self.col)

    def is_wall(self, cx, cy):
        return self.data[cx][cy] == 1

    def get_maze_solution(self):
        """
        计算迷宫的解
        若存在解,则将将最短路的路径在self.data中标记为负数,并返回最短路所需的步数
        若无解,则返回-1
        """
        for i in range(self.row):
            for j in range(self.col):
                if (self.get(i, j) <= -1):
                    self.set(i, j, 0) #将之前的最短路路径消除
        
        # 用bfs算法计算最短路径,路径存储于ans
        vis = [[0 for j in range(self.col)] for i in range(self.row)]
        ans = {}
        haveAns = False
        
        queue = [self.startpos]
        
        while queue:
            x, y = queue.pop(0)
            if vis[x][y]:
                continue
            vis[x][y] = 1
            
            for dx, dy in [(-1, 0), (0, 1), (1, 0), (0, -1)]:
                cx = x + dx
                cy = y + dy
                
                if self.is_in_maze(cx, cy) == False:
                    continue
                if self.is_wall(cx, cy):
                    continue
                
                if (vis[cx][cy] == 1):
                    continue
                
                queue.append((cx, cy))
                ans[(cx, cy)] = (x, y)
                if (cx, cy) == self.endpos:
                    haveAns = (x, y)
                    break
        
        if (haveAns == False):
            print("No Solution")
            return -1
        else :
            #处理路径细节
            val = {(0, 1) : -4, (0, -1) : -3, (1, 0) : -2, (-1, 0) : -1}
            cnt = 1
            pos = haveAns
            dir = (self.endpos[0] - pos[0], self.endpos[1] - pos[1])
            self.set(pos[0], pos[1], val[dir])
            while(pos in ans):
                cnt += 1
                dir = (pos[0] - ans[pos][0], pos[1] - ans[pos][1])
                pos = ans[pos]
                if pos != self.startpos:
                    self.set(pos[0], pos[1], val[dir])
            return cnt

    def export(self):
        """
        将self.data导出到out.txt中
        """
        with open('out.txt','w') as file:
            for i in range(self.row):
                for j in range(self.col):
                    num = self.get(i, j)
                    num = max(0, num)
                    file.write(str(num))
                    file.write(' ')
                file.write('\n')

class MazeWidget:
    config_Widget = {0 : {"bg":"white", "text":" "},
                     1 : {"bg":"black", "text":" "},
                     2 : {"bg":"green", "text":"🚩"},
                     3 : {"bg":"red", "text":"🚩"},
                     -1 : {"bg":"yellow", "text":"↑"},
                     -2 : {"bg":"yellow", "text":"↓"},
                     -3 : {"bg":"yellow", "text":"←"},
                     -4 : {"bg":"yellow", "text":"→"}} #方便配置显示的图案和颜色

    def __init__(self, root, mazeData):

        self.mazeFrame = tk.Frame(master=root, bg="black", bd=10)
        self.mazeData = mazeData

        self.showFrame = tk.Frame(master=root, bg="white", bd=20)
        self.showFrame.pack()

        self.cntText = tk.Label(master=self.showFrame, text="该迷宫没有通路！",font=("Arial", 15), width=30,height=3)
        self.cntText.pack()

        self.resetFrame = tk.Frame(master=self.showFrame, bg="white", bd=20)
        self.resetFrame.pack()

        tk.Button(master=self.resetFrame, text="重新生成",font=("Arial", 10), width=10,height=2, command=self.resetMaze).grid(row=0,column=1)

        self.isShowAnsRoad = 0
        def set_isShowAnsRoad():
            self.isShowAnsRoad = 1 - self.isShowAnsRoad
            self.update()
        tk.Checkbutton(master=self.resetFrame, text="显示路径",font=("Arial", 10), width=10,height=2,command=set_isShowAnsRoad).grid(row=0,column=2)

        tk.Button(master=self.resetFrame, text="导出",font=("Arial", 10), width=4,height=2, command=self.mazeData.export).grid(row=0,column=3)
        self.root = root
        self.mazeButtonArr = []
        self.cmdStack = [] #操作指令栈
        self.undoCmdStack = [] #撤回操作指令栈
        
        self.fontsize = round(60 / (self.mazeData.row + self.mazeData.col) * 6) #通过迷宫大小设置字体大小
        for i in range(self.mazeData.row):
            rowButton = []
            for j in range(self.mazeData.col):
                bt = tk.Button(self.mazeFrame,**self.config_Widget[self.mazeData.get(i, j)],font=("Arial", self.fontsize), width=2,height=1,padx=0,pady=0)
                bt.config(command=lambda x=i, y=j: self.click(x, y)) #注册点击操作
                rowButton.append(bt)
                rowButton[j].grid(row = i, column = j)

            self.mazeButtonArr.append(rowButton)
        self.update()

        self.mazeFrame.bind("<Control-z>", self.undoCmd) #注册撤回操作
        self.mazeFrame.bind("<Control-y>", self.restoreCmd) #注册恢复操作
        self.mazeFrame.focus_set() #设置焦点,使撤回和恢复操作生效

    def show(self):
        self.mazeFrame.pack()

    def click(self, x, y):
        """
            点击格子时,
            格子是墙时,变为道路
            不是墙时,变为墙
        """
        self.undoCmdStack = [] #将恢复操作列表清空
        self.mazeFrame.focus_set() #设置焦点,使撤回和恢复操作生效
        
        if self.mazeData.get(x, y) == 1:
            cmd = PrintMazeCommand(self.mazeData,x, y, 0)
            cmd.execute()
            self.cmdStack.append(cmd)
        else:
            cmd = PrintMazeCommand(self.mazeData,x, y, 1)
            cmd.execute()
            self.cmdStack.append(cmd)

        self.update()

    def undoCmd(self,event):
        """
        撤回操作
        """
        if self.cmdStack:
            cmd = self.cmdStack.pop()
            cmd.undo()
            self.undoCmdStack.append(cmd)
            self.update()

    def restoreCmd(self,event):
        """
        恢复操作
        """
        if self.undoCmdStack:
            cmd = self.undoCmdStack.pop()
            cmd.execute()
            self.cmdStack.append(cmd)
            self.update()

    def resetMaze(self):
        """
        重置迷宫操作
        """
        cmd = ResetMazeCommand(self.mazeData)
        cmd.execute()
        self.cmdStack.append(cmd)
        self.update()

    def update(self):
        """
        更新迷宫的显示状态
        """
        cnt = self.mazeData.get_maze_solution()
        if cnt == -1:
            self.cntText["text"] = "该迷宫没有解！"
        else:
            if self.isShowAnsRoad == 0:
                self.cntText["text"] = f"该迷宫有解！"
            else:
                self.cntText["text"] = f"最短路需要{cnt}步"
        for i in range(self.mazeData.row):
            for j in range(self.mazeData.col):
                index = self.mazeData.get(i, j)
                if self.isShowAnsRoad == 0:
                    index = max(index, 0)
                self.mazeButtonArr[i][j].config(**self.config_Widget[index])
