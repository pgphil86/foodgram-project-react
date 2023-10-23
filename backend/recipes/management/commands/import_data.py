import csv

from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            import_data()
            print('Ingridients from json file downloaded.')
        except Exception as err:
            print(err)


def import_data():
    with open('./data/ingredients.csv',
              encoding='utf-8') as csv_file:
        fieldnames = ['name', 'measurement_unit']
        csv_reader = csv.DictReader(csv_file, fieldnames=fieldnames)
        for row in csv_reader:
            Ingredient.objects.get_or_create(
                name=row['name'],
                measurement_unit=row['measurement_unit'])
