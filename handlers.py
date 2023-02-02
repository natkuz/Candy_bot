from aiogram import types
from loader import dp
import random

max_count = 150
total = 0
new_game = False


@dp.message_handler(commands=['start', 'старт'])
async def mes_start(message: types.Message):
    global new_game
    name = message.from_user.first_name
    if not new_game:
        await message.answer(f'Привет, {name}! Давай поиграем в конфеты.\n\n'
                             f'Выбери количество конфет: '
                             f'напиши /set и через пробел количество конфет,\n\n'
                             f'а потом нажми /new_game\n\n/rules - здесь правила\n')
    else:  # добавлена возможность сброса начатой игры по команде /start
        new_game = False
        await message.answer(f'Ну что, {name}, начинаем играть заново.\n\n'
                             f'Выбери количество конфет: '
                             f'напиши /set и через пробел количество конфет,\n\n'
                             f'а потом нажми /new_game\n\n/rules - здесь правила\n')


@dp.message_handler(commands=['rules'])  # добавлено описание правил
async def mes_rules(message: types.Message):
    await message.answer('На столе лежит заданное количество конфет.\n'
                         'Играют два игрока, человек и бот, делая ход по очереди.\n'
                         'Первый ход определяется жеребьёвкой.\n'
                         'За один ход можно забрать не более чем 28 конфет.\n'
                         'Все конфеты оппонента достаются сделавшему последний ход.')


@dp.message_handler(commands=['new_game'])
async def mes_new_game(message: types.Message):
    global new_game
    global total
    global max_count
    new_game = True
    total = max_count
    await message.answer(f'Игра началась, на столе {total} конфет.')
    await lot(message)  # выбор игрока, делающего первый ход, вынесен в отдельную функцию


@dp.message_handler(commands=['set'])
async def mes_set(message: types.Message):
    global max_count
    global new_game
    name = message.from_user.first_name
    try:  # добавлена проверка, чтобы при вводе команды /set без указания числа не вылетала ошибка: IndexError
        count = message.text.split()[1]
        if not new_game:
            if count.isdigit():
                max_count = int(count)
                await message.answer(f'Конфет теперь будет {max_count}, начинаем /new_game ?')
            else:
                await message.answer(f'{name}, напишите цифрами')
        else:
            await message.answer(f'{name}, нельзя менять правила во время игры. Бери уже конфеты.')
    except IndexError:
        if new_game:  # добавлено условие, чтобы не выводилось сообщение, что Конфет будет ..., если игра уже началась
            await message.answer(f'{name}, нельзя менять правила во время игры. Бери уже конфеты.')
        else:
            await message.answer(f'Конфет будет {max_count}, начинаем /new_game ?')


@dp.message_handler()
async def mes_take_candy(message: types.Message):
    global total
    global new_game
    name = message.from_user.first_name
    count = message.text  # все вхождения message.text в функцию заменены переменной count
    if new_game:
        if count.isdigit() and 0 < int(count) < 29:
            total -= int(count)
            if total <= 0:
                await message.answer(f'{name}, ты забрал(а) последние конфеты. Ура! Это победа!')
                new_game = False
            else:
                await message.answer(f'{name} взял(а) {count} конфет. На столе осталось {total} конфет.')
                await bot_turn(message)
        else:
            await message.answer(f'{name}, надо указать ЧИСЛО от 1 до 28.')


async def bot_turn(message: types.Message):
    global total
    global new_game
    # bot_take = 0 - здесь можно не объявлять переменную bot_take
    if 0 < total < 29:
        bot_take = total
        total -= bot_take
        await message.answer(f'Бот взял {bot_take} конфет. '
                             f'На столе осталось {total} конфет и бот одержал победу!')
        new_game = False
    else:
        reminder = total % 29
        bot_take = reminder if reminder != 0 else 28
        total -= bot_take
        await message.answer(f'Бот взял {bot_take} конфет. На столе осталось {total} конфет.')


async def lot(message):
    first = random.randint(0, 1)
    if first:
        await message.answer(f'Первый ход достался тебе, {message.from_user.first_name}. Бери конфеты')
    else:
        await message.answer('Первый ход достается Candy-боту')
        await bot_turn(message)
