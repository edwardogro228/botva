import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import Command
from dotenv import load_dotenv

# Загружаем токен из .env
load_dotenv()
TOKEN = os.getenv("TOKEN")

# Указываем ID владельца (замени на свой Telegram ID)
OWNER_ID = 380695288  

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Файл для хранения ID групп
GROUPS_FILE = "/Users/eduardgrot/Desktop/Рассылочный бот/ВА ТГ/groups.txt"

# Функция загрузки групп
def load_groups():
    if not os.path.exists(GROUPS_FILE):
        print("Файл groups.txt не найден. Создаю новый...")
        return set()

    print("Файл найден, загружаю группы...")  
    
    with open(GROUPS_FILE, "r") as file:
        lines = file.readlines()
    
    print("Содержимое файла:", lines)  

    groups = set()
    for line in lines:
        line = line.strip()
        if line:  
            try:
                group_id = int(line)
                groups.add(group_id)
            except ValueError:
                print(f"Ошибка: '{line}' не является числом!")

    print("Загруженные группы:", groups)  
    return groups

# Функция сохранения групп
def save_groups():
    print("Сохраняю группы:", registered_groups)  
    with open(GROUPS_FILE, "w") as file:
        for group_id in registered_groups:
            file.write(f"{group_id}\n")
    print("Группы сохранены!")

# Загружаем группы при запуске
registered_groups = load_groups()

def is_owner(message: Message) -> bool:
    """Проверяет, является ли отправитель владельцем бота"""
    return message.from_user.id == OWNER_ID

@dp.message(Command("register"))
async def register_group(message: Message):
    """Регистрирует группу для рассылки"""
    if message.chat.type in ['group', 'supergroup']:
        registered_groups.add(message.chat.id)
        save_groups()
        await message.answer("Группа зарегистрирована для рассылки!")
    else:
        await message.answer("Эта команда работает только в группах!")

@dp.message(Command("broadcast"))
async def broadcast_message(message: Message):
    """Рассылает текстовое сообщение и/или изображение во все зарегистрированные группы"""
    if not is_owner(message):
        await message.answer("❌ У вас нет прав на рассылку.")
        return

    if not registered_groups:
        await message.answer("Нет зарегистрированных групп для рассылки.")
        return

    text = message.text.replace("/broadcast", "").strip() if message.text else None  
    caption = message.caption.strip() if message.caption else None  
    photo = message.photo[-1] if message.photo else None  

    if not text and not photo:
        await message.answer("Введите текст или отправьте изображение с подписью после команды /broadcast")
        return

    for group_id in registered_groups:
        try:
            if photo:
                await bot.send_photo(group_id, photo.file_id, caption=caption)  
            if text:
                await bot.send_message(group_id, text)  
        except Exception as e:
            print(f"Ошибка отправки в {group_id}: {e}")

    await message.answer("✅ Рассылка завершена!")

@dp.message(lambda message: message.photo)
async def broadcast_photo(message: Message):
    """Рассылает фото с подписью во все зарегистрированные группы"""
    if not is_owner(message):
        await message.answer("❌ У вас нет прав на рассылку.")
        return

    if not registered_groups:
        await message.answer("Нет зарегистрированных групп для рассылки.")
        return

    photo = message.photo[-1].file_id  
    caption = message.caption or ""

    for group_id in registered_groups:
        try:
            await bot.send_photo(group_id, photo, caption=caption)
        except Exception as e:
            print(f"Ошибка отправки в {group_id}: {e}")

    await message.answer("✅ Фото разослано!")

async def main():
    """Основной цикл бота"""
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
