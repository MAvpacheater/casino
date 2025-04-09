from aiogram import Dispatcher, types
from aiogram.types import Message
from utils import get_or_create_user, update_balance, get_balance, set_referral, transfer_coins
import random, time

BONUS_HOURLY = 25
BONUS_DAILY = 100
BONUS_HOUR = 3600
BONUS_DAY = 86400

def register_handlers(dp: Dispatcher):
    @dp.message_handler(commands=["start"])
    async def start_cmd(message: Message):
        user = get_or_create_user(message.from_user)
        ref_id = message.get_args()
        if ref_id.isdigit():
            set_referral(user['user_id'], int(ref_id))
        await message.answer(f"Привіт, {message.from_user.full_name}!\nТвій баланс: {user['balance']} коінів.")

    @dp.message_handler(commands=["balance"])
    async def balance_cmd(message: Message):
        user = get_or_create_user(message.from_user)
        await message.answer(f"У тебе {user['balance']} коінів.")

    @dp.message_handler(commands=["bonus"])
    async def bonus_cmd(message: Message):
        user = get_or_create_user(message.from_user)
        now = int(time.time())
        bonuses = []

        if now - user['last_hourly_bonus'] >= BONUS_HOUR:
            update_balance(user['user_id'], BONUS_HOURLY)
            bonuses.append(f"+{BONUS_HOURLY} коінів (щогодинний бонус)")
            user['last_hourly_bonus'] = now

        if now - user['last_daily_bonus'] >= BONUS_DAY:
            update_balance(user['user_id'], BONUS_DAILY)
            bonuses.append(f"+{BONUS_DAILY} коінів (щоденний бонус)")
            user['last_daily_bonus'] = now

        if bonuses:
            await message.answer("Отримано бонуси:\n" + "\n".join(bonuses))
        else:
            await message.answer("Бонус вже отримано. Спробуй пізніше.")

    @dp.message_handler(commands=["referral"])
    async def referral_cmd(message: Message):
        await message.answer(f"Твоє реферальне посилання:\nhttps://t.me/{(await message.bot.get_me()).username}?start={message.from_user.id}")

    @dp.message_handler(commands=["transfer"])
    async def transfer_cmd(message: Message):
        parts = message.text.split()
        if len(parts) != 3:
            await message.reply("Приклад: /transfer @username 100")
            return
        _, username, amount_str = parts
        try:
            amount = int(amount_str)
            if amount <= 0:
                raise ValueError()
        except ValueError:
            await message.reply("Неправильна сума.")
            return

        result = transfer_coins(message.from_user.id, username.replace("@", ""), amount)
        await message.reply(result)

    @dp.message_handler(commands=["guess"])
    async def guess_cmd(message: Message):
        number = random.randint(1, 10)
        await message.answer("Вгадай число від 1 до 10! Напиши відповідь.")
        dp.register_message_handler(guess_response, state=None, user_data={"number": number})

    async def guess_response(message: Message, **kwargs):
        number = kwargs['user_data']['number']
        try:
            guess = int(message.text.strip())
            if guess == number:
                update_balance(message.from_user.id, 50)
                await message.answer("🎉 Вірно! Ти отримав 50 коінів.")
            else:
                await message.answer(f"Не вгадано. Було число {number}.")
        except:
            await message.answer("Введи число.")
        dp.unregister_message_handler(guess_response)

    @dp.message_handler(commands=["roulette"])
    async def roulette_cmd(message: Message):
        result = random.choice(["червоне", "чорне", "зеро"])
        update = 100 if result == "червоне" else -50
        update_balance(message.from_user.id, update)
        await message.answer(f"🎡 Рулетка: {result.capitalize()}! {'+' if update > 0 else ''}{update} коінів.")

    @dp.message_handler(commands=["casino"])
    async def casino_cmd(message: Message):
        symbols = ["🍒", "🍋", "🍇", "💎"]
        roll = [random.choice(symbols) for _ in range(3)]
        win = 100 if len(set(roll)) == 1 else -20
        update_balance(message.from_user.id, win)
        await message.answer(f"{' '.join(roll)}\n{'🎉 Виграш!' if win > 0 else '😢 Програш.'} {'+' if win > 0 else ''}{win} коінів.")

    @dp.message_handler(commands=["minesweeper"])
    async def minesweeper_cmd(message: Message):
        grid = [random.choice(["💣", "🟩", "🟩"]) for _ in range(5)]
        if "💣" in grid:
            update = -30
            msg = "💥 Ти натрапив на міну!"
        else:
            update = 60
            msg = "✅ Успішно обійшов всі міни!"
        update_balance(message.from_user.id, update)
        await message.answer(f"{''.join(grid)}\n{msg} {'+' if update > 0 else ''}{update} коінів.")
