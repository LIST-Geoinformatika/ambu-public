import json
from datetime import datetime

from django.core.management.base import BaseCommand
from wps.models import NodeFlowMeasurement, WaterBodyNode


class Command(BaseCommand):
    help = """
        Import data for waterbody nodes from JSON to DB
        usage: python manage.py import_waterbody_nodes_flows path/to/file.json
    """

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the JSON file')

    def handle(self, *args, **options):
        file_path = options['file_path']

        with open(file_path) as f:
            data = json.load(f)

        for obj in data:
            for month_name, values in obj.items():
                month = datetime.strptime('2023-{}'.format(month_name), '%Y-%B')
                for node in values:
                    node_id = node['node_id']

                    node_obj = WaterBodyNode.objects.get(node_id=node_id)
                    q50 = node['q50']
                    q95 = node['q95']
                    wafu = node['wafu']

                    NodeFlowMeasurement.objects.get_or_create(
                        month=month,
                        node=node_obj,
                        q50_value=q50,
                        ef_value=q95,
                        wafu_value=wafu
                    )

        self.stdout.write(self.style.SUCCESS('Node flows imported successfully!'))
