from csv import DictReader

from django.core.management import BaseCommand

from jobs.models import Company, JobPost


class Command(BaseCommand):
    # Show this when the user types help
    help = "Loads companies from company.csv"

    def handle(self, *args, **options):
        print("Loading companies")
        with open('c_data_sheet.csv') as f:
            for row in DictReader(f, delimiter=','):
                Company.objects.get_or_create(**row)
