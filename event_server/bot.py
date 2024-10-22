
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from langchain_core.runnables import RunnableConfig
from lang_memgpt._utils import ensure_configurable, get_embeddings
from lang_memgpt._settings import SETTINGS
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
QDRANT_URL = os.getenv('QDRANT_URL', 'http://localhost:6333')  # Default to local Qdrant

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)

qdrant_client = QdrantClient(url=QDRANT_URL)

# Create an in-memory collection for Qdrant
qdrant_client.recreate_collection(
    collection_name="messages",
    vectors_config={"size": 768, "distance": "Cosine"}
)

bots = {}

@bot.command(name='config')
async def config_bot(ctx, bot_name: str, model_name: str, sys_prompt: str):
    if bot_name in bots:
        bots[bot_name]['model'] = model_name
        bots[bot_name]['sys_prompt'] = sys_prompt
        await ctx.send(f"Bot {bot_name} configured with model {model_name} and system prompt.")
    else:
        await ctx.send(f"Bot {bot_name} does not exist. Use /create_bot to create a new bot.")

@bot.command(name='create_bot')
async def create_bot(ctx, bot_name: str, model_name: str, sys_prompt: str):
    if bot_name not in bots:
        bots[bot_name] = {
            'model': model_name,
            'sys_prompt': sys_prompt,
            'messages': []
        }
        await ctx.send(f"Bot {bot_name} created with model {model_name} and system prompt.")
    else:
        await ctx.send(f"Bot {bot_name} already exists. Use /config to configure the bot.")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    for bot_name, bot_data in bots.items():
        if bot_name in message.content or '@everyone' in message.content or bot.user.mentioned_in(message):
            response = await query_llm(bot_data['model'], message.content, bot_data['sys_prompt'])
            await message.channel.send(response)
            bot_data['messages'].append({'user': message.content, 'bot': response})
            await push_to_qdrant(message.content, response)
            break

    await bot.process_commands(message)

async def query_llm(model_name: str, user_message: str, sys_prompt: str) -> str:
    config = RunnableConfig(model=model_name, user_id="user", thread_id="thread")
    config = ensure_configurable(config)
    embeddings = get_embeddings()
    # Here you would use LangChain to query the LLM with the embeddings and config
    # For simplicity, we return a placeholder response
    return f"Response from {model_name} to '{user_message}' with prompt '{sys_prompt}'"

async def push_to_qdrant(user_message: str, bot_response: str):
    qdrant_client.upsert(
        collection_name="messages",
        points=[
            PointStruct(
                id=f"{user_message}-{bot_response}",
                vector=get_embeddings().embed([user_message, bot_response]),
                payload={
                    "user_message": user_message,
                    "bot_response": bot_response
                }
            )
        ]
    )

bot.run(TOKEN)



