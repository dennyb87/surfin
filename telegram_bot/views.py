from django.http import JsonResponse
from django.conf import settings
from telegram import Bot


def start(request):
    with open("called", "w") as f:
        f.write("called")

    # bot = Bot(settings.TELEGRAM_BOT_TOKEN)
    # bot.sendMessage(chat_id=chat_id)

    return JsonResponse({"foo": "bar"})
