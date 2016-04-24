from django.conf.urls import url

from . import views

urlpatterns = [
    # new puzzle
    url(r'^puzzle/(?P<indx>\d{1,2})/(?P<value>\d{1})/$', views.set_puzzle_value),
    url(r'^puzzle/new/$', views.new_puzzle, name='new_random_puzzle_url'),
    url(r'^puzzle/$', views.show_puzzle, name='show_puzzle_url'),
    url(r'^$', views.sudoku_main_page, name='puzzle_main_menu_url'),
    url(r'^puzzle/swich_marks/$', views.on_off_marks, name='swich_marks_url'),
    url(r'^puzzle/load/$', views.load_base_tables),
    url(r'^puzzle/empty/$', views.new_empty_puzzle),
]
