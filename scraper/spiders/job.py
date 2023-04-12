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
        

    @staticmethod
    @sync_to_async
    def _get_item_from_database(code):
        return HhItems.objects.filter(code=code).first()
        

    def start_requests(self):
        """Запрос на первую страницу поиска с вакансиями"""
        for word in self.key_words:
            start_url = f'https://hh.ru/search/vacancy?area=1&ored_clusters=true&text={word}&order_by=publication_time'
            yield scrapy.Request(start_url, callback=self.parse_page)


    async def parse_page(self, response, **kwargs):
        """Парсинг страницы поиска с вакансиями"""
        for item in response.css('span[data-page-analytics-event*=vacancy_search_suitable_item]'):
            
            href = item.css('a.serp-item__title::attr("href")').extract_first()
            code = self._get_code_from_url(href)
            
            # проверка на существование вакансии в базе
            item_from_database= await self._get_item_from_database(code)
            if not item_from_database:
                
                title = item.css('a.serp-item__title::text').extract_first()
                # если название совпадает по ключевым словам 
                if any(word_ in title.lower() for word_ in self.key_words) and \
                    all(word_ not in title.lower() for word_ in self.key_words_exception):            

                    yield scrapy.Request(href, callback=self.parse, meta={'code': code, 'title': title})
        
        # переход на следующую страницу
        next_page = response.css('a[data-qa*=pager-next]::attr("href")').extract_first()
        if next_page:
            yield response.follow(next_page, callback=self.parse_page)


    def parse(self, response, **kwargs):

        title = response.meta.get('title')
        code = response.meta.get('code')

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
    
                item = ScraperHhItem(
                    title=title,
                    salary=salary,
                    exp=exp,
                    location=location,
                    url=url,
                    code=code,
                )

                yield item
                    
    


    
        
        