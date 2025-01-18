from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from telegram import Bot


@csrf_exempt
def start(request):
    # bot = Bot(settings.TELEGRAM_BOT_TOKEN)
    # bot.sendMessage(chat_id=chat_id)
    return JsonResponse({"foo": "bar"})
