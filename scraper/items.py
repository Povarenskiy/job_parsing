from scrapy_djangoitem import DjangoItem
from hh.models import HhItems


class ScraperHhItem(DjangoItem):
    django_model = HhItems
    