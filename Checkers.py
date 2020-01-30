from kivy.uix.layout import Layout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.graphics import *
from kivy.app import App


class Square(ButtonBehavior, Widget):
    def __init__(self, pos, size, black, row, col):
        Widget.__init__(self)
        ButtonBehavior.__init__(self)
        self.black = black
        self.unit = None
        self.pos = pos
        self.size = size
        self.queen = False
        self.selected = False
        self.row = row
        self.col = col


class Board(Layout):
    def __init__(self):
        Layout.__init__(self)
        self.reset = Button(text="Restart Game")
        self.reset.pos = (Window.size[0] / 2 - self.reset.size[0] / 2, Window.size[1] / 4 - self.reset.size[1] / 2)
        self.reset.bind(on_press=self.reset_game)
        self.win_title = Label(color=(1, 93 / 255, 136/255))
        self.reset_game()

    def reset_game(self, touch=None):
        self.clear_widgets()
        self.squares = list()
        self.turn = "r"
        black = True
        self.selected = None
        self.toClear = None
        self.can_jump = None
        for i, y in enumerate(range(Window.size[1], 0 - 2 * int(Window.size[1] / 8), -int(Window.size[1] / 8))):
            self.squares.append(list())
            for j, x in enumerate(
                    range(-int(Window.size[0] / 8), Window.size[0] + int(Window.size[0] / 8), int(Window.size[0] / 8))):
                square = Square(pos=(x, y), size=(Window.size[0] / 8, Window.size[1] / 8), black=black, row=i, col=j)
                self.squares[i].append(square)
                if i not in [0, 9] and j not in [0, 9]:
                    with square.canvas:
                        if square.black:
                            Color(0, 0, 0)
                            black = False
                        else:
                            Color(1, 1, 1)
                            black = True
                        Rectangle(pos=(x, y), size=(Window.size[0] / 8, Window.size[1] / 8))
                        d = Window.size[1] / 8
                        if y < int(Window.size[1] / 4):
                            square.unit = "r"
                            Color(1, 0, 0)
                            Ellipse(pos=(x + Window.size[0] / 16 - d / 2, y), size=(d, d))
                        elif y >= int(Window.size[1] * 3 / 4):
                            square.unit = "b"
                            Color(0, 0, 1)
                            Ellipse(pos=(x + Window.size[0] / 16 - d / 2, y), size=(d, d))
                        square.bind(on_press=self.click)
                        self.add_widget(square)
            black = not black

    def win(self):
        for i in self.squares:
            for j in i:
                j.disabled = True
        self.add_widget(self.reset)
        if self.selected.unit == "r":
            self.win_title.text = "RED PLAYER WINS"
        else:
            self.win_title.text = "BLUE PLAYER WINS"
        self.win_title.pos = (Window.size[0] / 2 - self.win_title.size[0] / 2, Window.size[1] * 3 / 4 - self.win_title.size[1] / 2)
        self.add_widget(self.win_title)

    def click(self, touch):
        if touch == self.selected:
            touch.selected = False
            self.selected = None
            touch.canvas.clear()
            self.draw_square(touch)
        elif self.turn == touch.unit or touch == self.can_jump:
            if self.selected is not None:
                self.selected.selected = False
                self.selected.canvas.clear()
                self.draw_square(self.selected)
            self.selected = touch
            touch.selected = True
            touch.canvas.clear()
            self.draw_square(touch)
        elif self.selected is not None:
            if self.valid_move(touch):
                if self.toClear is not None:
                    self.toClear.unit = None
                    self.toClear.canvas.clear()
                    self.draw_square(self.toClear)
                    self.toClear = None
                if self.selected.unit == self.turn:
                    if self.turn == "r":
                        self.turn = "b"
                    else:
                        self.turn = "r"
                if (self.selected.unit == "r" and touch.row == 1) or (self.selected.unit == "b" and touch.row == 8):
                    self.selected.queen = True
                self.selected.selected = False
                touch.unit = self.selected.unit
                touch.queen = self.selected.queen
                winner = True
                for i in self.squares:
                    for j in i:
                        if self.selected.unit != j.unit is not None:
                            winner = False
                            break
                    if not winner:
                        break
                if winner:
                    self.win()
                self.selected.unit = None
                self.selected.queen = False
                self.selected.canvas.clear()
                self.draw_square(self.selected)
                self.selected = None
                self.draw_square(touch)

    def valid_move(self, square):
        if square.unit is None:
            if self.selected != self.can_jump:
                if self.can_jump is not None:
                    self.can_jump = None
                if self.selected.unit == "r":
                    if square.row == self.selected.row-1 and square.col in range(self.selected.col-1, self.selected.col+2):
                        return True
                else:
                    if square.row == self.selected.row+1 and square.col in range(self.selected.col-1, self.selected.col+2):
                        return True
            if (abs(square.row - self.selected.row) == 2 and abs(square.col - self.selected.col) == 2) or (abs(square.row - self.selected.row) == 2 and square.col - self.selected.col == 0) or (abs(square.col - self.selected.col) == 2 and square.row - self.selected.row == 0):
                if self.selected.unit != self.squares[int(self.selected.row + (square.row - self.selected.row) / 2)][int(self.selected.col + (square.col - self.selected.col) / 2)].unit is not None:
                    self.toClear = self.squares[int(self.selected.row + (square.row - self.selected.row) / 2)][int(self.selected.col + (square.col - self.selected.col) / 2)]
                    if self.check_jump(square):
                        self.can_jump = square
                    if self.can_jump == self.selected:
                        self.can_jump = None
                    return True
            if self.selected.queen:
                if abs(square.row - self.selected.row) == abs(square.col - self.selected.col) or square.row - self.selected.row == 0:
                    passed = False
                    for i in range(1, abs(square.col - self.selected.col)):
                        if i == 1:
                            if self.selected.unit != self.squares[square.row + i * ((square.row < self.selected.row)-(square.row > self.selected.row))][square.col + i * ((square.col < self.selected.col)-(square.col > self.selected.col))].unit is not None:
                                passed = True
                                self.toClear = self.squares[square.row + i * ((square.row < self.selected.row)-(square.row > self.selected.row))][square.col + i * ((square.col < self.selected.col)-(square.col > self.selected.col))]
                                if self.check_jump(square):
                                    self.can_jump = square
                                else:
                                    self.can_jump = None
                            elif self.selected.unit == self.squares[square.row + i * ((square.row < self.selected.row)-(square.row > self.selected.row))][square.col + i * ((square.col < self.selected.col)-(square.col > self.selected.col))].unit or self.selected == self.can_jump:
                                self.toClear = None
                                return False
                        elif self.squares[square.row + i * ((square.row < self.selected.row)-(square.row > self.selected.row))][square.col + i * ((square.col < self.selected.col)-(square.col > self.selected.col))].unit is not None:
                            self.toClear = None
                            return False
                    if passed or self.selected != self.can_jump:
                        return True
                elif square.col - self.selected.col == 0:
                    passed = False
                    for i in range(square.row + (square.row<self.selected.row)-(square.row>self.selected.row), self.selected.row, (square.row<self.selected.row)-(square.row>self.selected.row)):
                        if i == square.row + ((square.row<self.selected.row)-(square.row>self.selected.row)):
                            if self.selected.unit != self.squares[i][square.col].unit is not None:
                                passed = True
                                self.toClear = self.squares[i][square.col]
                                if self.check_jump(square):
                                    self.can_jump = square
                                else:
                                    self.can_jump = None
                            elif self.selected.unit == self.squares[i][square.col].unit or self.selected == self.can_jump:
                                self.toClear = None
                                return False
                        elif self.squares[i][square.col].unit is not None:
                            self.toClear = None
                            return False
                    if passed or self.selected != self.can_jump:
                        return True
        return False

    def check_jump(self, square):
        if square.queen:
            for i in range(1, 7):
                if square.row - i - 1 > 0 and square.col - i - 1 > 0:
                    if square.unit != self.squares[square.row - i][square.col - i] is not None:
                        if self.squares[square.row - i - 1][square.col - i - 1] is None:
                            return True
                if square.row - i - 1 > 0:
                    if square.unit != self.squares[square.row - i][square.col] is not None:
                        if self.squares[square.row - i - 1][square.col] is None:
                            return True
                if square.row - i - 1 > 0 and square.col + i + 1 < 9:
                    if square.unit != self.squares[square.row - i][square.col + i] is not None:
                        if self.squares[square.row - i - 1][square.col + i + 1] is None:
                            return True
                if square.col + i + 1 < 9:
                    if square.unit != self.squares[square.row][square.col + i] is not None:
                        if self.squares[square.row][square.col + i + 1] is None:
                            return True
                if square.row + i + 1 < 9 and square.col + i + 1 < 9:
                    if square.unit != self.squares[square.row + i][square.col + i] is not None:
                        if self.squares[square.row + i + 1][square.col + i + 1] is None:
                            return True
                if square.row + i + 1 < 9:
                    if square.unit != self.squares[square.row + i][square.col] is not None:
                        if self.squares[square.row + i + 1][square.col] is None:
                            return True
                if square.row + i + 1 < 9 and square.col - i - 1 > 0:
                    if square.unit != self.squares[square.row + i][square.col - i] is not None:
                        if self.squares[square.row + i + 1][square.col - i - 1] is None:
                            return True
                if square.col - i - 1 > 0:
                    if square.unit != self.squares[square.row][square.col - i] is not None:
                        if self.squares[square.row][square.col - i - 1] is None:
                            return True
            return False
        else:
            for i in range(square.row - 1, square.row + 2):
                for j in range(square.col - 1, square.col + 2):
                    if (i != square.row or j != square.col) and (i != int(self.selected.row + (square.row - self.selected.row) / 2) or j != int(self.selected.col + (square.col - self.selected.col) / 2)) and self.selected.unit != self.squares[i][j].unit is not None and self.squares[square.row + (i - square.row)*2][square.col + (j - square.col)*2].unit is None and square.row + (i - square.row)*2 not in [0, 9] and square.col + (j - square.col)*2 not in [0, 9]:
                        return True
            return False

    def draw_square(self, square):
        with square.canvas:
            if square.black:
                Color(0, 0, 0)
                black = False
            else:
                Color(1, 1, 1)
                black = True
            Rectangle(pos=square.pos, size=square.size)
            d = square.size[1]
            if square.unit == "r":
                if square.selected:
                    Color(1, 1, 0)
                else:
                    Color(1, 0, 0)
                Ellipse(pos=(square.pos[0] + square.size[0] / 2 - d / 2, square.pos[1]), size=(d, d))
            elif square.unit == "b":
                if square.selected:
                    Color(0, 1, 1)
                else:
                    Color(0, 0, 1)
                Ellipse(pos=(square.pos[0] + square.size[0] / 2 - d / 2, square.pos[1]), size=(d, d))
            if square.queen:
                if square.black:
                    Color(0, 0, 0)
                    black = False
                else:
                    Color(1, 1, 1)
                    black = True
                Ellipse(pos=(square.pos[0] + square.size[0] / 2 - d / 4, square.pos[1] + square.size[1] / 2 - d / 4), size=(d / 2, d / 2))


class Game(App):
    def build(self):
        self.title = "ChEcKeRs"
        return Board()


Game().run()
