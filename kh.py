import asyncio
import random
from datetime import datetime, timedelta
import sqlite3
from aiogram import Dispatcher, filters, Bot, F, html
from aiogram.types import (Message, FSInputFile, CallbackQuery, URLInputFile, InlineKeyboardMarkup, InlineKeyboardButton, inline_keyboard_markup, message, )
from aiogram.enums import ParseMode

dp = Dispatcher()

db = sqlite3.connect("bot.db")
cursor = db.cursor()


cursor.execute("""
CREATE TABLE IF NOT EXISTS user (
    user_id INTEGER PRIMARY KEY,
    toman INTEGER DEFAULT 0,
    is_banned INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    xp INTEGER DEFAULT 0,
    last_toman TEXT
    
)
"""
)

def required_xp(level):
    return round(100 * (1.20 ** (level - 1)))

@dp.message(filters.CommandStart())
async def start(message: Message):
    username = message.from_user.username
    first_name = message.from_user.first_name


    user_id = message.from_user.id

    cursor.execute(
        "INSERT OR IGNORE INTO user (user_id) VALUES (?)",
        (user_id,)
    )

    db.commit()

    await message.answer(
        text=f"""
سلام دوست عزیز من❤️

این یک ربات بازی تلگرامی هستش که در مورد دماغ بسیار بزرگ یک شخص است

شما با اسم {html.bold(first_name)} و با یوزرنیم {html.bold(username)} ثبت شدید!
        """,
        parse_mode=ParseMode.HTML
    )


@dp.message(filters.Command("chenar"))
async def chenar(message: Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name

    cursor.execute("SELECT * FROM user WHERE user_id = ?", (user_id,))
    result1 = cursor.fetchone()

    if result1 is None:
        cursor.execute("INSERT INTO user (user_id) VALUES (?)", (user_id,))
        db.commit()

    cursor.execute("SELECT toman, xp, level, last_toman FROM user WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()

    toman =result[0]
    xp = result[1]
    level = result[2]
    last_toman =result[3]

    now = datetime.now()
    cooldown = timedelta(minutes=5)

    if last_toman is not None:

        last_toman_time = datetime.fromisoformat(last_toman)

        passed_time = now - last_toman_time

        if passed_time < cooldown:

            remaining = cooldown - passed_time

            minutes = remaining.seconds // 60
            seconds = remaining.seconds % 60

            await message.answer(
                text=f"""
شما به تازگی دماغ پوینت خودتون رو دریافت کردید لطفا بعد از {minutes}:{seconds} این تایم تلاش کنید برای دریافت💕
                """
            )

            return

    earned_toman = random.randint(50, 100)
    earned_xp = random.randint(10, 30)

    toman += earned_toman
    xp += earned_xp

    old_level = level

    while xp >= required_xp(level):

        need_xp = required_xp(level)

        xp -= need_xp

        level += 1

    last_toman = now.isoformat()

    cursor.execute("UPDATE user SET toman = ?, xp = ?, level = ?, last_toman =?", (toman, xp, level,last_toman))
    db.commit()

    if level > old_level:
        text += (
            f"\n\n🎉 Level Up!"
            f"\n{old_level} → {level}"
        )

    await message.answer(
        text=f"""
🎉 لول اپ شدی!
{old_level} → {level}
        """
    )

    await message.answer(
        text=f"""
شما {earned_toman} دماغ پوینت دریافت کردید و موجودی جدی شما {toman} انقدره و شما {earned_xp} اکس پی دماغی دریافت کردید
added {earned_toman} toman to your walet now you have {toman} and you earned {earned_xp} xp 
        """
    )

@dp.message(filters.Command("bank"))
async def bank(message: Message):
    user_id = message.from_user.id
    frist_name = message.from_user.first_name
    cursor.execute(
        """
        SELECT toman FROM user WHERE user_id = ?
        """,
        (user_id, )
    )

    result = cursor.fetchone()
    toman = result[0]

    await message.reply_photo(
        photo="https://files.catbox.moe/zr8c7c.jpg",
        caption=f"""
کاربر {html.bold(frist_name)} شما دارای {html.bold(toman)} دماغ پوینت هستید
        """,
        parse_mode=ParseMode.HTML
    )

#-----------------------------------------------------------------------------------------------------

async def main():
    bot = Bot(token="8930946441:AAHvb6bGZ68_jKbxFN-etuoPG_uBisw3G-Y")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())