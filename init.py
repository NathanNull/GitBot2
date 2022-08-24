#SUPER BROKEN

from website import website
from bot import main as bot
from threading import Thread

Thread(target=bot.main).start()
Thread(target=website.main).start()