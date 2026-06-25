import asyncio
import logging
import sys

from config import BOT_TOKEN as TOKEN
from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import (
   Message,
   CallbackQuery,
   ReplyKeyboardRemove,
   URLInputFile,
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command, CommandStart

from commands import (
   BOT_COMMANDS,
)
from data import get_films, add_film, Film
from keyboards import films_keyboard_markup, FilmCallback
from external import async_log_function_call
bot = BOT_TOKEN = "8420241149:AAHxI8wOmeWfWQa6VKaqoQjhz-fgCyjTTyY"


dp = Dispatcher()


class FilmForm(StatesGroup):
   name = State()
   description = State()
   rating = State()
   genre = State()
   actors = State()
   poster = State()


@dp.message(CommandStart())
@async_log_function_call
async def start(
   message: Message,
   *args,
   **kwargs,
) -> None:
   message_text = (
       f"Вітаю, {message.from_user.full_name}!\n"
       "Я перший бот Python розробника [ПІБ студента]."
   )
   await message.answer(text=message_text)


@dp.message(Command("films_list"))
@async_log_function_call
async def films(
   message: Message,
   *args,
   **kwargs,
) -> None:
   data = get_films()
   markup = films_keyboard_markup(films_list=data)
   message_text = (
       "Перелік фільмів.\n"
       "Натисніть на назву фільму для отримання деталей."
   )
   await message.answer(
       text=message_text,
       reply_markup=markup,
   )


@dp.message(Command("film_create"))
@async_log_function_call
async def film_create(
   message: Message,
   state: FSMContext,
   *args,
   **kwargs,
) -> None:
   await state.set_state(FilmForm.name)
   await message.answer(
       "Введіть назву фільму.",
       reply_markup=ReplyKeyboardRemove(),
   )


@dp.message(FilmForm.name)
@async_log_function_call
async def film_name(
   message: Message,
   state: FSMContext,
   *args,
   **kwargs,
) -> None:
   await state.update_data(name=message.text)
   await state.set_state(FilmForm.description)
   await message.answer(
       "Введіть опис фільму.",
       reply_markup=ReplyKeyboardRemove(),
   )


@dp.message(FilmForm.description)
@async_log_function_call
async def film_description(
   message: Message,
   state: FSMContext,
   *args,
   **kwargs,
) -> None:
   await state.update_data(description=message.text)
   await state.set_state(FilmForm.rating)
   await message.answer(
       "Вкажіть рейтинг фільму від 0 до 10.",
       reply_markup=ReplyKeyboardRemove(),
   )


@dp.message(FilmForm.rating)
@async_log_function_call
async def film_rating(
   message: Message,
   state: FSMContext,
   *args,
   **kwargs,
) -> None:
   await state.update_data(rating=float(message.text))
   await state.set_state(FilmForm.genre)
   await message.answer(
       "Введіть жанр фільму.",
       reply_markup=ReplyKeyboardRemove(),
   )


@dp.message(FilmForm.genre)
@async_log_function_call
async def film_genre(
   message: Message,
   state: FSMContext,
   *args,
   **kwargs,
) -> None:
   await state.update_data(genre=message.text)
   await state.set_state(FilmForm.actors)
   message_text = "Введіть акторів фільму через роздільник ', '"
   message_text += html.bold(" Обов'язкова кома та відступ після неї.")
   await message.answer(
       text=message_text,
       reply_markup=ReplyKeyboardRemove(),
   )


@dp.message(FilmForm.actors)
@async_log_function_call
async def film_actors(
   message: Message,
   state: FSMContext,
   *args,
   **kwargs,
) -> None:
   actors = [x for x in message.text.split(", ")]
   await state.update_data(actors=actors)
   await state.set_state(FilmForm.poster)
   await message.answer(
       "Введіть посилання на постер фільму.",
       reply_markup=ReplyKeyboardRemove(),
   )


@dp.message(FilmForm.poster)
@async_log_function_call
async def film_poster(
   message: Message,
   state: FSMContext,
   *args,
   **kwargs,
) -> None:
   data = await state.update_data(poster=message.text)
   film = Film(**data)
   add_film(film.model_dump())
   await state.clear()
   await message.answer(
       f"Фільм {film.name} успішно додано!",
       reply_markup=ReplyKeyboardRemove(),
   )

@dp.message(FilmForm.rating)
async def film_rating(message: Message, state: FSMContext, *args, **kwargs):
    try:
        rating = float(message.text)
    except ValueError:
        await message.answer("Будь ласка, введіть число від 0 до 10.")
        return
    await state.update_data(rating=rating)
    await state.set_state(FilmForm.genre)
    await message.answer("Введіть жанр фільму.", reply_markup=ReplyKeyboardRemove())


from aiogram.fsm.state import State, StatesGroup


class SearchActorForm(StatesGroup):
    actor = State()

@dp.message(Command("search_by_actor"))
async def search_by_actor(message: Message, state: FSMContext):
    await state.set_state(SearchActorForm.actor)
    await message.answer("Введіть ім'я актора для пошуку.")

@dp.message(SearchActorForm.actor)
async def process_actor_search(message: Message, state: FSMContext):
    actor_name = message.text.strip().lower()
    films = get_films()
    result = [f for f in films if any(actor_name in a.lower() for a in f["actors"])]

    if result:
        text = "\n\n".join([f"{f['name']} ({f['year']}) – {f['genre']}" for f in result])
        await message.answer(f"Знайдено фільми:\n{text}")
    else:
        await message.answer("Фільмів з таким актором не знайдено.")
    await state.clear()



class FilterForm(StatesGroup):
    criteria = State()

@dp.message(Command("filter_movies"))
async def filter_movies(message: Message, state: FSMContext):
    await state.set_state(FilterForm.criteria)
    await message.answer("Введіть жанр або мінімальний рейтинг (наприклад: Драма або 8.0).")

@dp.message(FilterForm.criteria)
async def process_filter(message: Message, state: FSMContext):
    films = get_films()
    query = message.text.strip().lower()
    result = []

    try:
        rating = float(query)
        result = [f for f in films if f["rating"] >= rating]
    except ValueError:
        result = [f for f in films if query in f["genre"].lower()]

    if result:
        text = "\n\n".join([f"{f['name']} ({f['year']}) – {f['genre']}, рейтинг {f['rating']}" for f in result])
        await message.answer(f"Знайдено фільми:\n{text}")
    else:
        await message.answer("Фільмів за таким критерієм не знайдено.")
    await state.clear()

@dp.message(Command("help"))
async def help_command(message: Message):
    text = (
        "Доступні команди:\n"
        "/start – привітання\n"
        "/films_list – список фільмів\n"
        "/film_create – додати новий фільм\n"
        "/search_by_actor – пошук фільмів за актором\n"
        "/filter_movies – фільтрувати фільми\n"
        "/edit_movie – редагувати фільм\n"
        "/delete_movie – видалити фільм\n"
    )
    await message.answer(text)
from aiogram.fsm.state import State, StatesGroup

class EditMovieForm(StatesGroup):
    name = State()
    rating = State()

@dp.message(Command("edit_movie"))
async def edit_movie(message: Message, state: FSMContext):
    await state.set_state(EditMovieForm.name)
    await message.answer("Введіть назву фільму, який хочете редагувати.")

@dp.message(EditMovieForm.name)
async def process_edit_name(message: Message, state: FSMContext):
    films = get_films()
    name = message.text.strip().lower()
    film = next((f for f in films if f["name"].lower() == name), None)

    if film:
        await state.update_data(name=name)
        await state.set_state(EditMovieForm.rating)
        await message.answer("Введіть новий рейтинг для цього фільму.")
    else:
        await message.answer("Фільм з такою назвою не знайдено.")
        await state.clear()

@dp.message(EditMovieForm.rating)
async def process_edit_rating(message: Message, state: FSMContext):
    try:
        new_rating = float(message.text.strip())
    except ValueError:
        await message.answer("Рейтинг має бути числом.")
        return

    data = await state.get_data()
    name = data["name"]

    films = get_films()
    for f in films:
        if f["name"].lower() == name:
            f["rating"] = new_rating

    import json
    with open("data.json", "w", encoding="utf-8") as fp:
        json.dump(films, fp, ensure_ascii=False, indent=2)

    await message.answer(f"Рейтинг фільму '{name}' оновлено до {new_rating}.")
    await state.clear()


class DeleteForm(StatesGroup):
    name = State()

@dp.message(Command("delete_movie"))
async def delete_movie(message: Message, state: FSMContext):
    await state.set_state(DeleteForm.name)
    await message.answer("Введіть назву фільму, який хочете видалити.")

@dp.message(DeleteForm.name)
async def process_delete(message: Message, state: FSMContext):
    films = get_films()
    name = message.text.strip().lower()
    new_films = [f for f in films if f["name"].lower() != name]

    if len(new_films) < len(films):
        import json
        with open("data.json", "w", encoding="utf-8") as fp:
            json.dump(new_films, fp, ensure_ascii=False, indent=2)
        await message.answer(f"Фільм '{message.text}' видалено.")
    else:
        await message.answer("Фільм з такою назвою не знайдено.")
    await state.clear()



@dp.message(Command("edit_movie"))
async def edit_movie(message: Message):
    await message.answer("Редагування ще не реалізоване. Введіть назву фільму, щоб змінити дані.")


@dp.callback_query(FilmCallback.filter())
@async_log_function_call
async def callb_film(
   callback: CallbackQuery,
   callback_data: FilmCallback,
   *args,
   **kwargs,
) -> None:
   film_id = callback_data.id
   film_data = get_films(film_id=film_id)

   film_data: dict[str, str | float]
   film = Film(**film_data)

   text = (
       f"Poster: {film.poster}\n"
       f"Фільм: {film.name}\n"
       f"Опис: {film.description}\n"
       f"Рейтинг: {film.rating}\n"
       f"Жанр: {film.genre}\n"
       f"Актори: {', '.join(film.actors)}\n"
   )
   await callback.message.answer(
       text=text,
   )


@async_log_function_call
async def main(
   *args,
   **kwargs,
) -> None:
   bot = Bot(
       token=TOKEN,
       default=DefaultBotProperties(
           parse_mode=ParseMode.HTML,
       ),
   )
   await bot.delete_webhook(drop_pending_updates=True)
   await bot.set_my_commands(BOT_COMMANDS)
   await dp.start_polling(bot)


if __name__ == "__main__":
   logging.basicConfig(level=logging.INFO, stream=sys.stdout)
   asyncio.run(main())

   