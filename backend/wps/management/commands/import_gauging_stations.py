import json

from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand
from wps.models import GaugingStation, SurfaceWaterBody


class Command(BaseCommand):
    help = """
        Import data for gauging stations from JSON to DB
        usage: python manage.py import_gauging_stations.py
    """

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the JSON file')

    def handle(self, *args, **options):
        file_path = options['file_path']

        with open(file_path) as f:
            data = json.load(f)

        for obj in data:
            geom = Point(obj['coordinates'])
            water_body = SurfaceWaterBody.objects.filter(buffer200__intersects=geom).first()

            gs, _ = GaugingStation.objects.get_or_create(
                name=obj['name'],
                altitude=obj['altitude'],
                geom=geom,
                water_body=water_body
            )

        self.stdout.write(self.style.SUCCESS('Gauging stations imported successfully!'))
