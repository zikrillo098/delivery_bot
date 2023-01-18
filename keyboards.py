from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup


def generate_categories(categories: list):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
    buttons = []
    for category in categories:
        btn = KeyboardButton(text=category[0])
        buttons.append(btn)
    markup.add(*buttons)
    return markup


def generate_download(image_id):
    markup = InlineKeyboardMarkup()
    download = InlineKeyboardMarkup(text='Скачать картинку', callback_data=f'download_{image_id}')
    markup.add(download)
    return markup
