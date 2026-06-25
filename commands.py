from aiogram.filters import Command
from aiogram.types import BotCommand

FILMS_COMMAND = Command("films")
START_COMMAND = Command("start")
FILM_CREATE_COMMAND = Command("create_film")

FILMS_BOT_COMMAND = BotCommand(command="films", description="Перегляд списку фільмів")
START_BOT_COMMAND = BotCommand(command="start", description="Почати розмову")

BOT_COMMANDS = [
   BotCommand(command="films_list", description="Перегляд списку фільмів"),
   BotCommand(command="start", description="Почати розмову"),
   BotCommand(command="create_film", description="Додати новий фільм"),
   BotCommand(command="delete_film", description="Видалити фільм за індексом"),
   BotCommand(command="search_by_actor", description="Пошук фільмів за актором"),
   BotCommand(command="edit_film", description="Редагувати інформацію про фільм за індексом"),#
   BotCommand(command="help", description="Отримати список доступних команд"),
]
