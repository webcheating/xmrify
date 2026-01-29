import asyncio
import aiohttp
from aiogram import Bot, Dispatcher
from aiogram.types import InputFile
import matplotlib.pyplot as plt
from io import BytesIO
from aiogram.types import InputMediaPhoto, FSInputFile
from dotenv import load_dotenv, dotenv_values
import os
from chart import generate_chart

load_dotenv()
bot_token = os.getenv("bot_token")
chat_id = os.getenv("chat_id")

bot = Bot(token=bot_token)
dp = Dispatcher()
THRESHOLD = 5.00
CHECK_INTERVAL = 333
xmr_history = []
zec_history = []

#price_url = "https://api.coingecko.com/api/v3/simple/price?ids=monero,zcash&vs_currencies=usd"
xmr_url = "https://api.coingecko.com/api/v3/simple/price?ids=monero&vs_currencies=usd"
zec_url = "https://api.coingecko.com/api/v3/simple/price?ids=zcash&vs_currencies=usd"

async def get_price(url, coin):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()
            print(f"[debug] data: {data}")
            return data[coin]['usd']

async def send_price_alert(xmr_price, zec_price, xmr_old_price, zec_old_price, startup=False):
    if startup:
        startup_msg = f"[+] started\n\n[*] XMR price:  ${xmr_price:.2f}\n[*] ZEC price: ${zec_price:.2f}"
        generate_chart('dual')
        await bot.send_photo(chat_id=chat_id, photo=FSInputFile("img/xmr_zec.png"), caption=startup_msg)
        #generate_chart("monero")
        #generate_chart("zcash")
        #startup_charts = [
        #    InputMediaPhoto(
        #        media=FSInputFile("img/monero.png"),
        #        caption=startup_msg
        #    ),
        #    InputMediaPhoto(
        #        media=FSInputFile("img/zcash.png")
        #    )
        #]
    else:
        xmr_diff = xmr_price - xmr_old_price
        zec_diff = zec_price - zec_old_price
        #direction = "↑" if diff > 0 else "↓"
        direction_up = "↑"
        direction_down = "↓"
        if xmr_diff > 0:
            xmr_msg = f"[!] monero (XMR) {direction_up} increased by ${abs(xmr_diff):.2f}\n\n[*] current price: ${xmr_price:.2f}"
        else:
            xmr_msg = f"[!] monero (XMR) {direction_down} dropped by ${abs(xmr_diff):.2f}\n\n[*] current price: ${xmr_price:.2f}"
        if zec_diff > 0:
            zec_msg = f"[!] zcash (ZEC) {direction_up} increased by ${abs(zec_diff):.2f}\n\n[*] current price: ${zec_price:.2f}"
        else:
            zec_msg = f"[!] zcash (ZEC) {direction_down} dropped by ${abs(zec_diff):.2f}\n\n[*] current price: ${zec_price:.2f}"
    
        if xmr_msg:
            generate_chart('single', 'monero')
            await bot.send_photo(chat_id=chat_id, photo=FSInputFile("img/monero.png"), caption=xmr_msg)
        elif zec_msg:
            generate_chart('single', 'zcash')
            await bot.send_photo(chat_id=chat_id, photo=FSInputFile("img/zcash.png"), caption=zec_msg)
        else:
            pass
    #await bot.send_photo(chat_id=chat_id, photo=FSInputFile("img/xmr_zec.png"), caption=startup_msg)
    #await send_price_chart()
    #news = await get_xmr_news()
    #if news:
    #    await bot.send_message(chat_id=chat_id, text=f"[*] monero latest news:\n\n{news}")

async def price_monitor():
    xmr_last_price = await get_price(xmr_url, "monero")
    xmr_history.append(xmr_last_price)
    zec_last_price = await get_price(zec_url, "zcash")
    zec_history.append(zec_last_price)

    await send_price_alert(xmr_last_price, zec_last_price, None, None, startup=True)

    while True:
        await asyncio.sleep(CHECK_INTERVAL)
        try:
            xmr_current_price = await get_price(xmr_url, "monero")
            xmr_history.append(xmr_current_price)
            zec_current_price = await get_price(zec_url, "zcash")
            zec_history.append(zec_current_price)
            print(f"[debug] XMR diff: {xmr_current_price - xmr_last_price}\n[debug] ZEC diff: {zec_current_price - zec_last_price}\n\n")
            if abs(xmr_current_price - xmr_last_price) >= THRESHOLD:
                await send_price_alert(xmr_current_price, zec_current_price, xmr_last_price, zec_last_price)
                xmr_last_price = xmr_current_price
            if abs(zec_current_price - zec_last_price) >= THRESHOLD:
                await send_price_alert(xmr_current_price, zec_current_price, xmr_last_price, zec_last_price)
                zec_last_price = zec_current_price
        except Exception as e:
            print("Error:", e)

async def stats_command():
    generate_chart('dual')
    msg = f"[+] ok\n\n[*] XMR price:  ${xmr_price:.2f}\n[*] ZEC price: ${zec_price:.2f}"
    await bot.send_photo(chat_id=chat_id, photo=FSInputFile("xmr_zec.png"), caption=msg)

async def main():
    asyncio.create_task(price_monitor())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

