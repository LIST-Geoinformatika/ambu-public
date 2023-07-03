import json

from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand
from wps.models import WaterBodyNode


class Command(BaseCommand):
    help = """
        Import waterbody nodes from GeoJSON to DB
        usage: python manage.py import_waterbody_nodes.py
    """

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the JSON file')

    def handle(self, *args, **options):
        file_path = options['file_path']

        with open(file_path) as f:
            data = json.load(f)

        features = data['features']

        for obj in features:
            geom = Point(obj['geometry']['coordinates'])
            node_id = obj['properties']['Id']

            WaterBodyNode.objects.get_or_create(
                node_id=node_id,
                geom=geom,
            )

        self.stdout.write(self.style.SUCCESS('Waterbody nodes imported successfully!'))
