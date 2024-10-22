import asyncio
import logging
import os
import uuid

from dotenv import load_dotenv
import discord
from aiohttp import web
from discord.ext import commands
from discord.message import Message

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("discord")

# Load environment variables
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise ValueError(
        "No Discord token found. Make sure DISCORD_TOKEN is set in your environment."
    )

INTENTS = discord.Intents.default()
INTENTS.message_content = True
BOT = commands.Bot(command_prefix="!", intents=INTENTS)

@BOT.event
async def on_ready():
    """Log a message when the bot has successfully connected to Discord."""
    logger.info(f"{BOT.user} has connected to Discord!")

@BOT.event
async def on_message(message: Message):
    """Event handler for incoming Discord messages.

    This function processes incoming messages, ignoring those sent by the bot itself.
    When the bot is mentioned, it creates or fetches the appropriate threads,
    processes the message through LangGraph, and sends the response.

    Args:
        message (Message): The incoming Discord message.
    """
    print(f"Discord on_message") 
    if message.author == BOT.user:
      return
    await message.reply('Hi!', mention_author=True)

async def run_bot():
    """Run the Discord bot.

    This function starts the Discord bot and handles any exceptions that occur during its operation.
    """
    try:
        await BOT.start(TOKEN)
    except Exception as e:
        print(f"Error starting BOT: {e}")

async def main():
    """Main function to run both the Discord bot and the web server concurrently.

    This function uses asyncio.gather to run both the bot and the web server in parallel.
    """
    await asyncio.gather(run_bot())

if __name__ == "__main__":
    asyncio.run(main())