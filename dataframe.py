# dataframe.py
import asyncio
import logging

import pandas as pd
from telethon.sync import TelegramClient
from transformers import pipeline

from config import API_HASH, API_ID

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():

    api_id = API_ID
    api_hash = API_HASH

    client = TelegramClient('session_name', api_id, api_hash)

    await client.start()

    chat = 'https://t.me/SuperChatMaster3000_bot'

    data_item = []
    async for item in client.iter_participants(chat):
        data_item.append([item.first_name, item.last_name, item.id])

    df_participants = pd.DataFrame(
        data_item, columns=['first_name', 'last_name', 'id'])

    data_message = []
    async for message in client.iter_messages(chat, limit=100):
        data_message.append([message.sender_id, message.text])

    df_messages = pd.DataFrame(data_message, columns=['user_id', 'text'])

    df_messages.to_csv('messages.csv', index=False, encoding='utf-8')

    df_op = pd.read_csv('messages.csv', encoding="utf-8")

    model = pipeline("sentiment-analysis",
                     "blanchefort/rubert-base-cased-sentiment")

    sentiments = []
    for text in df_messages["text"]:
        result = model(text)[0]
        sentiments.append(result["label"])

    df_messages["Sentiment"] = pd.Series(sentiments)

    df_positive = df_messages[df_messages["Sentiment"] == "POSITIVE"]
    df_negative = df_messages[df_messages["Sentiment"] == "NEGATIVE"]

    logger.info("Положительные высказывания:")
    logger.info(df_positive)
    logger.info("\nОтрицательные высказывания:")
    logger.info(df_negative)

if __name__ == "__main__":
    asyncio.run(main())
