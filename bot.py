import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler

TOKEN = "PASTE_YOUR_BOT_TOKEN_HERE"

bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

group_id = None
submitted_today = set()

# ---------- PHOTO UPLOAD ----------
@dp.message(lambda m: m.photo)
async def photo_handler(msg: types.Message):
    submitted_today.add(msg.from_user.id)
    await msg.reply("✅ Good Job!")

# ---------- MORNING 8 AM MESSAGE ----------
async def morning_message():
    global submitted_today
    submitted_today = set()
    if group_id:
        await bot.send_message(
            group_id,
            "🌅 সকাল ৮টা ⏰\nআজকের study কাজের ছবি আপলোড করো 📸"
        )

# ---------- 10 AM CHECK ----------
async def ten_am_check():
    if not group_id:
        return

    members = await bot.get_chat_administrators(group_id)
    pending = []

    for m in members:
        uid = m.user.id
        if not m.user.is_bot and uid not in submitted_today:
            pending.append(
                f"<a href='tg://user?id={uid}'>{m.user.first_name}</a>"
            )

    if pending:
        await bot.send_message(
            group_id,
            "⚠️ সকাল ১০টা পার হয়ে গেছে!\n" +
            " ".join(pending) +
            "\nএখনো আজকের কাজ আপলোড করোনি ❌"
        )

# ---------- GROUP TRACK ----------
@dp.message()
async def track_group(msg: types.Message):
    global group_id
    if msg.chat.type in ["group", "supergroup"]:
        group_id = msg.chat.id

# ---------- MAIN ----------
async def main():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(morning_message, "cron", hour=8, minute=0)
    scheduler.add_job(ten_am_check, "cron", hour=10, minute=0)
    scheduler.start()

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())