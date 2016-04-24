from django.contrib import admin

from sudoku.models import Unique_tables


class Unique_tablesAdmin(admin.ModelAdmin):
    list_display = ('id', 'base_string', 'finger_print', 'time_of_solving')

# Register your models here.
admin.site.register(Unique_tables, Unique_tablesAdmin)