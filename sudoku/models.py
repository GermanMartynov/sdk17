from django.db import models

# Create your models here.

class Unique_tables(models.Model):
    PUZZLE_DIFFICULTY = (('E','Easy'), ('M','Medium'), ('H','Hard'))
    base_string = models.IntegerField('String from file', default=0)
    given = models.CharField('Given puzzle', max_length=81, unique=True)
    finger_print = models.CharField('Finger print', max_length=189, unique=True)
    solved = models.CharField('Solved puzzle', max_length=81, blank=True)
    has_solution = models.BooleanField('The puzzle has a solution', default=False)
    single_solution = models.BooleanField('The puzzle has a single solution', default=False)
    difficulty = models.CharField('Level of difficulty', max_length=1, default='E', choices=PUZZLE_DIFFICULTY)
    time_of_solving = models.IntegerField('Solving time (millisecond)', default=0)

    def __str__(self):
        return str(self.id)

