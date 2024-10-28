import disnake
from disnake.ext import commands
import os
import config

bot = commands.Bot(command_prefix='!', intents=disnake.Intents.all())

def load_extensions():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            bot.load_extension(f'cogs.{filename[:-3]}')

@bot.event
async def on_ready():
    print(f'БОТ ВКЛЮЧЕН')

load_extensions()

bot.run(config.token)