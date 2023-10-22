import csv

from django.core.management.base import BaseCommand
from recipes.models import Ingredient


def import_data():
    with open('./data/ingredients.csv',
              encoding='utf-8') as csv_file:
        fieldnames = ['name', 'measurement_unit']
        csv_reader = csv.DictReader(csv_file, fieldnames=fieldnames)
        for row in csv_reader:
            Ingredient.objects.get_or_create(
                name=row['name'],
                measurement_unit=row['measurement_unit'])


class Command(BaseCommand):

    def handle(self, *args, **options):
        import_data()
    print('Information from ingredients json-file downloaded.')
