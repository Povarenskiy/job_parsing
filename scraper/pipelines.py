from asgiref.sync import sync_to_async

from hh.tasks import send_notification

class ScraperHhItemPipeline(object):
    async def process_item(self, item, spider):
        new_item = await sync_to_async(item.save)()
        send_notification.delay(new_item.code)
        return item
