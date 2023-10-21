import json
import os
import sys

from django.conf import settings
from django.core.management.base import BaseCommand
from recipes.models import Ingredient


def import_ingredient():
    with open(os.path.join(settings.BASE_DIR, 'data', 'ingredients.json'),
              'r', encoding='utf-8') as f:
        data = json.load(f)
        for i in range(len(data)):
            Ingredient.objects.get_or_create(
                name=data[i].get('name'),
                measurement_unit=data[i].get('measurement_unit')
            )
    print('Information from ingredients json-file downloaded.')


class Command(BaseCommand):

    def handle(self, *args, **options):
        import_ingredient()


sys.path.append(os.path.dirname(__file__))
