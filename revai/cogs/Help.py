import discord, os
from discord.ext import commands

cogfolder = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/cogs'

class Help(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def help(self, context, search:str = None):
        cogs = [self.client.get_cog(cog.replace('.py', '')) for cog in os.listdir(cogfolder) if not cog.startswith('__') and cog != 'Help.py' and cog != 'Events.py' and cog != 'Eval.py']
        search = search.capitalize() if search != None else None
        commandlist = []
        for cog in cogs:
            for command in cog.get_commands():
                commandlist.append(command.qualified_name.capitalize())
        if search in [cog.qualified_name for cog in cogs]:
            embed = discord.Embed(title=search.capitalize())
            for command in self.client.get_cog(search).get_commands():
                embed.add_field(name=f'**{command.qualified_name.capitalize()}**', value=command.help, inline=False)
        elif search in commandlist:
            command = self.client.get_command(search.lower())
            embed = discord.Embed(title=command.qualified_name.capitalize(), description=command.help)
            embed.add_field(name='**Usage**', value=command.usage)
        else:
            embed = discord.Embed(title='Help')
            for cog in cogs:
                embed.add_field(name=f'**{cog.qualified_name.capitalize()}**', value=cog.description, inline=False)
        await context.send(embed=embed)

def setup(client):
    client.add_cog(Help(client))