from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData


class FilmCallback(CallbackData, prefix="film", sep=";"):
    id: int
    name: str


def films_keyboard_markup(films_list: list[dict]):
    builder = InlineKeyboardBuilder()
    builder.adjust(1)

    for index, film_data in enumerate(films_list):
        name = film_data.get("name", "Без назви")
        cb = FilmCallback(id=index, name=name)

        builder.button(
            text=name,
            callback_data=cb.pack()
        )

    return builder.as_markup()
