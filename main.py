# main.py
import asyncio
import logging

from pyrogram import Client
from pyrogram.errors import FloodWait

from bot import check_users_ready
from config import API_HASH, API_ID


async def main():
    logging.basicConfig(level=logging.INFO)
    bot = Client("ChatMastersbot", api_id=API_ID, api_hash=API_HASH)

    try:
        await bot.start()
        asyncio.create_task(check_users_ready(bot))
        while True:
            # Keep the bot running by sleeping for 60 seconds
            await asyncio.sleep(60)
    except FloodWait as e:
        wait_time = e.x
        logging.warning(
            f"Подождите {wait_time} секунд перед повторной попыткой")
        await asyncio.sleep(wait_time)
        await main()  # Retry main function after waiting
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        # Handle the error gracefully or terminate the program

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError as e:
        logging.error(f"RuntimeError: {e}")
        # Take additional action here, such as restarting the program or logging the error to a file
        # For example, you could restart the program by calling main() again
        logging.info("Restarting the program...")
        asyncio.run(main())


# async def main():
 #   await handlers_main()
  #  bot = Client("ChatMastersbot", api_id=API_ID, api_hash=API_HASH)

   # try:
    #    await bot.start()
    #   asyncio.create_task(check_users_ready(bot))
    #  await bot.idle()  # Bot remains active and responds to incoming messages
   # except Exception as e:
    #    logging.error(f"An error occurred: {e}")
    #   traceback.print_exc()  # Print full traceback
    #  await bot.stop()

# if __name__ == "__main__":
 #   logging.basicConfig(level=logging.INFO)
  #  asyncio.run(main())
