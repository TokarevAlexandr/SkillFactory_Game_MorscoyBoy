class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


class Ship:
    def __init__(self, length, bow, direction):
        self.length = length
        self.bow = bow
        self.direction = direction
        self.lives = length

    def dots(self):
        ship_dots = []
        for i in range(self.length):
            x = self.bow.x
            y = self.bow.y
            if self.direction == "vertical":
                y += i
            elif self.direction == "horizontal":
                x += i
            ship_dots.append(Dot(x, y))
        return ship_dots

class Board:
    def __init__(self, size=6):
        self.size = size
        self.field = [["O"] * size for _ in range(size)]
        self.ships = []
        self.hid = False
        self.alive_ships = 0

    def add_ship(self, ship):
        for dot in ship.dots():
            if self.out(dot) or dot in self.contour(ship):
                raise Exception("Ошибка размещения корабля!")
        for dot in ship.dots():
            x, y = dot.x, dot.y
            self.field[y][x] = "■"
        self.ships.append(ship)
        self.alive_ships += 1

    def contour(self, ship):
        contour_dots = []
        for dot in ship.dots():
            for i in range(-1, 2):
                for j in range(-1, 2):
                    x, y = dot.x + i, dot.y + j
                    if not (self.out(Dot(x, y))) and Dot(x, y) not in ship.dots() and self.field[y][x] == "O":
                        contour_dots.append(Dot(x, y))
                        self.field[y][x] = "."
        return contour_dots

    def out(self, dot):
        return not ((0 <= dot.x < self.size) and (0 <= dot.y < self.size))

    def shot(self, dot):
        if self.out(dot):
            raise Exception("Выстрел за пределами поля!")
        elif self.field[dot.y][dot.x] != "O" and self.field[dot.y][dot.x] != ".":
            raise Exception("Вы уже стреляли сюда!")
        elif self.field[dot.y][dot.x] == "■":
            self.field[dot.y][dot.x] = "X"
            for ship in self.ships:
                if dot in ship.dots():
                    ship.lives -= 1
                    if ship.lives == 0:
                        self.alive_ships -= 1
                        for d in ship.dots():
                            x, y = d.x, d.y
                            self.field[y][x] = "D"
                        print("Вы уничтожили вражеский корабль!")
                    else:
                        print("Вы попали в корабль противника!")
                    break
        else:
            self.field[dot.y][dot.x] = "."
            print("Вы промахнулись!")

    def __str__(self):
        board = ""
        board += "  | " + " | ".join([str(i) for i in range(1, self.size+1)]) + " |\n"
        board += "-" * (4 * self.size + 3) + "\n"
        for i in range(self.size):
            if i < 5:
                board += " "
            board += str(i + 1) + "| "
            for j in range(self.size):
                if self.hid and self.field[i][j] == "■":
                    board += "O | "
                else:
                    board += self.field[i][j] + " | "
            board += str(i + 1) + "\n"
        board += "-" * (4 * self.size + 3) + "\n"
        board += "  | " + " | ".join([str(i) for i in range(1, self.size+1)]) + " |\n"
        return board


class Player:
    def __init__(self, size=6):
        self.my_board = Board(size)
        self.enemy_board = Board(size)

    def move(self):
        while True:
            try:
                shot_dot = self.ask()
                self.enemy_board.shot(shot_dot)
                return self.enemy_board.field[shot_dot.y][shot_dot.x] == "X"
            except Exception as e:
                print(e)

    def ask(self):
        pass


import random
class AI(Player):
    def ask(self):
        x = random.randint(0, len(self.enemy_board.field) - 1)
        y = random.randint(0, len(self.enemy_board.field) - 1)
        return Dot(x, y)


class User(Player):
    def ask(self):
        while True:
            try:
                x = int(input("Введите координату Х: "))
                y = int(input("Введите координату Y: "))
                return Dot(x, y)
            except ValueError:
                print("Пожалуйста, введите целое число.")





class Game:
    def __init__(self):
        self.user = User()
        self.user_board = Board()
        self.ai = AI()
        self.ai_board = Board()

    def random_board(self, board):
        ships = [3, 2, 2, 1, 1, 1, 1]
        for ship in ships:
            while True:
                x = random.randint(0, len(board.field) - 1)
                y = random.randint(0, len(board.field) - 1)
                orientation = random.choice(['horizontal', 'vertical'])
                if board.add_ship(x, y, ship, orientation):
                    break
            if board.count_ships() > 20_000:
                raise Exception("Слишком много попыток разместить корабль. Доска слишком мала или переполнена.")

    def greet(self):
        print("Добро пожаловать в игру 'Морской Бой'!")
        print("Вы будете играть против компьютера.")
        print("Введите координаты вашего выстрела в формате 'X,Y' (без кавычек).")
        print("Давайте начнём!")

    def loop(self):
        while True:
            # Ход игрока
            user_move = self.user.ask()
            result = self.ai_board.move(user_move)
            self.user_board.shot(user_move)
            print("Твой ход:", user_move, result)
            if self.ai_board.alive_ships == 0:
                print("Ты выиграл!")
                break

            # Ход компьютера
            ai_move = self.ai.ask()
            result = self.user_board.shot(ai_move)
            self.ai_board.mark(ai_move, result)
            print("AI's move:", ai_move, result)
            if self.user_board.alive_ships == 0:
                print("AI выиграл!")
                break

    def start(self):
        self.random_board(self.user_board)
        self.random_board(self.ai_board)
        self.greet()
        self.loop()

game = Game()
game.start()