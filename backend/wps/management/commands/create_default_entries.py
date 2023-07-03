
from django.core.management.base import BaseCommand
from wps.models import NaceCode


class Command(BaseCommand):
    help = """
        Create default DB entries
        usage: python manage.py create_default_entries
    """

    def handle(self, *args, **options):

        nace_codes = [
            {'code': '36', 'description': 'Water collection, treatment and supply'},
            {'code': '37', 'description': 'Sewerage'},
            {'code': '38', 'description': 'Waste collection, treatment and disposal activities; materials recovery'},
            {'code': '39', 'description': 'Remediation activities and other waste management services'}
        ]

        for nc in nace_codes:
            NaceCode.objects.get_or_create(**nc)

        self.stdout.write(self.style.SUCCESS('NACE codes successfully created'))
