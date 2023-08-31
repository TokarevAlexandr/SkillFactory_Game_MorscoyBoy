import random


class Dot:  # класс точек и виды отображения точек на игровой доске
    type = 'dot'
    empty_dot = "O"  # пустая точка
    ship_dot = "■"  # точка с кораблем
    destroyed_ship_dot = "X"  # точка с уничтоженным кораблем
    missed_dot = "T"  # точка промаха
    contour_dot = "□"  # точка контура корабля

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):  # метод сравнения точек
        return self.x == other.x and self.y == other.y


class Ship:  # класс корабля
    def __init__(self, size, x, y, direction=0, ship_dots=None):
        if ship_dots is None:
            ship_dots = []
        self.size = size
        self.x = x
        self.y = y
        self.direction = direction
        self.hp = size
        self.ship_dots = ship_dots
        self.ship_contour = []

    def dots(self):  # метод формирует список с точками корабля (класса Dot)
        self.ship_dots = []  # чтобы избежать накопления точек в списке,
        # перед формированием точек каждого корабля список "обнуляется"
        if self.direction == 0:  # если корабль горизонтальный
            for i in range(self.size):
                self.ship_dots = self.ship_dots + [Dot(self.x - 1, self.y + i - 1)]
        else:  # если корабль вертикальный
            for i in range(self.size):
                self.ship_dots = self.ship_dots + [Dot(self.x + i - 1, self.y - 1)]
        return self.ship_dots

    def contour(self, ship_dots):  # метод формирует контур корабля (список класса Dot)
        for i in ship_dots:  # обводим корабль контуром в виде списка точек
            for a in range((i.x - 1), (i.x + 2)):
                for b in range(i.y - 1, i.y + 2):
                    if Dot(a, b) not in self.ship_contour and Dot(a, b) not in ship_dots and 0 <= a < 6 and 0 <= b < 6:
                        # избегаем дублирования точек "контура"
                        self.ship_contour = self.ship_contour + [
                            Dot(a, b)]  # формируем список точек "контура", куда корабли ставить нельзя
        return self.ship_contour


class Board:  # класс игровой доски
    def __init__(self, board=None, ships=None, hid=False, live_ships=0):
        if ships is None:
            ships = []
        if board is None:
            board = [[Dot.empty_dot] * 6 for _ in range(6)]
        self.board = board
        self.ships = ships
        self.hid = hid
        self.live_ships = live_ships
        self.ship_contours = []
        self.shot_points = []
        self.unique_ships = []

    def print_board(self):  # метод вывода доски (с красивой графикой)
        if not self.hid:
            for i in range(7):
                if i == 0:
                    i = " "
                print(i, end=" | ")
            print()
            for i in range(6):
                for j in range(6):
                    if j == 0:
                        print(i + 1, "|", self.board[i][j], end=" | ")
                    else:
                        print(self.board[i][j], end=" | ")
                print()
        print(f"\n{self.live_ships} кораблей в строю\n")  # показываем , сколько живых кораблей
        # осталось на доске

    def add_ship(self, ship_dots, ship_contour, hid, ship):  # метод добавления корабля на игровую доску
        try:
            for i in ship_dots:  # проверяем, не находится ли какая-то из точек корабля в "запретном диапазоне"
                if i in self.ships or i in self.ship_contours or i.x < 0 or i.x > 5 or i.y < 0 or i.y > 5:
                    raise IndexError  # если да, то инициируем ошибку
            self.ships = self.ships + ship_dots  # дополняем список точек кораблей списком точек очередного корабля
            self.unique_ships = self.unique_ships + [ship]  # дополняем список уникальных кораблей класса Ship
            if hid is False:
                for i in ship_dots:  # ставим корабль на доску (для игрока-человека)
                    self.board[i.x][i.y] = i.ship_dot
            for i in ship_contour:  # добавляем контур корабля в список контуров доски
                self.ship_contours = self.ship_contours + [i]
            self.live_ships = self.live_ships + 1  # добавляем установленный корабль в счетчик "живых кораблей"
            return self.board, self.ships, self.ship_contours, self.live_ships
        except IndexError:
            if hid is False:  # этот параметр для расстановки доски игрока-компьютера, сообщение не выводим
                print("Диапазон занят либо некорректен, попробуйте еще раз")

    def shot(self, shot_point, hid=False):  # метод выполняет обработку выстрела по доске
        try:
            if shot_point in self.shot_points or \
                    shot_point.x < 0 or shot_point.x > 6 or shot_point.y < 0 or shot_point.y > 6:  # если выстрел сделан
                # вне поля, либо туда, куда уже ранее был сделан выстрел, объявляется исключение
                raise IndexError
            self.shot_points = self.shot_points + [shot_point]  # счетчик уже сделанных выстрелов
            if shot_point in self.ships:  # проверка, попал ли выстрел в какую-то из клеток кораблей доски
                self.board[shot_point.x][shot_point.y] = shot_point.destroyed_ship_dot
                unique_ship_counter = -1
                for i in self.unique_ships:  # проверяем список "уникальных" кораблей доски (список класса Ship), при
                    # определении, в какой корабль попал выстрел - отнимаем хитпоинт
                    unique_ship_counter = unique_ship_counter + 1
                    for j in i.ship_dots:  # пробегаемся по точкам каждого корабля
                        if shot_point == j:
                            self.unique_ships[unique_ship_counter].hp = self.unique_ships[unique_ship_counter].hp - 1
                            # отнимаем хитпоинт
                            if i.hp == 0:  # если хитпоинтов корабля ноль,
                                # то выводим сообщения (для игрока-человека), что корабль уничтожен
                                self.live_ships = self.live_ships - 1  # счетчик "живых" кораблей доски
                                for k in i.ship_contour:  # уничтоженный корабль обводим контуром для удобства
                                    self.board[k.x][k.y] = k.contour_dot
                                if hid is False:
                                    print("Корабль уничтожен!")
                                    break
                            elif hid is False:  # если у корабля есть еще не подбитые точки (хитпоинты)
                                print("Корабль поврежден!")
                                break
            else:
                print("Промах!")
                self.board[shot_point.x][shot_point.y] = shot_point.missed_dot  # если в корабль не попали,
                # ставим точку "промаха
            return self.board

        except IndexError:
            if hid is False:  # выводим сообщение для игрока-человека, не выводим для игрока-компьютера
                print("Координаты выстрела некорректны, либо повторны, попробуйте еще раз")


class Player:  # класс игрока
    def __init__(self, player, my_board, enemy_board, shot_point=None, hid=True):
        self.player = player
        self.my_board = my_board
        self.enemy_board = enemy_board
        self.shot_point = shot_point
        self.hid = hid

    def ask(self):  # метод ввода точки выстрела, данный метод переопределен в "подклассах", т.к. игрок-человек
        # вводит точки вручную, а компьютер автоматически
        return self.shot_point

    def move(self, hid=False):  # метод делает игровой ход - выстрел по доске противника и обработку результата
        self.enemy_board.shot(self.shot_point, self.hid)
        if hid is False:
            print("Ваша игровая доска:", "\n")
        else:
            print("Игровая доска противника:", "\n")
        self.enemy_board.print_board()
        if self.enemy_board.live_ships == 0:  # если живых кораблей ноль, объявляется победа данного игрока
            # (человека либо компьютера)
            print("Победа игрока ", self.player, "\n")


class User(Player):  # наследуемый подкласс для игрока-человека
    def __init__(self, my_board, enemy_board, player='"Человек"', hid=False):
        super().__init__(player, my_board, enemy_board, shot_point=None, hid=True)
        self.player = player
        self.hid = hid

    def ask(self):  # метод ввода точки стрельбы для человека
        print("Введите координаты выстрела:")
        x = int(input("X:")) - 1
        y = int(input("Y:")) - 1
        self.shot_point = Dot(x, y)
        return self.shot_point


class AI(Player):  # наследуемый подкласс для игрока-компьютера
    def __init__(self, my_board, enemy_board, player='"Компьютер"', hid=True):
        super().__init__(player, my_board, enemy_board, shot_point=None, hid=True)
        self.player = player
        self.hid = hid

    def ask(self):  # метод ввода точки стрельбы для компьютера
        self.shot_point = Dot(random.randint(0, 5), random.randint(0, 5))
        return self.shot_point


class Game:  # класс игрового цикла - расстановки кораблей и собственно игры
    def __init__(self, player=None, ai=None):
        self.player = player
        self.player_board = Board()
        self.ai = ai
        self.ai_board = Board()
        self.ships_sizes = (3, 2, 2, 1, 1, 1, 1)  # список размеров кораблей
        self.ship_names = ('крейсер (3 точки)', "эсминец 1 (2 точки)", "эсминец 2 (2 точки)",
                           "катер 1 (1 точка)", "катер 2 (1 точка)", "катер 3 (1 точка)", "катер 4 (1 точка)")  # список
        # названий кораблей

    def gen_player_board(self):  # метод устанавливает корабли и формирует игровую доску игрока-человека
        print(self.player_board.print_board())  # перед началом расстановки выведем пустую игровую доску
        ship_count = 0  # начальное значение счетчика кораблей
        ship_name_count = -1  # начальное значение счетчика названий кораблей
        for ship_size in self.ships_sizes:
            ship_count = ship_count + 1  # счетчик кораблей
            ship_name_count = ship_name_count + 1  # счетчик названий
            while True:
                print("Устанавливаем ", self.ship_names[ship_name_count])
                if ship_size > 1:
                    ship = Ship(ship_size, int(input("Введите координату X:")), int(input("Введите координату Y:")),
                                int(input('Введите направление')))
                else:  # если корабль из одной точки, направление спрашивать не нужно
                    ship = Ship(ship_size, int(input("Введите координату X:")), int(input("Введите координату Y:")))
                self.player_board.add_ship(ship.dots(), ship.contour(ship.dots()), False, ship)
                if self.player_board.live_ships == ship_count:
                    self.player_board.print_board()
                    break
        return self.player_board

    def gen_ai_board(self):  # метод устанавливает корабли и формирует игровую доску игрока-компьютера
        attempt_count = 0  # задаем начальное количество попыток установки корабля
        while self.ai_board.live_ships != 7:  # цикл будет повторяться, пока успешно не установим все 7 кораблей
            ship_count = 0  # начальное значение счетчика кораблей
            for ship_size in self.ships_sizes:
                ship_count = ship_count + 1  # счетчик кораблей
                if attempt_count > 100:  # если неудачных попыток больше 100, цикл прерывается и уходит на while
                    attempt_count = 0  # если уходим на "большой" цикл - счетчик сбрасываем
                    break
                while True:
                    ship = Ship(ship_size, random.randint(1, 6), random.randint(1, 6), random.randint(0, 1))
                    self.ai_board.add_ship(ship.dots(), ship.contour(ship.dots()), True, ship)
                    attempt_count = attempt_count + 1  # счетчик попыток
                    if attempt_count > 100:  # если неудачных попыток больше 100, цикл прерывается и уходит на for,
                        # где тоже прерывается и уходит на while
                        self.ai_board = Board()  # "обнуляем" доску от ранее расставленных кораблей на "неудачной" доске
                        break
                    if self.ai_board.live_ships == ship_count:
                        attempt_count = 0  # если корабль установлен - счетчик сбрасываем
                        break
        # self.ai_board.print_board()
        return self.ai_board

    def game_loop(self):  # метод непосредственно игрового цикла, считает ходы,
        # по очереди вызывает методы ходов для игроков и в случае победы одного из игроков завершает игру
        pl = User(my_board=g.player_board, enemy_board=g.ai_board)
        ai = AI(my_board=g.ai_board, enemy_board=g.player_board)
        move_count = 1
        while True:
            print("Ход ", move_count, "\n")
            move_count = move_count + 1
            pl.ask()
            pl.move(hid=True)
            ai.ask()
            ai.move(hid=False)
            if pl.enemy_board.live_ships == 0 or ai.enemy_board.live_ships == 0:
                break

    def greeting(self):
        print("Правила игры:"
              "\n1. Играем с компьютером"
              "\n2. Игровая доска - поле 6х6 клеток"
              "\n3. В начале игры расставляем корабли на игровой доске"
              "\n4. У вас 1 трехпалубный крейсер, 2 двухпалубных эсминца и 4 однопалубных катера"
              "\n5. Игра начинается с расстановки кораблей на игровой доске:"
              "\nвводим координаты носа корабля (X - горизонталь, Y - вертикаль)"
              "\nи (кроме однопалубных катеров) направление корабля"
              "\n(0 - горизонтальное, 1 или любая другая цифра - вертикальное)"
              "\n4. Ставить корабли в соседних точках друг с другом нельзя, в этом случае будет предложена"
              "\nповторная попытка"
              "\n5. Компьютер расставляет свои корабли автоматически"
              "\n6. Далее игроки (Вы и компьютер) по очереди делаете выстрелы, вводя координаты X и Y"
              "\n7. Стрелять вне доски либо в точку, куда ранее стреляли - нельзя, в этом случае будет предложен"
              "\nповторный ход"
              "\n8. После выстрела будет выведено сообщение о результате - промах, либо корабль подбит, либо уничтожен"
              "\n9. Подбитые корабли обозначаются крестиком, промахи - буквой Т"
              "\n10. Если Вы уничтожили корабль противника, на игровой доске противника он будет для удобства"
              "\nобведен контуром - туда стрелять смысла нет"
              "\n11. После каждого хода будет выводится Ваша доска с результатами стрельбы противника, и доска"
              "\nпротивника с результатами Вашей стрельбы, а также количество оставшихся у Вас и у противника кораблей"
              "\n12. Выигрывает тот, кто первый уничтожит все корабли противника"
              "\n УДАЧИ!"
              "\n")


g = Game()
g.greeting()
g.gen_player_board()
g.gen_ai_board()
g.game_loop()