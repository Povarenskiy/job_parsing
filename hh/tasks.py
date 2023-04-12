import requests

from scraper.spiders.job import JobSpider
from scrapy.crawler import CrawlerProcess, CrawlerRunner
from scrapy.utils.project import get_project_settings

from job_scraping.celery import app
from celery.signals import celeryd_init

from django.conf import settings
from .models import HhItems


@app.task
def send_notification(code):
    """
    Рассылка уведомлений о новых вакансиях.
    """
    apiURL = f'https://api.telegram.org/bot{settings.BOT_TOKEN}/sendMessage'

    item = HhItems.objects.filter(code=code).first() 
    message = f'{item.title}\n{item.exp}\n{item.url}'
    
    try:
        requests.post(apiURL, json={'chat_id': settings.CHAT_ID, 'text': message})
    except Exception as e:
        print(f'Отправка сообщений не удалась, причина: {e}')



@app.task
def start_crawl():
    """
    Периодическая задача Celery каждые 3 часа
    Запуск паука 
    """
    process = CrawlerProcess(get_project_settings())
    process.crawl(JobSpider)
    process.start()






