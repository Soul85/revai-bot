import discord
from discord import utils
from discord.ext import commands
from Crypto.Cipher import AES
from revai.database import *
from revai.conf import key

class Owner(commands.Cog):
    """Owner only commands."""
    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.is_owner()
    async def view_message(self, ctx, id):
        with db_session:
            message = Message.get(id=id)
            cipher = AES.new(key, AES.MODE_EAX, nonce=message.nonce)
        
        await ctx.send(f'Encrypted message: {message.content}\nDecrypted message: {cipher.decrypt_and_verify(message.content, message.tag).decode()}')

    @commands.command()
    @commands.is_owner()
    async def shutdown(self, ctx):
        """Shuts down the bot in the event that manual shutdown is necessary."""
        try:
            await self.client.logout()
        except:
            self.client.clear()

def setup(client):
    client.add_cog(Owner(client))
