from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import links
b1 = KeyboardButton(links.menu_exchange)
b2 = KeyboardButton(links.menu_create)
b3 = KeyboardButton(links.menu_my_ads)
b4 = KeyboardButton(links.menu_change_city)
rus_menu_kb_button = ReplyKeyboardMarkup(resize_keyboard=True)
rus_menu_kb_button.add(b1, b2)
rus_menu_kb_button.add(b3, b4)