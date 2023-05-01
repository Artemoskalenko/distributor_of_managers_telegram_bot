from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import db

TOKEN = 'API_TOKEN'
ADMIN_ID = 5555555555
GROUP_ID = -1000000000000
PYTHONANYWHERE_LOGIN = 'login'

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

index = 0
last_user = "None"
usernames = []
text_to_photo = None


def get_post_url():
    """Генерирует ссылку на следующего менеджера"""
    global index
    global usernames
    if len(usernames) == 0:
        with open(f'/home/{PYTHONANYWHERE_LOGIN}/bot/managers.txt') as file:
            lines = file.readlines()
            for line in lines:
                if '\n' in line:
                    line = line.replace('\n', '')
                usernames.append(line)
    url = 'https://t.me/' + usernames[index]
    index += 1
    if index > len(usernames) - 1:
        index = 0

    return url


@dp.message_handler(commands=['start'])
async def send_post(message: types.Message):
    global last_user
    global text_to_photo
    chat_id = message.from_user.id
    username = message.from_user.username
    url = get_post_url()
    photo = open(f'/home/{PYTHONANYWHERE_LOGIN}/bot/media/photo.jpg', 'rb')

    if text_to_photo is None:
        with open(f'/home/{PYTHONANYWHERE_LOGIN}/bot/text.txt', encoding='utf8') as text:
            text_to_photo = text.read()

    if len(text_to_photo) > 1:
        await dp.bot.send_photo(
            chat_id=chat_id,
            photo=photo,
            caption=text_to_photo,
            reply_markup=InlineKeyboardMarkup(row_width=2).add(InlineKeyboardButton('Напиши мне!', url=url))
        )
    else:
        await dp.bot.send_photo(
            chat_id=chat_id,
            photo=photo,
            reply_markup=InlineKeyboardMarkup(row_width=2).add(
                InlineKeyboardButton('Напиши мне!', url=url))
        )

    if str(username) != "None" and str(username) != last_user:
        last_user = str(username)
        await dp.bot.send_message(ADMIN_ID, f"@{username} вошёл в бота\nМенеджер: @{url[13:]}")
        await dp.bot.send_message(GROUP_ID, f"@{username} вошёл в бота\nМенеджер: @{url[13:]}")
        db.tracking(url[13:])
    elif str(username) == "None":
        await dp.bot.send_message(ADMIN_ID, f"{message.from_user.first_name} вошёл в бота\nМенеджер: @{url[13:]}")
        await dp.bot.forward_message(ADMIN_ID, from_chat_id=chat_id, message_id=message.message_id)
        await dp.bot.send_message(GROUP_ID, f"{message.from_user.first_name} вошёл в бота\nМенеджер: @{url[13:]}")
        await dp.bot.forward_message(GROUP_ID, from_chat_id=chat_id, message_id=message.message_id)
        db.tracking(url[13:])


@dp.message_handler(commands=['today_statistic'])
async def today_statistic(message: types.Message):
    statistic = db.get_today_statistic()
    output = ""
    all_users = 0
    for manager, users in statistic:
        output += f"@{manager}: {users}\n"
        all_users += users
    output = f"Всего пользователей за сегодня: {all_users}\n" + output
    await dp.bot.send_message(ADMIN_ID, output)


@dp.message_handler(commands=['yesterday_statistic'])
async def yesterday_statistic(message: types.Message):
    statistic = db.get_yesterday_statistic()
    output = ""
    all_users = 0
    for manager, users in statistic:
        output += f"@{manager}: {users}\n"
        all_users += users
    output = f"Всего пользователей за вчера: {all_users}\n" + output
    await dp.bot.send_message(ADMIN_ID, output)


@dp.message_handler(lambda message: message.text.startswith('/20') and len(message.text) == 11)
async def get_statistic(message: types.Message):
    date = str(message.text[1:])
    statistic = db.get_statistic(date)
    output = ""
    all_users = 0
    for manager, users in statistic:
        output += f"@{manager}: {users}\n"
        all_users += users
    output = f"Всего пользователей за {date}: {all_users}\n" + output
    await dp.bot.send_message(ADMIN_ID, output)


@dp.message_handler(lambda message: message.text.startswith('/20') and len(message.text) == 22)
async def get_large_statistic(message: types.Message):
    date1 = str(message.text[1:11])
    date2 = str(message.text[12:])
    statistic = db.get_large_statistic(date1, date2)
    output = ""
    result = {}
    all_users = 0
    for manager, users in statistic:
        if manager in result:
            result[manager] += users
        else:
            result[manager] = users
        all_users += users
    for manager in result:
        output += f"@{manager}: {result[manager]}\n"
    output = f"Всего пользователей за указанный период: {all_users}\n" + output
    await dp.bot.send_message(ADMIN_ID, output)


@dp.message_handler(commands=['get_chat_id'])
async def get_chat_id(message: types.Message):
    chat_id = message.chat.id
    await dp.bot.send_message(chat_id, f"Айди группы: {chat_id}")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
