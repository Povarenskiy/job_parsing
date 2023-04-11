import scrapy
import re

from asgiref.sync import sync_to_async
from scraper.items import ScraperHhItem 
from hh.models import HhItems


class JobSpider(scrapy.Spider):
    name = 'job'
    allowed_domains = ['hh.ru']


    def __init__(self,
                name=None,
                key_remotely = ['удаленная работа', 'удален'],   
                key_words = ['python', 'django'],     
                key_words_exception = ['senior ', 'middle', 'team lead'],             
                key_locations = ['санкт'],                       
                key_exp = ['6 лет'],                               
                **kwargs):
        super().__init__(name, **kwargs)
        
        self.key_remotely = key_remotely                # ключи для работы удаленно
        self.key_words = key_words                      # ключи для поиска вакансий (в нижнем регистре)
        self.key_words_exception = key_words_exception  # ключи исключения из названия (в нижнем регистре)
        self.key_locations = key_locations              # список локаций для работы в офисе (в нижнем регистре)
        self.key_exp = key_exp                          # ключи для опыт работы (на исключение)



    @staticmethod
    def _get_code_from_url(url):
        match = re.search(r"\d+", url)
        if match:
            return match.group(0)
        

    def start_requests(self):
        """Запрос на первую страницу поиска с вакансиями"""
        for word in self.key_words:
            start_url = f'https://hh.ru/search/vacancy?text={word}+&area=1'
            yield scrapy.Request(start_url, callback=self.parse_page)


    async def parse_page(self, response, **kwargs):
        """Парсинг страницы поиска с вакансиями"""
        for href in response.css('.serp-item__title::attr("href")').extract():
            # проверка на существование вакансии в базе
            code = self._get_code_from_url(href)
            try:
                await sync_to_async(HhItems.objects.get)(code=code)
            except HhItems.DoesNotExist:
                yield scrapy.Request(href, callback=self.parse)
        
        # переход на следующую страницу
        next_page = response.css('a[data-qa*=pager-next]::attr("href")').extract_first()
        if next_page:
            yield response.follow(next_page, callback=self.parse_page)


    def parse(self, response, **kwargs):
        title = response.css('div.vacancy-title [data-qa*=vacancy-title]::text').extract_first()

        # если название совпадает по ключому словам 
        if any(word_ in title.lower() for word_ in self.key_words) and \
            all(word_ not in title.lower() for word_ in self.key_words_exception):            
            exp = response.css('p.vacancy-description-list-item *::text').extract()
            exp = ' '.join(exp)
            
            # если нет исключений по опыту работы
            if all(exp_ not in exp.lower() for exp_ in self.key_exp):    
                location = response.css('p[data-qa*=vacancy-view-location]::text').extract_first() or \
                    response.css('[data-qa*=vacancy-view-raw-address]::text').extract_first()
                
                salary = response.css('div.vacancy-title [data-qa*=vacancy-salary]::text').extract()
                salary = ' '.join(salary)

                # если удаленно или совпадает по локации
                if any(remote_ in exp.lower() for remote_ in self.key_remotely) or \
                    any(location_ in location.lower() for location_ in self.key_locations):
                    
                    url = response.request.url
                    code = self._get_code_from_url(url)

                    item = ScraperHhItem(
                        title=title,
                        salary=salary,
                        exp=exp,
                        location=location,
                        url=url,
                        code=code,
                    )

                    yield item
                        
        


    
        
        