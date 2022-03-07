from aiogram import types
from russian import russian
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher import FSMContext
from create_bot import bot
from db import users_db
from aiogram.dispatcher.filters.state import State, StatesGroup
import links
import database


class FSMAdmin(StatesGroup):
    photo = State()
    name = State()
    description = State()


async def cm_start(message: types.Message):
    if users_db.have_user(message.from_user.id):
        await FSMAdmin.photo.set()
        await message.reply(links.create_add_text)
    else:
        await russian.change_city(message)


async def load_photo(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['photo'] = message.photo[0].file_id
    await FSMAdmin.next()
    await message.reply('Теперь введите название игрушки')


async def load_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    await FSMAdmin.next()
    await message.reply('Теперь опишите свои игрушку и свои предпочтения')


async def load_description(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['description'] = message.text
        data['user_id'] = message.from_user.id
        data['city'] = users_db.get_city_of_user(message.from_user.id)
    await database.ad_add_moderator(state)
    await message.answer('Ваше обьявление было успешно загружено. '
                         'Подождите пока один из модераторов проверит его и опубликует')
    await state.finish()


async def create_markup_and_send_message(el, user_id):
    markup = InlineKeyboardMarkup()
    b1 = InlineKeyboardButton(text=links.nxt_btn, callback_data="next_my_ad " + el.get("_id"))
    b2 = InlineKeyboardButton(text=links.del_btn, callback_data="del_my_ad " + el.get("_id"))
    markup.add(b1, b2)
    await bot.send_photo(
        user_id,
        el.get("photo"),
        f'{el.get("name")}\nОписание игрушки: {el.get("description")}',
        reply_markup=markup
    )


async def my_adds(message: types.Message):
    if users_db.have_user(message.from_user.id):
        cur_db = database.get_user_ads(message.from_user.username)
        if len(cur_db) == 0:
            await bot.send_message(message.from_user.id, links.no_add_text)
        else:
            await create_markup_and_send_message(cur_db[0], message.from_user.id)
    else:
        await russian.change_city(message)


async def next_my_add(callback: types.CallbackQuery):
    t = callback.data.split(' ')
    cur_db = database.get_user_ads(callback.from_user.username)
    last_id = int(t[1])
    id_of_last = -1
    for i in range(len(cur_db)):
        if int(cur_db[i].get("_id")) == last_id:
            id_of_last = i
    if id_of_last == -1:
        await callback.answer(links.add_has_been_delete)
    else:
        id_of_last += 1
        id_of_last %= len(cur_db)
        await create_markup_and_send_message(cur_db[id_of_last], callback.from_user.id)
        await callback.answer()


async def del_my_add(callback: types.CallbackQuery):
    t = callback.data.split(' ')
    cur_db = database.get_user_ads(callback.from_user.username)
    id_of_last = -1
    for i in range(len(cur_db)):
        if int(cur_db[i].get("_id")) == int(t[1]):
            id_of_last = i
            break
    if id_of_last == -1:
        await callback.answer(links.add_has_been_delete)
    else:
        database.delete_add_ads(t[1])
        await callback.answer(links.success_delete)
