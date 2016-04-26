from django.conf.urls import url

from . import views

urlpatterns = [
    # new puzzle
    url(r'^puzzle/(?P<indx>\d{1,2})/(?P<value>\d{1})/$', views.set_puzzle_value),
    url(r'^puzzle/new/$', views.new_puzzle, name='new_random_puzzle_url'),
    url(r'^puzzle/$', views.show_puzzle, name='show_puzzle_url'),
    url(r'^$', views.sudoku_main_page, name='puzzle_main_menu_url'),
    url(r'^puzzle/swich_marks/$', views.on_off_marks, name='swich_marks_url'),
    url(r'^puzzle/load/$', views.load_base_tables, name='load_tables_from_file_url'),
    url(r'^puzzle/empty/$', views.new_empty_puzzle, name='empty_puzzle_url'),
    url(r'^puzzle/mix/$', views.mix_puzzle, name='mix_puzzle_url'),
    url(r'^puzzle/mix/undo$', views.undo_mix_puzzle, name='undo_mix_puzzle_url'),
    url(r'^puzzle/relabel/$', views.relabe_puzzle, name='relabe_puzzle_url'),
    url(r'^puzzle/relabel/undo/$', views.undo_relabeling_puzzle, name='undo_relabeling_puzzle_url'),
    url(r'^puzzle/solve/$', views.solve_puzzle, name='solve_puzzle_url'),
]
