from django.shortcuts import render, redirect
from django.http import HttpResponse
from random import randint

from sudoku.sudoku import Puzzle
from sudoku.models import Unique_tables
import time
import copy



# Create your views here.

def sudoku_main_page(request):
    return render(request, 'sudoku/main.html')
    # return HttpResponse('Главная страница приложения sudoku')

class MyPuzzle(Puzzle):
        all_marks = False   # показывать все 9 вариантов значений, или только возможные значения
        def swich_marks(self): self.all_marks = not self.all_marks


new = MyPuzzle()
base_puzzle = Unique_tables()
base_num = "m,,mn,"


def show_puzzle(request):
    """показать пазл"""
    new.make_finger_print()
    return render(request, 'sudoku/puzzle.html', {'puzzle': new, 'base_puzzle': base_puzzle})

def new_puzzle(request):
    """загрузить случайный пазл"""
    global base_puzzle
    n_pazzles = Unique_tables.objects.count()  # количество пазлов в списке
    rand = randint(1, n_pazzles)     # индекс случайного пазла
    base_puzzle = Unique_tables.objects.get(id=rand)
    # print('случайный пазл #%d :' % base_puzzle.id, base_puzzle.given, '\n длина фингерпринт:', len(base_puzzle.finger_print))
    new.__init__(base_str=base_puzzle.given, base_has_solution=base_puzzle.has_solution, base_solution=base_puzzle.solved, single_solution=base_puzzle.single_solution)
    # new.mix()
    return redirect('show_puzzle_url')

def new_empty_puzzle(request):
    global base_puzzle
    new.__init__([0]*81)
    base_puzzle = ''
    return redirect('show_puzzle_url')

def set_puzzle_value(request, indx, value):
    new.set_value(int(indx), int(value))
    return redirect('show_puzzle_url')

def on_off_marks(request):
    new.swich_marks()
    return redirect('show_puzzle_url')

def load_base_tables(request):
    myfile = open('sudoku/sudoku17.txt' ,'U')
    i = 0
    for line in myfile:
        i += 1
        line = line[:-1]    # обрезать последний символ
        puz = MyPuzzle(line)
        table = Unique_tables(base_string=i, given=line, finger_print=puz.make_finger_print())
        try:
            table.save()
        except:
            print('не удалось сохранить пазл #',i)
        else:
            sol = set()
            t = time.time()
            puz.solve(sol, max_solution=2, find_singles=True)
            table.time_of_solving = int((time.time() - t)*1000)
            if len(sol):
                table.has_solution = True
                if len(sol) == 1:
                    table.single_solution = True
                solution = sol.pop()
                s = ''
                for cell in solution.grid:
                    s += str(cell.value)
                table.solved = s
            table.save()
    return redirect('show_puzzle_url')

def mix_puzzle(request):
    new.mix()
    return redirect('show_puzzle_url')

def relabe_puzzle(request):
    new.relabeling()
    new.update_all_marks()
    return redirect('show_puzzle_url')

def solve_puzzle(request):
    new.get_solution()
    return redirect('show_puzzle_url')

def undo_relabeling_puzzle(request):
    new.undo_relabeling()
    return redirect('show_puzzle_url')

def undo_mix_puzzle(request):
    new.undo_mix()
    return redirect('show_puzzle_url')




