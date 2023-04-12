from django.core.management.base import BaseCommand, CommandError
from hh.tasks import start_crawl


class Command(BaseCommand):
    help = "Аorce start crawl"

    def handle(self, *args, **options):
        start_crawl.delay()