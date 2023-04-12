from django.db import models


class HhItems(models.Model):
    """Модель для записи информации о вакансии с HH"""
    code = models.IntegerField('Код вакансии', db_index=True, null=True)
    title = models.CharField('Название вакансии', max_length=250, null=True) 
    salary = models.CharField('Зарплата', max_length=100, null=True) 
    exp = models.CharField('Опыт и режим работы', max_length=100, null=True) 
    url = models.CharField('Ссылка на вакансию', max_length=250, null=True) 
    location = models.CharField('Место работы', max_length=100, null=True) 
    last_update = models.DateTimeField('Время последнего обновления', auto_created=True, null=True)


    def __str__(self) -> str:
        return str(self.code)
                        