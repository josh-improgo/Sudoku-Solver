import argparse
# import tkinter as tk
from tkinter import *

BOARDS = ['test', 'easy1', 'easy2', 'med1', 'med2', 'hard1', 'hard2']
BOARD_MARGIN = 40
CELL_SIZE = 50
HEIGHT = WIDTH = (2 * BOARD_MARGIN) + (CELL_SIZE * 9)
LINE_WIDTH = 4        

# x and y is equal to board margin for opposite sides plus the each cell

class SudokuError(Exception):
    pass

def parse_arguments():
    parser = argparse.ArgumentParser(description="Process a board in BOARDS list")
    parser.add_argument("--board",
                            help="Name of board in BOARDS list",
                            type=str,
                            choices=BOARDS,
                            required=True)
    args = parser.parse_args()
    return args.board
    # python FILE.py --board BOARD_NAME

class SudokuBoard(object):
    def __init__(self, board_file):
        self.board = self.__create_board(board_file)

    def __create_board(self, board_file):
        board = []
        for line in board_file:
            line = line.strip()

            if len(line) != 9:
                raise SudokuError("Sudoku puzzle must be 9x9")

            board.append([])

            for char in line:
                if not char.isdigit():
                    raise SudokuError("Sudoku puzzle must only contain numerical values")
                # append to latest list
                board[-1].append(int(char))

        if len(board) != 9:
            raise SudokuError("Sudoku puzzle must be 9x9!")
        return board

class SudokuGUI(Frame):
    def __init__(self, parent, game):
        # frame = Frame(root)
        # frame.pack()
        self.parent = parent
        self.game = game

        Frame.__init__(self, parent)

        self.__initGUI()
        
        
    def __initGUI(self):
        self.parent.title("Sudoku")
        # self.parent.geometry("{}x{}".format(WIDTH, HEIGHT+50))
        
        self.canvas = Canvas(self.parent, width=WIDTH, height=HEIGHT, bg="white")
        self.canvas.pack(fill=BOTH, side=TOP)

        clear_btn = Button(self.parent, text="Clear", command=self.__clear_answers)
        clear_btn.pack(fill=BOTH, side=BOTTOM)

        solve_btn = Button(self.parent, text="Solve", command=self.__solve)
        solve_btn.pack(fill=BOTH, side=BOTTOM)

        message_lbl = Label(self.parent, text="Playing...")
        message_lbl.pack(fill=BOTH, side=TOP)
        # for cursor
        self.row = -1
        self.col = -1

        self.__draw_grid()
        self.__draw_numbers()
        
        self.canvas.bind("<Button-1>", self.__click_cell)
        self.canvas.bind("<Key>", self.__key_pressed)
        
    def __draw_grid(self):
        for i in range(10):
            color = "#344861"# if i % 3 == 0 else "gray"
            
            # Vertical Lines
            x1 = BOARD_MARGIN + i * CELL_SIZE
            y1 = BOARD_MARGIN - LINE_WIDTH/2
            x2 = BOARD_MARGIN + i * CELL_SIZE
            y2 = HEIGHT - BOARD_MARGIN + LINE_WIDTH/2
            # print("x1: {}, y1: {}, x2: {}, y2: {},".format(x1, y1, x2, y2))
            self.canvas.create_line(x1, y1, x2, y2, fill=color)
            if (i%3 == 0):
                self.canvas.create_line(x1, y1, x2, y2, fill=color, width=LINE_WIDTH)
            else:
                self.canvas.create_line(x1, y1, x2, y2, fill=color)

            # Horizontal Lines
            x1 = BOARD_MARGIN - LINE_WIDTH/2
            y1 = BOARD_MARGIN + i * CELL_SIZE
            x2 = WIDTH - BOARD_MARGIN + LINE_WIDTH/2
            y2 = BOARD_MARGIN + i * CELL_SIZE
            if (i%3 == 0):
                self.canvas.create_line(x1, y1, x2, y2, fill=color, width=LINE_WIDTH)
            else:
                self.canvas.create_line(x1, y1, x2, y2, fill=color)
    
    def __draw_numbers(self):
        self.canvas.delete("numbers")
        verdana = ("Verdana", 16, "bold")
        for r in range(9):
            for c in range(9):
                num = self.game.puzzle[r][c]

                if num != 0:
                    # print(num)
                    x = BOARD_MARGIN + c * CELL_SIZE + CELL_SIZE/2
                    y = BOARD_MARGIN + r * CELL_SIZE + CELL_SIZE/2
                    initial_num = self.game.begin_game[r][c]
                    color = "#344861" if num == initial_num else "gray"
                    self.canvas.create_text(x, y, text=num, tags="numbers", fill=color, font=verdana)
                    # text.configure(font=("Verdana", 16, "bold"))

    def __click_cell(self, event):
        if self.game.game_over:
            return
        
        x, y = event.x, event.y
        if BOARD_MARGIN < x < WIDTH - BOARD_MARGIN and BOARD_MARGIN < y < HEIGHT - BOARD_MARGIN:
            self.canvas.focus_set()

            r, c = int((y - BOARD_MARGIN) / CELL_SIZE), int((x - BOARD_MARGIN) / CELL_SIZE)
            print(r, c)
            if (r, c) == (self.row, self.col):
                self.row, self.col = -1, -1
            elif self.game.puzzle[r][c] == 0:
                self.row, self.col = r, c

        self.__draw_cursor()

    def __draw_cursor(self):
        FILL = "#bbdefb"
        self.canvas.delete("cursor")
        if self.row >= 0 and self.col >= 0:
            x1 = BOARD_MARGIN + self.col * CELL_SIZE - 1 + LINE_WIDTH / 2 - 1
            y1 = BOARD_MARGIN + self.row * CELL_SIZE - 1 + LINE_WIDTH / 2 - 1
            x2 = BOARD_MARGIN + (self.col + 1) * CELL_SIZE - 1 + LINE_WIDTH / 2 - 1
            y2 = BOARD_MARGIN + (self.row + 1) * CELL_SIZE - 1 + LINE_WIDTH / 2 - 1
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=FILL, outline=FILL, tags="cursor")

    def __key_pressed(self, event):
        if self.game.game_over:
            return
        
        if self.row >= 0 and self.col >= 0 and event.char in "1234567890":
            self.game.puzzle[self.row][self.col] = int(event.char)

            # reset cursor
            self.col, self.row = -1, -1

            self.__draw_numbers()
            self.__draw_cursor()
    
    def __solve(self):
        self.canvas.delete("numbers")

        solvedBoard = self.game.puzzle
        Solver(solvedBoard).start()
        self.__draw_numbers()
        print("finished solving")

    def __clear_answers(self):
        self.game.start()
        self.__draw_numbers()
        print("finished clearing")

class Solver:
    def __init__(self, b):
        self.b = b
        print("PRINTING")

        print(self.b)
        # self.start()
        
    def start(self):
        self.solve()

    def __find_empty_cell(self):
        for i in range(len(self.b)):
            for j in range(len(self.b[i])):
                if self.b[i][j] == 0:
                    return  (i, j)

        return None

    def __check_row(self, num, pos):
        for i in range(len(self.b[0])):
            
            # if the cell in the row is equal to num and not the position we are currently in
            if self.b[pos[0]][i] == num and pos[1] != i:
                return False
        return True

    def __check_col(self, num, pos):
        for i in range(len(self.b[0])):
            if self.b[i][pos[1]] == num and pos[0] != i:
                return False
        return True

    def __check_subgrid(self, num, pos):
        startRowPos = pos[0]//3 * 3
        endRowPos = startRowPos + 2
        startColPos = pos[1]//3 * 3
        endColPos = startColPos + 2
        # print("startRowPos: {}\nendRowPos: {}\nstartColPos: {}\nendColPos: {}\n".format(startRowPos, endRowPos, startColPos, endColPos))
        for i in range(startRowPos, endRowPos+1):
            for j in range(startColPos, endColPos+1):
                # print("[{}][{}]".format(i, j))
                if self.b[i][j] == num and (i, j) != pos:
                    return False
        return True

    def __valid(self, num, pos):
        # check row constraints
        # check columns
        # check subgrids
        if self.__check_row(num, pos) and self.__check_col(num, pos) and self.__check_subgrid(num, pos):
            return True

    def solve(self):
        empty_cell = self.__find_empty_cell()
        if not empty_cell: # if there are no more empty cells, the board is solved (base case)
            return True
        else:
            row, col = empty_cell
        
        for i in range(1, 10):
            if self.__valid(i, (row,col)):
                self.b[row][col] = i

                if self.solve():
                    return True

                self.b[row][col] = 0
        # print("False")
        return False

    # add SOLVE WITH STEPS
class Sudoku(object):
    def __init__(self, sudoku_file):
        self.sudoku_file = sudoku_file
        self.begin_game = SudokuBoard(sudoku_file).board
        self.start()
    
    def start(self):
        self.puzzle = []
        self.game_over = False
        for r in range(9):
            self.puzzle.append([])
            for c in range(9):
                self.puzzle[r].append(self.begin_game[r][c])

name = parse_arguments()
print(name)

with open("sudoku_board_files\%s.txt"%name, 'r') as sudoku_file:


    root = Tk()
    game = Sudoku(sudoku_file)
    gui = SudokuGUI(root, game)
    gui.mainloop()
