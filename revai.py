import discord, os
from discord.ext import commands
from discord.ext.commands import Bot
from revai.database import *

BOT_PREFIX = ('!')
TOKEN = os.environ['TOKEN']
client = Bot(command_prefix=BOT_PREFIX)
client.remove_command('help')
cogfolder = os.path.dirname(os.path.abspath(__file__)) + '/revai/cogs'
[client.load_extension(f'revai.cogs.{f.replace(".py", "")}') for f in os.listdir(cogfolder) if not f.startswith('__')]

@client.event
async def on_ready():
    for guild in client.guilds:
        await add_guild(guild)
        for channel in guild.channels:
            await add_channel(channel)
    for user in client.users:
        await add_member(user)
    print(f'{client.user.name} is now online.')

@client.command()
@commands.is_owner()
async def reload(context, cog:str):
    try:
        msg = await context.send(f'Attempting to reload {cog.capitalize()}')
        client.reload_extension(f'revai.cogs.{cog.capitalize()}')
    except Exception as er:
        try:
            await msg.edit(content=f'Failed to reload cog:\n{er}')
            await msg.edit(content=f'Attempting to load {cog.capitalize()}')
            client.load_extension(f'revai.cogs.{cog.capitalize()}')
            await msg.edit(content=f'Successfully loaded {cog.capitalize()}')
            await msg.delete()
        except Exception as e:
            await context.send(f'Failed to load unloaded cog:\n{e}')
    else:
        await msg.edit(content=f'Successfully reloaded {cog.capitalize()}')

client.run(TOKEN)
