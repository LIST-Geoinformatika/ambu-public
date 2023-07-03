import json

from django.contrib.gis.geos import MultiPolygon, Polygon
from django.core.management.base import BaseCommand
from wps.models import Wetland


class Command(BaseCommand):
    help = """
        Import vector data for wetlands from GeoJSON to the DB
        usage: python manage.py import_wetlands.py
    """

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the GeoJSON file')

    def handle(self, *args, **options):
        file_path = options['file_path']

        with open(file_path) as f:
            data = json.load(f)

        features = data['features']

        for feature in features:
            name = feature['properties']['InspireID']
            coordinates = feature['geometry']['coordinates']

            polygons = []
            for coords in coordinates:
                polygon = Polygon(coords[0])
                polygons.append(polygon)

            geom = MultiPolygon(polygons)
            Wetland.objects.get_or_create(name=name, geom=geom)

        self.stdout.write(self.style.SUCCESS('Data imported successfully'))
