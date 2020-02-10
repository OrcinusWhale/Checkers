from kivy.uix.layout import Layout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.graphics import *
from kivy.app import App


class Square(ButtonBehavior, Widget):
    def __init__(self, pos, size, black, row, col):
        Widget.__init__(self)
        ButtonBehavior.__init__(self)
        self.black = black  # The square's color
        self.unit = None  # The unit that is on the board (None/'b'/'r')
        self.pos = pos  # Position on screen (x, y)
        self.size = size  # Size (height, width)
        self.queen = False  # Whether the unit on the square is a queen
        self.selected = False  # If the square is selected
        self.row = row  # Row of square on board
        self.col = col  # Column of square on board


class Board(Layout):
    def __init__(self):
        Layout.__init__(self)
        #  Button that'll allow to reset the game at the end
        self.reset = Button(text="Restart Game", size=(Window.size[0] / 4, Window.size[1] / 4))
        self.reset.pos = (Window.size[0] / 2 - self.reset.size[0] / 2, Window.size[1] / 2 - self.reset.size[1] / 2)
        self.reset.bind(on_press=self.reset_game)
        #  End of button creation
        self.reset_game()

    #  Creates a new board
    def reset_game(self, touch=None):
        self.clear_widgets()
        self.squares = list()  # List of all squares for later access - two dimensional
        self.turn = "r"  # The current turn ingame
        black = True  # For board creation - to swap between black and white squares
        self.selected = None  # Currently selected square
        self.toClear = None  # If unit was eaten, it will be eaten by this variable
        self.can_jump = None  # If unit was eaten, in the case that another move is possible by the same unit, this variable will hold it
        # Loop to create board
        for i, y in enumerate(range(Window.size[1], 0 - 2 * int(Window.size[1] / 8), -int(Window.size[1] / 8))):
            self.squares.append(list())
            for j, x in enumerate(range(-int(Window.size[0] / 8), Window.size[0] + int(Window.size[0] / 8), int(Window.size[0] / 8))):
                square = Square(pos=(x, y), size=(Window.size[0] / 8, Window.size[1] / 8), black=black, row=i, col=j)
                self.squares[i].append(square)
                # If the loop is not out of bounds
                if i not in [0, 9] and j not in [0, 9]:
                    # Draws the square (black/white rectangle) and the unit on it
                    with square.canvas:
                        if square.black:
                            Color(0, 0, 0)
                            black = False
                        else:
                            Color(1, 1, 1)
                            black = True
                        Rectangle(pos=(x, y), size=(Window.size[0] / 8, Window.size[1] / 8))
                        d = Window.size[1] / 8
                        # If bottom of screen
                        if y < int(Window.size[1] * 3 / 8) and square.black:
                            square.unit = "r"
                            Color(1, 0, 0)
                            Ellipse(pos=(x + Window.size[0] / 16 - d / 2, y), size=(d, d))
                        elif y >= int(Window.size[1] * 5 / 8) and square.black:
                            square.unit = "b"
                            Color(0, 0, 1)
                            Ellipse(pos=(x + Window.size[0] / 16 - d / 2, y), size=(d, d))
                        square.bind(on_press=self.click)
                        self.add_widget(square)
                    # End of drawing
            black = not black

    # Displays reset button and disables all the rest
    def win(self):
        for i in self.squares:
            for j in i:
                j.disabled = True
        self.add_widget(self.reset)

    # Executed upon a square being pressed
    def click(self, touch):
        # If the same square is pressed twice
        if touch == self.selected:
            touch.selected = False
            self.selected = None
            touch.canvas.clear()
            self.draw_square(touch)
        # If the it's the turn of the unit pressed or the unit that was pressed can jump
        elif self.turn == touch.unit or touch == self.can_jump:
            # If there already was a selected unit
            if self.selected is not None:
                self.selected.selected = False
                self.selected.canvas.clear()
                self.draw_square(self.selected)
            self.selected = touch
            touch.selected = True
            touch.canvas.clear()
            self.draw_square(touch)
        # If there is a selected unit
        elif self.selected is not None:
            # If the move is valid (The selected unit can move to the pressed square)
            if self.valid_move(touch):
                # If there a unit was eaten
                if self.toClear is not None:
                    self.toClear.unit = None
                    self.toClear.canvas.clear()
                    self.draw_square(self.toClear)
                    self.toClear = None
                # If the selected unit fits the turn
                if self.selected.unit == self.turn:
                    if self.turn == "r":
                        self.turn = "b"
                    else:
                        self.turn = "r"
                # If reached the vertical edge of the board
                if (self.selected.unit == "r" and touch.row == 1) or (self.selected.unit == "b" and touch.row == 8):
                    self.selected.queen = True
                self.selected.selected = False
                touch.unit = self.selected.unit
                touch.queen = self.selected.queen
                # Win check
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
                # End win check
                self.selected.unit = None
                self.selected.queen = False
                self.selected.canvas.clear()
                self.draw_square(self.selected)
                self.selected = None
                self.draw_square(touch)

    # Checks whether the move is valid
    def valid_move(self, square):
        # If the pressed square is empty
        if square.unit is None:
            # If the selected unit is not the unit that can jump
            if self.selected != self.can_jump:
                # If there is a unit that can jump
                if self.can_jump is not None:
                    self.can_jump = None
                # If the unit is red
                if self.selected.unit == "r":
                    # If the selected square is in diagonal and forward from the red's perspective
                    if square.row == self.selected.row-1 and square.col in [self.selected.col-1, self.selected.col+1]:
                        return True
                else:
                    # If the selected square is in diagonal and forward from the blue's perspective
                    if square.row == self.selected.row+1 and square.col in [self.selected.col-1, self.selected.col+1]:
                        return True
            # If the user is attempting to jump over a square
            if abs(square.row - self.selected.row) == 2 and abs(square.col - self.selected.col) == 2:
                # If there is an enemy unit in the middle
                if self.selected.unit != self.squares[int(self.selected.row + (square.row - self.selected.row) / 2)][int(self.selected.col + (square.col - self.selected.col) / 2)].unit is not None:
                    self.toClear = self.squares[int(self.selected.row + (square.row - self.selected.row) / 2)][int(self.selected.col + (square.col - self.selected.col) / 2)]
                    # If there is a possibility for a jump
                    if self.check_jump(square):
                        self.can_jump = square
                    # If a unit who jumped before doesn't have any other jumping opportunities
                    if self.can_jump == self.selected:
                        self.can_jump = None
                    return True
            # If the unit is a queen
            if self.selected.queen:
                # The selected square is on a diagonal
                if abs(square.row - self.selected.row) == abs(square.col - self.selected.col):
                    passed = False  # Flag used for a c
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
        return False

    def check_jump(self, square):
        if square.queen:
            for i in range(1, 7):
                if square.row - i - 1 > 0 and square.col - i - 1 > 0:
                    if square.unit != self.squares[square.row - i][square.col - i] is not None:
                        if self.squares[square.row - i - 1][square.col - i - 1] is None:
                            return True
                if square.row - i - 1 > 0 and square.col + i + 1 < 9:
                    if square.unit != self.squares[square.row - i][square.col + i] is not None:
                        if self.squares[square.row - i - 1][square.col + i + 1] is None:
                            return True
                if square.row + i + 1 < 9 and square.col + i + 1 < 9:
                    if square.unit != self.squares[square.row + i][square.col + i] is not None:
                        if self.squares[square.row + i + 1][square.col + i + 1] is None:
                            return True
                if square.row + i + 1 < 9 and square.col - i - 1 > 0:
                    if square.unit != self.squares[square.row + i][square.col - i] is not None:
                        if self.squares[square.row + i + 1][square.col - i - 1] is None:
                            return True
            return False
        else:
            for i in [square.row - 1, square.row + 1]:
                for j in [square.col - 1, square.col + 1]:
                    if (i != int(self.selected.row + (square.row - self.selected.row) / 2) or j != int(self.selected.col + (square.col - self.selected.col) / 2)) and self.selected.unit != self.squares[i][j].unit is not None and self.squares[square.row + (i - square.row)*2][square.col + (j - square.col)*2].unit is None and square.row + (i - square.row) * 2 not in [0, 9] and square.col + (j - square.col) * 2 not in [0, 9]:
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
