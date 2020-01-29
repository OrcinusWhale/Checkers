from kivy.uix.layout import Layout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.graphics import *
from kivy.app import App


class Square(ButtonBehavior, Widget):
    def __init__(self, pos, size, black):
        Widget.__init__(self)
        ButtonBehavior.__init__(self)
        self.black = black
        self.unit = None
        self.pos = pos
        self.size = size
        self.queen = False
        self.selected = False


class Board(Layout):
    def __init__(self):
        Layout.__init__(self)
        self.squares = list()
        self.turn = "r"
        black = True
        self.selected = None
        for i in range(0, Window.size[1], int(Window.size[1] / 8)):
            for j in range(0, Window.size[0], int(Window.size[0] / 8)):
                square = Square(pos=(j, i), size=(Window.size[0] / 8, Window.size[1] / 8), black=black)
                self.squares.append(square)
                with square.canvas:
                    if square.black:
                        Color(0, 0, 0)
                        black = False
                    else:
                        Color(1, 1, 1)
                        black = True
                    Rectangle(pos=(j, i), size=(Window.size[0] / 8, Window.size[1] / 8))
                    d = Window.size[1] / 8
                    if i < int(Window.size[1] / 4):
                        square.unit = "r"
                        Color(1, 0, 0)
                        Ellipse(pos=(j + Window.size[0] / 16 - d / 2, i), size=(d, d))
                    elif i >= int(Window.size[1] * 3 / 4):
                        square.unit = "b"
                        Color(0, 0, 1)
                        Ellipse(pos=(j + Window.size[0] / 16 - d / 2, i), size=(d, d))
                    square.bind(on_press=self.click)
                    self.add_widget(square)
            black = not black

    def click(self, touch):
        if touch == self.selected:
            touch.selected = False
            self.selected = None
            touch.canvas.clear()
            self.draw_square(touch)
        elif self.turn == "r" and touch.unit == "r" or self.turn == "b" and touch.unit == "b":
            if self.selected is not None:
                self.selected.selected = False
                self.selected.canvas.clear()
                self.draw_square(self.selected)
            self.selected = touch
            touch.selected = True
            touch.canvas.clear()
            self.draw_square(touch)


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
                Ellipse(pos=(square.pos[0] + square.size[0] / 2 - d / 4, square.pos[1]), size=(d / 2, d / 2))


class Game(App):
    def build(self):
        self.title = "ChEcKeRs"
        return Board()


Game().run()
