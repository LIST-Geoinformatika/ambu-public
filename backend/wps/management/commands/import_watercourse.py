import json

from django.contrib.gis.geos import LineString, MultiLineString, MultiPolygon
from django.core.management.base import BaseCommand
from wps.models import SurfaceWaterBody


class Command(BaseCommand):
    help = """
        Import vector data for water courses from GeoJSON to the DB
        usage: python manage.py import_watercourse.py
    """

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the GeoJSON file')

    def handle(self, *args, **options):
        file_path = options['file_path']

        with open(file_path) as f:
            data = json.load(f)

        features = data['features']

        buffer_distance = 200  # distance in meter
        buffer_width = buffer_distance / 40000000.0 * 360.0

        for feature in features:
            name = feature['properties']['EmertimiGj']
            wb_code = feature['properties']['Nat_WBCode']
            coordinates = feature['geometry']['coordinates']
            line_strings = []
            polygons = []
            for coords in coordinates:
                line_string = LineString(coords)
                line_strings.append(line_string)

                buffered = line_string.buffer(buffer_width)
                polygons.append(buffered)

            geom = MultiLineString(line_strings)
            buffer200 = MultiPolygon(polygons)

            SurfaceWaterBody.objects.get_or_create(name=name, geom=geom, wb_code=wb_code, buffer200=buffer200)

        self.stdout.write(self.style.SUCCESS('Data imported successfully'))
