import json

from django.contrib.gis.geos import LineString, MultiLineString
from django.core.management.base import BaseCommand
from wps.models import WaterCourseNetwork


class Command(BaseCommand):
    help = """
        Import vector data for water flows from GeoJSON to the DB
        usage: python manage.py import_watercourse_network.py
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
            line_strings = []
            for coords in coordinates:
                line_string = LineString(coords)
                line_strings.append(line_string)

            multi_line_string = MultiLineString(line_strings)

            WaterCourseNetwork.objects.get_or_create(name=name, geom=multi_line_string)

        self.stdout.write(self.style.SUCCESS('Data imported successfully'))
