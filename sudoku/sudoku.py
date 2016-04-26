""" Генератор и решатель пазла судоку
Генратор:
1) генерация случайного судоку с единственным решением и каким получится количеством заполненных ячеек
2) генерация нового судоку путем множества случайных преобразований базового поля с сохранением числа
заполненных ячеек и количества решений
"""
import random
import copy

def sum_of(lst):
    """Вернуть сумму элементов списка"""
    s = []
    for x in lst:
        if type(x) is list: s = s + x
    return s

class Marks:
    """Класс отметок о вариантах возможных значений для ячейки"""
    def __init__(self):
        self.candidats = [1, 2, 3, 4, 5, 6, 7, 8, 9]

    def __len__(self):
        return len(self.candidats)

    def __getitem__(self, item):
        """Проверка наличия item среди кандидатов
        :return True или False """
        try: i = int(item)
        except:
            return False
        return True if i in self.candidats else False

    def __str__(self):
        return str(self.candidats)

    def remove(self, item):
        if self[item]: self.candidats.remove(item)


class Cell:
    def __init__(self, i, v=0, give=False):
        self.index = i
        self.marks = Marks()
        self.set(v, give)

    def set(self, v, give=False):
        self.value = v
        self.given = True if give and v else False


class Puzzle:
    def __init__(self, base_str='', base_has_solution=False, base_solution='', single_solution=False):
        """Инициация пустого пазла либо на основе 81 символьной строки со значениями"""
        self.grid = []              # список ячеек пазла
        self.base_solution = [int(v) for v in list(base_solution)]     # решение базового пазла
        self.single_solution = single_solution  # единственное ли решение базового пазла
        self.steps = []             # история установки значений
        self.transformations = []   # история трансформаций
        self.relabelings = []       # история замены значений
        self.solved = {}    # словарь с решением текущего состояния пазла
                            # если словарь пустой - решения не известны, иначе:
                                # по ключу 'n_solutions' лежит количество решений
                                # # по ключу 'solution' массив с значениями решения по строкам

        for i in range(81): # загружаем ячейки пустыми или из базовой строки
            self.grid.append(Cell(i, int(base_str[i]), give=True)) if base_str else self.grid.append(Cell(i))
        if base_str: self.update_all_marks()

    def puzzle_str(self):
        """возвращает строку с текущими значениями пазла"""
        ps = ''
        for cell in self.grid:
            if cell.value:
                ps += str(cell.value)
            else:
                ps += '0'
        return ps

    def __str__(self):
        """подготавливает строку для выводв при печати пазла """
        ps = self.puzzle_str()
        show_str = 'Puzzle:' + '\n' + ps + '\n\n'
        for i in range(9):
            show_str = show_str + ps[i*9:i*9 + 9] + '\n'
        return show_str

    @property
    def given_cells(self):
        """массив заданных значений"""
        return [cell.value if cell.given else 0 for cell in self.grid]

    @property
    def rows(self):
        """ возвращает список строк пазла """
        return [self.grid[x*9: x*9 + 9] for x in range(9)]

    @property
    def columns(self):
        """ возвращает список колонок пазла """
        return list(map(list, zip(*self.rows)))

    @property
    def boxes(self):
        """ возвращает список ячеек для 9-и блоков 3Х3 пазла """
        return [self.grid[c*3+r*27:c*3+r*27+3] +
                  self.grid[c*3+r*27+9:c*3+r*27+12] +
                  self.grid[c*3+r*27+18:c*3+r*27+21] for r in range(3) for c in range(3)]

    @property
    def blank_cells(self):
        """ Вернуть список пустых ячеек
        :param rev: обратная сортировка (True) или прямая (False)"""
        b = [cell for cell in self.grid if cell.value == 0]  # получить список пустых ячеек
        b.sort(key=(lambda cell: cell.marks.candidats), reverse=False)    # отсортировать по меткам
        b.sort(key=(lambda cell: len(cell.marks)), reverse=False)  # и их количеству
        return b

    @property
    def filled_cells(self):
        """  Вернуть список заполненных ячеек, отсортированных по количеству меток
         :param rev: обратная сортировка (True) или прямая (False)"""
        b = [cell for cell in self.grid if cell.value != 0]  # получить список пустых ячеек
        b.sort(key=(lambda cell: cell.marks.candidats), reverse=False)    # отсортировать по меткам
        b.sort(key=(lambda cell: len(cell.marks)), reverse=True)  # и их количеству
        return b

    @property
    def is_correct(self):
        """Возвращает истину если заполненные ячейки соответствуют правилам судоку"""
        for i in range(9):
            if not (self.no_repit(self.boxes[i]) and self.no_repit(self.rows[i]) and self.no_repit(self.columns[i])):
                return False
        return True

    def no_repit(self, cells_list):
        """:return: True если ячейки не имеют одинаковых отличных от нуля значений"""
        len_of_set = len(set([cell.value for cell in cells_list if cell.value]))
        len_of_sequence = len([cell.value for cell in cells_list if cell.value])
        return True if len_of_set == len_of_sequence else False

    def rows_of_boxes(self):
        """ возвращает список из 3 трех слоев по 3 блока 3Х3 пазла """
        return [[[self.grid[c*3+r*27:c*3+r*27+3],
                  self.grid[c*3+r*27+9:c*3+r*27+12],
                  self.grid[c*3+r*27+18:c*3+r*27+21]] for c in range(3)] for r in range(3)]

    def make_finger_print(self):
        """Создание цифрововой метки пазла, не меняющейся от преобразований пазла"""
        fp = ['']*9 # по строке для каждого возможного значения метки от 1 до 9
        head = ''   # число свободных ячеек с одной меткой, двумя, тремя ... девятью
        blanks = self.blank_cells
        for n_marks in range(9):  # для каждого количества отметок n_marks от 1 до 9
            n_marks_cells = [cell for cell in blanks if len(cell.marks) == n_marks+1] # составляем список ячеек имеющих n_marks отметок
            head += '{0:02d}'.format(len(n_marks_cells))   # добавляем в строку заголовка число ячеек, имеющих n_marks отметок
            for i in range(9):                  # для i от 0 до 8
                n = 0                           # подсчитываем сколько ячеек,
                for cell in n_marks_cells:      # имеющих n_marks отметок
                    if cell.marks[i+1]: n += 1  # содержит значение i+1
                fp[i] += '{0:02d}'.format(n)    # записываем число найденых ячеек в соответствующую строку списка fp
        fp.sort(reverse=True)   # сортируем список
        self.fp = []
        self.fp.append(head)
        for i in range(9):  # формируем fingerprint , добавляя к заголовку сортированный массив fp
            head += '.' + fp[i]     # в виде строки с разделителем '.'
            self.fp.append(fp[i])   # и массива
        return head     # возвращаем fingerprint в виде строки

    def set_value(self, i, v):
        """Устанавливаем значение в пустую ячейку или очищаем ранее установленную с очисткой ячеек установленных после нее"""
        if v:   # если надо поставить ненулевое значение
            if self.grid[i].value == 0:     # в пустую ячейку:
                self.grid[i].set(v)                 # ставим заначение
                self.update_marks_by_value(i, v)    # пересчитываем метки
                self.steps.append(self.grid[i])     # записываем установленную ячейку
                if self.solved:
                    if self.solved['solution'][i//9][i%9] != v: # если значение не совпадает с решением
                        self.solved = {}                # обнуляем решение
            else:   # если в заполненную:
                return      # ничего не делаем и возвращаемся
        else: # если надо выставить нулевое значение
            if self.grid[i].value and not self.grid[i].given:   # в заполненную ячейку, не заданную изначально
                while True: # делаем следующее:
                    step = self.steps.pop()   # извлекаем из истории шагов последнюю установленную ячейку
                    step.value = 0              # очищаем ее
                    if i == step.index:         # если это был индекс нужной нам ячейки
                        self.update_all_marks()     # пересчитываем все отметки
                        self.solved = {}                    # обнуляем решение
                        return                      # и возвращаемся

    def update_marks_by_value(self, i, v):
        """ Обновить все отметки, связанные с установкой значения  v в ячейку с индексом i"""
        for cell in self.rows[i//9]:
            cell.marks.remove(v)     #  в строке содержащей ячейку с индексом i
        for cell in self.columns[i % 9]:
            cell.marks.remove(v)  #  в столбце содержащем ячейку с индексом i
        for cell in self.boxes[(i//27)*3 +(i%9)//3]:
            cell.marks.remove(v)  # очистка отметок о возможном значении для квадрата 3Х3

    def update_all_marks(self):
        """ Обновить все отметки на поле """
        for cell in self.grid:   cell.marks = Marks()
        for cell in self.grid:
            if cell.value:  self.update_marks_by_value(cell.index, cell.value)  # обновление меток всех связанных ячеек

    def make_given(self):
        """Отметить все заполненные ячейки как предопределенные"""
        for cell in self.grid:
            if cell.value:
                cell.given = True
            else:
                cell.given = False

    def find_hidden_single(self, some_cells):
        """найти скрытые синглы в области some_cells и вернуть отсортированный список индксов пустых ячеек пазла"""
        blanks = [cell for cell in some_cells if cell.value == 0]  # создаем список пустых ячеек для области
        if len(blanks) >= 2:      # если в группе имеются как минимум две пустые ячейки
            for cell in blanks:   # для каждой пустой ячейки
                other_sum = []
                for other_cell in blanks:   # найдем сумму отметок других ячеек:
                    if other_cell != cell:
                        other_sum += other_cell.marks.candidats
                sub = list(set(cell.marks.candidats) - set(other_sum))    # из отметок ячейки вычитаем множество отметок других ячеек
                if len(sub) == 1:
                    cell.marks.candidats = sub             # если это скрытый сингл обновляем отметки ячейки
                    # return self.blank_cells
        return self.blank_cells     # возвращаем новый список пустых ячеек

    def find_single_ang_set(self):
        """найти и установить синглы, вернуть список индексов пустых ячеек"""
        b = self.blank_cells  # получаем список пустых ячеек
        while len(b) and len(b[0].marks):     # если есть пустые ячейки и нет ячеек без меток - будем искать синглы
            for row in self.rows: b = self.find_hidden_single(row)  # в каждой строке
            for column in self.columns: b = self.find_hidden_single(column)  # в каждом столбце
            for box in self.boxes: b = self.find_hidden_single(box)  # в каждм блоке 3х3
            single_list = [cell for cell in b if len(cell.marks) == 1]  # составляем список синглов на поле
            if not single_list: break   # если нет синглов - выходим из цикла
            for cell in single_list:
                if len(cell.marks):
                    self.set_value(cell.index ,cell.marks.candidats[0])   # устанавливаем все синглы
                else:
                    return self.blank_cells
            b = self.blank_cells  # обновляем список индексов
        return b   # возвращаем список индексов

    def solve(self, sol, max_solution=0, find_singles=True):
        """  Найти  множество решений пазла
        :param sol: множество решений пазла
        :param max_solution: искать решений не более max_solution, если 0 - найти все решения
        :return: None"""
        if max_solution and len(sol) == max_solution: return
        if find_singles:    # если для решения используем поиск синглов
            b = self.find_single_ang_set()   # ищем голые и скрытые синглы
        else:                       # или
            b = self.blank_cells  # без поиска скрытых синглов
        if b == []:     # нет пустых ячеек - пазл решен!!!
            sol.add(self)   # добавить решенный пазл к множеству решений
            return          # выход
        else:
            if len(b[0].marks) == 0:  # нет отметок в первой пустой ячейке?
                return  # неправильный пазл
            else:  # если отметки есть
                for v in b[0].marks.candidats:  # для каждого возможного значения
                    puz = copy.deepcopy(self)   # создаем "глубокую" копию пазла
                    puz.set_value(b[0].index, v)  # устанавливаем значение в ячейку
                    puz.solve(sol, max_solution, find_singles)  # пробуем решить

    def get_solution(self):
        if not self.solved:
            puz = copy.deepcopy(self)
            sol = set()
            puz.solve(sol, max_solution=2)
            n = len(sol)
            self.solved['n_solutions'] = n
            if len(sol):
                self.solved['solution'] = [[cell.value for cell in rw] for rw in sol.pop().rows]
        return self.solved

    def transposing(self):
        """транспонировать пазл"""
        self.grid = sum_of(self.columns)

    def rotate90(self):
        """Повернуть матрицу на 90 градусов"""
        self.grid = sum_of(list(map(list, zip(*self.rows[::-1]))))

    def swap_rows(self):
        """обмен случайных строк в пределах случайного района"""
        a = random.randint(0, 2)  # найти случайный район
        r1, r2 = random.randint(0, 2), random.randint(0, 2)  # две случайные строки в районе
        while r1 == r2: r2 = random.randint(0, 2)  # причем вторая не должна совпадать с первой
        rws = self.rows
        rws[a * 3 + r1], rws[a * 3 + r2] = rws[a * 3 + r2], rws[a * 3 + r1]
        self.grid = sum_of(rws)

    def swap_columns(self):
        """обмен случайных столбцов в пределах случайного района"""
        self.transposing()
        self.swap_rows()
        self.transposing()

    def swap_row_area(self):
        """обмен случайными районами по горизонтали"""
        a1, a2 = random.randint(0, 2), random.randint(0, 2)  # две случайные области в пазле
        while a1 == a2: a2 = random.randint(0, 2)  # причем вторая не должна совпадать с первой
        rws = self.rows
        for i in range(3):
            rws[a1 * 3 + i], rws[a2 * 3 + i] = rws[a2 * 3 + i], rws[a1 * 3 + i]
        self.grid = sum_of(rws)

    def swap_columns_area(self):
        """Обмен случайными районами по вертикали"""
        self.transposing()
        self.swap_row_area()
        self.transposing()

    def relabeling(self, seed_number=0):
        """замена каждого значения по правилу"""
        rule = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        if seed_number: random.seed(seed_number)
        random.shuffle(rule)   # перемешать правило замены
        self.relabelings.append(rule)   # запомнить правило преобразования
        for cell in self.grid:      # все установленные значения заменить согласно правилу
            if cell.value: cell.value = rule[cell.value - 1]
        self.solved = {}    # обнулить решение
        return rule

    def mix(self, amt=100, relabeling=False):
        """Перемешать таблицу amt раз случайным преобразованием amt раз"""
        funct = self.transposing, self.swap_rows, self.rotate90,  self.swap_columns, self.swap_row_area, self.swap_columns_area
        for t in range(amt):
            funct[random.randint(0, len(funct) - 1)]()  # вызов случайной функции
        if relabeling:  rule = self.relabeling()
        self.reset_indexes()    #переопределить индекы
        self.update_all_marks() # пересчитать метки
        self.solved = {}
        return rule if relabeling else [1, 2, 3, 4, 5, 6, 7, 8, 9]

    def reset_indexes(self):
        """переопределить индексы ячеек перемешанного пазла"""
        self.transformations.append([cell.index for cell in self.grid]) # запомнить трансформмацию индексов
        for i in range(81):     # переопределить индексы ячеек
            self.grid[i].index = i
        self.base_solution = [self.base_solution[i] for i in self.transformations[-1]] # перемешать решение базового пазла

    def undo_mix(self):
        if self.transformations:
            transform = self.transformations.pop()
            for i in range(81):
                self.grid[i].index = transform[i]
            self.grid.sort(key=(lambda cell: cell.index), reverse=False)
            self.solved = {}

    def undo_relabeling(self):
        if self.relabelings:
            rule = self.relabelings.pop()
            for cell in self.grid:
                if cell.value: cell.value = rule.index(cell.value) + 1
            self.solved = {}

    def set_random_value(self, i, seed_number=0):
        """установить для ячейки i случайное возможное значение """
        val = self.grid[i].marks.candidats  # получаем очищенный список отметок
        n_marks = len(val)
        if n_marks:  # если есть отметки
            if seed_number: random.seed(seed_number)
            r_ind = random.randint(0, n_marks - 1)
            v = val[r_ind]  # устанавливаем в качестве значения одну из них
            self.set_value(i, v)

    def set_random_cells(self, n=1, random_order=False, seed_number=0):
        """ Установить случайные возможные значения в случайные пустые ячейки
        :param n: количество устанавливаемых ячеек
        :param random_order: если False для установки выбираются ячейки с наименьшим количеством меток
        :param seed_number: номер псевдослучайного числа, или 0 для нерегулируемого случайного числа
        :return: количество установленных ячеек """
        count = 0
        for t in range(0, n):  # нужное число раз
            empty = self.blank_cells  # получаем список пустых ячеек
            if len(empty) == 0: break  # заканчиваем цикл если больше нет пустых ячеек
            if random_order:  # если нужен случайный порядок
                if seed_number: random.seed(seed_number)  # заряжаем псевдослучайный генератор
                random.shuffle(empty)  # перемешиваем список
            i = empty[0].index  # получаем индекс устанавливаемой ячейки
            self.set_random_value(i)    # устанавливаем случайную ячейку
            count += 1  # увеличиваем счетчик установленных ячеек
        return count

    def clear_random_cells(self, n=1, b=[], seed_number=0):
        """ Попытаться очистить n ячеек пазла, так чтобы у пазла оставалось единственное решение
        :param n: количество очищаемых ячеек пазла
        :param b: список множеств "плохих" ячеек,
        :param seed_number: настройка генератора случайных чисел
        :return: количество очищенных ячеек
        """
        f_cells = self.filled_cells  # получить список заполненных ячеек
        b_cells = self.blank_cells  # получить список пустых ячеек
        if seed_number: random.seed(seed_number)
        random.shuffle(f_cells)  # и перемешать его
        c = 0  # счетчик успешно очищеных ячеек
        for i in f_cells:  # для заполненных ячеек
            if set(i + b_cells) in b: continue  # пропускаем множество плохих ячеек
            v = self.grid[i].value  # запомним очищаемое значение
            self.set_value(i, 0)  # очищаем ячейку
            sol = set()  # очищаем множество возможных решений
            self.solve(sol, max_solution=2)  # попробуем найти не более 2 решений
            if len(sol) == 1:  # если решение одно
                c += 1
                if c == n: break  # если очищено сколько надо выходим из цикла
            else:  # если решение не одно
                print('.', end='')
                b.append(set(self.blank_cells))  # пополняем список множеств плохих ячеек
                self.set_value(i, v)  # восстановить очищенную ячейку и продолжаем цикл
        return c  # -> количество успешно очищенных ячеек


    def generate_random_puzzle(self, n_start=20, seed_number=0):
        pass

    def show(self):  # распечатать пазл
        for row in range(0, 9):
            print('')
            for col in range(0, 9):
                print(self.grid[row * 9 + col].value, end=' ')
        # print('\n', self.grid)
        print('Всего ячеек: %d Пустых: %d Заполненых: %d' % (
            len(self.grid), len(self.blank_cells), len(self.filled_cells)))



#  тесты модуля
if __name__ == '__main__':
    import time
    print('-' * 8, ' Test ', '-' * 8)

    base = '000000001000002000003004050000060000000700620018000000000085003060000008200000000'
    print(base)
    new = Puzzle(base)

    new.show()
    print(new.is_correct)
    print('blank_cells:', [cell.marks.candidats for cell in new.blank_cells])
    fp0 = new.make_finger_print()
    # print('find_singles:', [new.grid[i]['mark'] for i in new.find_single_ang_set()])

    print(new.grid[0].marks[2])

    sol = set()
    t = time.time()
    solved = new.get_solution()
    print('C поиском скрытых синглов. Решений:%d   Затрачено времени:%f секунд' % (len(sol), time.time() - t))


    s = ''
    for cell in solved.grid:
        s += str(cell.value)
    print(s)


    # new.load_table(base)
    new.load_table(base)
    rule = new.mix(relabeling=True)
    new.show()
    print('blank_cells:', [cell.marks.candidats for cell in new.blank_cells])
    fp1 = new.make_finger_print()

    sol = set()
    t = time.time()
    new.solve(sol, max_solution=2, find_singles=True)
    print('Без поиска скрытых синглов. Решений:%d   Затрачено времени:%f секунд' % (len(sol), time.time() - t))
    solved = sol.pop()
    solved.show()

    print(len(fp0),'fp0:', fp0)
    print(len(fp1),'fp1:', fp1)

    # n = 0

    # while True:
    #     reply = input('начальное число ячеек>')
    #     try:
    #         f0 = int(reply)
    #     except:
    #         print('Блин!!!')
    #     else:
    #         if f0 < 16:
    #             print('маловато')
    #         else:
    #             break

    # while len(sol) == 0:
    #     n += 1
    #     new = Puzzle()
    #     for i in range(0, 26):
    #         new.set_random_cells(random_order=True)
    #     new.solve(sol, max_solution=2)
    #     print('# %d \r' % n, end='')
    #     if n > 100: break

    # b = set()
    #
    # new = Puzzle()
    #
    # new.load_table(s4_17)
    #
    # new.show()
    # print('blank cells: ', [new.grid[x]['mark'] for x in new.blank_cells()])
    #
    # b.add((new.grid[x]['mark'] for x in new.blank_cells()))
    # print('len(b) = ', len(b))
    #
    # new.mix()
    # new.update_all_marks()
    # new.show()
    # print('blank cells: ', [new.grid[x]['mark'] for x in new.blank_cells()])
    #
    # b.add((new.grid[x]['mark'] for x in new.blank_cells()))
    # print('len(b) = ', len(b))



    # sol = set()
    #
    # new.solve(sol, max_solution=2)
    #
    # print('Найдено решений:', len(sol))
    #
    # print(sol)
    #
    # s = sol.pop()
    # s.show()




    # if len(sol):
    #     new.show()
    #     print('Готово !!! Найдено решений: %d ' % len(sol))
    #     print('blank_cells:', [new.grid[x]['mark'] for x in new.blank_cells()])
    # else:
    #     print('Невозможно решить')
    #
    # s0 = copy.deepcopy(sol)
    #
    # while len(sol) > 1:
    #     one_of_sol = sol.pop()
    #     last_step = one_of_sol.steps[80]
    #     i, v = last_step['cell'], last_step['value']
    #     print('set (%d,%d)=%d' % (i // 9, i % 9, v))
    #     new.set_value(i, v)
    #     new.show()
    #     sol = set()
    #     new.solve(sol, max_solution=2)
    #     print('Теперь имеется решений:', len(sol))
    #     print('blank_cells:', [new.grid[x]['mark'] for x in new.blank_cells()])
    #
    #
    # bad, clr, count  = [], [], 0
    # t = time.time()
    # min_cell = len(new.filled_cells())
    # start_puz = copy.deepcopy(new)
    # while True:
    #     prev_puz = copy.deepcopy(new)
    #     if new.clear_random_cells(n=1, b=bad, seed_number=20):  # если удается очистить ячейку из пазла
    #         new.show()
    #         print([new.grid[x]['mark'] for x in new.blank_cells()])
    #         count += 1
    #         print('#%i Итого прошло %.2f сек.' % (count, time.time() - t))
    #         if len(new.filled_cells()) < min_cell: min_cell = len(new.filled_cells())
    #         print('min_cell = ', min_cell)
    #         if len(new.filled_cells()) < 20: break
    #         clr += list(set(prev_puz.filled_cells()) - set(new.filled_cells()))
    #         print('clr=',clr[::-1])
    #     else:
    #         print('!!! НАЗАД !!!  К ячейке:', clr[-2])
    #         bad.append(set([clr[-1]] + new.blank_cells()))     # пополняем множество плохих ячеек
    #         new.set_value(clr[-1] ,start_puz.grid[clr[-1]]['value'])    #  восстанавливаем значение ячейки из стартовой таблицы
    #         clr.pop()   # исключаем индекс последней ячейки из списка очищеных
    #         new.set_value(clr[-1] ,start_puz.grid[clr[-1]]['value'])    #  возвращаемся еще на шаг назад
    #         clr.pop()   # исключаем индекс последней ячейки из списка очищеных
