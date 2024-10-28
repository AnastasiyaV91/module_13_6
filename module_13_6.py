from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio

"""
Импортируем необходимые модули из aiogram:
      Bot — для создания бота.
      Dispatcher — для обработки сообщений.
      types — для работы с типами сообщений и других данных.
      MemoryStorage — для хранения состояний в памяти.
      FSMContext — для работы с контекстом машины состояний.
      State и StatesGroup — для работы с состояниями.
      executor — для запуска бота.
      ReplyKeyboardMarkup - для работы с обычной клавиатурой
      KeyboardButton - для работы с кнопками
      InlineKeyboardMarkup - для работы с Inline клавиатурой
      InlineKeyboardButton - для работы с Inline кнопками
"""

api = ""
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

class UserState(StatesGroup):
    age = State()     # Возраст
    growth = State()  # Рост
    weight = State()  # Вес

kb = ReplyKeyboardMarkup(resize_keyboard=True)  # Обычная клавиатура
button1 = KeyboardButton("Рассчитать")   #  Объявление кнопки "Рассчитать"
button2 = KeyboardButton("Информация")   #  Объявление кнопки "Информация"
kb.add(button1, button2)           #  Кнопки добавляются в ряд

inline_kb = InlineKeyboardMarkup()  # Inline клавиатура
inline_button1 = InlineKeyboardButton("Рассчитать норму калорий", callback_data='calories')
inline_button2 = InlineKeyboardButton("Формулы расчёта", callback_data='formulas')
              # callback_data= - данные, которые будут отправлены в запросе обратного вызова боту при нажатии кнопки
inline_kb.add(inline_button1, inline_button2)     #  Inline кнопки добавляются в ряд

@dp.message_handler(commands=['start'])        #  Запуск функции start при вводе команды /start
async def start(message):
    await message.answer('Привет! Я бот помогающий твоему здоровью', reply_markup=kb)   #  Ответное сообщение и вызов
                                                                                        # клавиатуры из двух кнопок

@dp.message_handler(text='Рассчитать')  #  Реакция на нажатие кнопки 'Рассчитать', запуск функции main_menu
async def main_menu(message):
    await message.answer("Выберите опцию:", reply_markup=inline_kb)  #  Сообщение и вызов inline_kb клавиатуры

@dp.callback_query_handler(text='formulas')  #  Реакция на нажатие кнопки 'Формулы расчёта', запуск функции get_formulas
async def get_formulas(call):
    await call.message.answer("Для женщин: 10 х вес(кг) + 6.25 х рост(см) - 5 х возраст(г) - 161")
    await call.message.answer("Для мужчин: 10 х вес(кг) + 6.25 х рост(см) - 5 х возраст(г) - 5")

@dp.callback_query_handler(text='calories')  #  Запуск функции set_age на нажатие кнопки "Рассчитать норму калорий"
async def set_age(call):
    await call.answer()  #  Завершение вызова. Без этой команды кнопка останется не активной(некликабельной)
    await call.message.answer("Введите свой возраст")   #  Ответное сообщение
    await UserState.age.set()                           #  Ожидание работы следующего хэндлера

@dp.message_handler(state=UserState.age)        #  Запуск функции set_growth при вводе возраста
async def set_growth(message, state):
    await state.update_data(age=message.text)   #  Здесь в словаре age - ключ, введенное число - значение ключа
    await message.answer("Введите свой рост")   #  Ответное сообщение
    await UserState.growth.set()                #  Ожидание работы следующего хэндлера

@dp.message_handler(state=UserState.growth)     #  Запуск функции set_weight при вводе роста
async def set_weight(message, state):
    await state.update_data(growth=message.text)   #  Здесь в словаре growth - ключ, введенное число - значение ключа
    await message.answer("Введите свой вес")    #  Ответное сообщение
    await UserState.weight.set()                #  Ожидание работы следующего хэндлера

@dp.message_handler(state=UserState.weight)     #  Запуск функции send_calories при вводе веса
async def send_calories(message, state):
    await state.update_data(weight=message.text)   #  Здесь в словаре weight - ключ, введенное число - значение ключа
    data = await state.get_data()               # Это элемент, который позволит получить данные состояния (это словарь)
    age = int(data.get("age"))        #  Возраст, значение с ключем "age"
    growth = int(data.get("growth"))  #  Рост, значение с ключем  "growth"
    weight = int(data.get("weight"))  #  Вес, значение с ключем  "weight"
    calories1 = 10 * weight + 6.25 * growth - 5 * age + 5    #  Формула для мужчин
    calories2 = 10 * weight + 6.25 * growth - 5 * age - 161  #  Формула для женщин
    await message.answer(f"Ваша норма калорий (для мужчин): {calories1} ккал.")  #  Считаем норму калорий по формуле
                                                                                 #  Миффлина - Сан Жеора для мужчин
    await message.answer(f"Ваша норма калорий (для женщин): {calories2} ккал.")  #  Считаем норму калорий по формуле
                                                                                 # Миффлина - Сан Жеора для женщин
    await state.finish()  #  Когда машина отработала, ее нужно остановить, чтобы сохранить свое состояние

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)  #  Запуск из этого файла