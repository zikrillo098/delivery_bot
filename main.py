import random
from aiogram import Dispatcher, executor, Bot
from aiogram.types import Message, CallbackQuery
import os
from dotenv import load_dotenv
from keyboards import generate_categories, generate_download
import sqlite3
import re

load_dotenv()
TOKEN = os.getenv('TOKEN')
bot = Bot(TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start', 'help', 'about'])
async def command_start(message: Message):
    chat_id = message.chat.id
    print(message.from_user.username)
    await bot.send_message(chat_id, f'Привет, {message.from_user.username} здесь вы найдете обои на любой вкус')
    await show_categories(message)


async def show_categories(message: Message):
    chat_id = message.chat.id
    db = sqlite3.connect('wallpapers.db')
    cursor = db.cursor()
    cursor.execute('''
        SELECT category_name from categories;
    ''')
    categories = cursor.fetchall()
    db.close()
    await bot.send_message(chat_id, 'Выберите категорию ', reply_markup=generate_categories(categories))


@dp.message_handler(content_types=['text'])
async def get_image(message: Message):
    category = message.text
    chat_id = message.chat.id
    await message.answer(f'Вы выбрали категорию "{category}"')
    db = sqlite3.connect('wallpapers.db')
    cursor = db.cursor()
    cursor.execute('''
    SELECT category_id FROM categories
    WHERE category_name = ?
    ''', (category,))
    category_id = cursor.fetchone()[0]
    cursor.execute('''
    SELECT image_link FROM images WHERE category_id = ?
    ''', (category_id,))
    image_links = cursor.fetchall()
    random_index = random.randint(0, len(image_links) - 1)
    random_image_link = image_links[random_index][0]
    resolution = re.search(r'[0-9]+x[0-9]+', random_image_link)[0]#1080x1980
    print(resolution)
    cursor.execute('''
    SELECT image_id FROM images WHERE image_link = ?;
    ''', (random_image_link,))
    image_id = cursor.fetchone()[0]
    db.close()
    try:
        await bot.send_photo(chat_id=message.chat.id,
                             photo=random_image_link,
                             caption=f'Разрешение изображения {resolution}',
                             reply_markup=generate_download(image_id)
                             )
    except Exception as e:
        resize_image_link = random_image_link.replace(resolution, '1920x1080')
        await bot.send_photo(chat_id=chat_id,
                             photo=resize_image_link,
                             caption=f'Разрешение изображения {resolution} ИЗМЕНИЛИ!',
                             reply_markup=generate_download(image_id))


@dp.callback_query_handler(lambda call: 'download' in call.data)
async def download_phot(call: CallbackQuery):
    chat_id = call.message.chat.id
    image_id = call.data.split('_')[1]
    db = sqlite3.connect('wallpapers.db')
    cursor = db.cursor()
    cursor.execute('''
    SELECT image_link FROM images WHERE image_id = ?
    ''', (image_id,))
    image_link = cursor.fetchone()[0]
    db.close()

    try:
        await call.message.answer_document(document=image_link)
    except Exception as e:
        resolution = re.search(r'[0-9]+x[0-9]+', image_link)[0]
        resize_image_link = image_link.replace(resolution, '1920x1080')
        await call.message.answer_document(document=resize_image_link)
        await call.message.answer(
            f'Мы пытались спарсить но не вышло в самом выском качестве вот вам ссылка можете перейти и сами скачть'
            f'данную фотографию в самом высоком разрешении'
            f'\n {image_link}')


executor.start_polling(dp, skip_updates=True)
