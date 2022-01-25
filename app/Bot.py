import asyncio
from aiogram import Bot, Dispatcher, executor, types

from app.Configuration import get_bot_token, get_user_id
from app.Users import get_lst_users
from app.logs import logger
from main import working_lines_for_bot, regime_lines_for_bot


bot = Bot(token=get_bot_token(), parse_mode='Markdown')
dp = Dispatcher(bot)
loop = asyncio.new_event_loop()
users = get_lst_users()


def send_msg(line, n): 
    async def send_warning(line, n):
        if users[n].quantity_notifications <= 5:
            await bot.send_message(users[n].id, f'{line.name_line} готова к остановке.')
            
        if users[n].quantity_notifications == 6:
            await bot.send_message(users[n].id, f'Уведомления отключены.')

    users[n].quantity_notifications += 1
    if users[n].quantity_notifications > 6: return
    loop.create_task(send_warning(line, n))

def auth(func):
    async def wrapper(message):
        if message ['from']['id'] not in get_user_id():
            logger.warning(f'{message.from_user.username}: {message.from_user.id}.  Несанкционированная попытка входа в бота')
            return await message.answer('Несанкционированная попытка входа')
        return await func(message)
    return wrapper

@dp.message_handler(commands=['start', 'help'])
@auth
@logger.catch
async def send_help(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ['Объем', 'Бутылки']
    buttons1 = ['Режимы']
    buttons2 = ['Включить оповещения', 'Отключить оповещения']
    keyboard.add(*buttons)
    keyboard.add(*buttons1)
    keyboard.add(*buttons2)
    text = ('/help - вызвать помощника \n'
            'Объем - получить информацию о обьеме \n'
            'Бутылки - получить информацию о количестве бутылок \n'
            'Режимы - получить информацию о всех включенных режимах \n'
            'Включить оповещения - включить уведомления \n'
            'Отключить оповещения - остановить уведомления')
    await message.answer(text, reply_markup=keyboard)

@dp.message_handler(lambda message: message.text in ['Объем', 'Обьем'])
@auth
@logger.catch
async def get_volume(message: types.Message):
    logger.info(f'{message.from_user.username}: {message.from_user.id}. Запрос объема')
    lines = working_lines_for_bot()
    if len(lines) == 0: return await message.answer('Нет активных линий')
    
    text = ''
    for line in lines: 
        text += f'{line.name_line}: {line.get_alko_volume()}. Указанное значение для оповещений: {line.volume_to_stop}.\n'
    await message.answer(text)


@dp.message_handler(lambda message: message.text in ['Бутылки'])
@auth
@logger.catch
async def get_bottles(message: types.Message):
    logger.info(f'{message.from_user.username}: {message.from_user.id}. Запрос бутылок')
    lines = working_lines_for_bot()
    if len(lines) == 0: return await message.answer('Нет активных линий')
    
    text = ''
    for line in lines:
        text += f'{line.name_line}: {line.name_product}. Количество бутылок: {line.get_n_bottles()}\n'
    await message.answer(text)

@dp.message_handler(lambda message: message.text == 'Режимы')
@auth
@logger.catch
async def get_regime(message: types.Message):
    logger.info(f'{message.from_user.username}: {message.from_user.id}. Запрос режимов')
    await message.answer(regime_lines_for_bot())


@dp.message_handler(lambda message: message.text == 'Отключить оповещения')
@auth
@logger.catch
async def turn_on_send_msg(message: types.Message):
    for index, user in enumerate(users):
        if user.id == message.from_user.id: 
            user.quantity_notifications = 10
            await bot.send_message(users[index].id, 'Уведомления отключены.')

@dp.message_handler(lambda message: message.text == 'Включить оповещения')
@auth
@logger.catch
async def turn_on_send_msg(message: types.Message):
    for index, user in enumerate(users):
        if user.id == message.from_user.id: 
            user.quantity_notifications = 0
            await bot.send_message(users[index].id, 'Уведомления включены.')


def start_bot():
    asyncio.set_event_loop(loop)
    executor.start_polling(dp, skip_updates=True)
    loop.close()