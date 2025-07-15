import tkinter as tk
import maze as mz

if __name__ == '__main__':
    n = int(input('生成的迷宫大小为（奇数）：'))

    root = tk.Tk()
    root.title('迷宫生成器')
    root.geometry('900x900')

    tk.Label(root, text = "迷宫生成器", height = 2, width=20, font = ('', 20)).pack()
    mazeData = mz.MazeData (n, n) #设置迷宫大小为n*n
    mazeWidget = mz.MazeWidget(root, mazeData)
    mazeWidget.show()

    root.mainloop()
