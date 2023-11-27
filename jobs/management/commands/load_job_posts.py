from csv import DictReader

from django.core.management import BaseCommand

from jobs.models import JobPost, JobTitleFilter


class Command(BaseCommand):
    # Show this when the user types help
    help = "Loads css from file"

    def add_arguments(self, parser):
        parser.add_argument('file', type=str)
        parser.add_argument('--private')
        parser.add_argument('--script')

    def handle(self, *args, **options):
        print("Loading css")
        script = options.get('script', None)
        with open(options['file'], encoding='utf-8') as f:
            for row in DictReader(f):
                job_title_filter = [i for i in list(JobTitleFilter.objects.all().values_list('title', flat=True)) if
                                    i in row['job_title']]
                if len(job_title_filter) > 0:
                    row['job_title_filter'] = JobTitleFilter.objects.get(title=job_title_filter[0])
                # if 'apply_url' in row and JobPost.objects.filter(apply_url=row['apply_url']).exists():
                #     continue
                if script:
                    if script == '1':
                        row['source'] = 'google'
                    elif script == '2':
                        row['source'] = 'other'
                    elif script == '3':
                        row['source'] = 'linkedin'
                if options['private']:
                    JobPost.objects.get_or_create(private=True, **row)
                else:
                    JobPost.objects.get_or_create(**row)
