import json

from django.contrib.gis.geos import Polygon
from django.core.management.base import BaseCommand
from wps.models import Basin, SubBasin


class Command(BaseCommand):
    help = """
        Import vector data for sub-basins from GeoJSON to the DB
        usage: python manage.py import_subbasins.py
    """

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the GeoJSON file')

    def handle(self, *args, **options):
        file_path = options['file_path']

        with open(file_path) as f:
            data = json.load(f)

        features = data['features']

        for feature in features:
            name = feature['properties']['Sub_code']
            coordinates = feature['geometry']['coordinates']
            polygon = Polygon(coordinates[0][0])
            centroid = polygon.centroid
            basin = Basin.objects.filter(geom__intersects=centroid).first()
            SubBasin.objects.get_or_create(name=name, geom=polygon, basin=basin)

        self.stdout.write(self.style.SUCCESS('Data imported successfully'))
