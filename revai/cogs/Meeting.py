import discord, arrow
from collections import defaultdict
from discord.ext import commands, tasks
from datetime import datetime
from revai.database import *

class Meeting(commands.Cog):
    """Meeting commands."""
    def __init__(self, client):
        self.client = client
        self.schedule.start()

    @commands.command(usage='`!meetup 1-31-2021 12:00PM something @everyone because tomorrow is February`')
    async def meetup(self, ctx, date, time, name, invitations: commands.Greedy[discord.Member], *, reason=None):
        """Schedule meetups with each other."""
        date = arrow.get(f'{date} {time}', 'M-DD-YYYY h:mmA', tzinfo='US/Eastern')
        reason = reason if reason else 'no reason'
        if date < arrow.now('US/Eastern'):
            await ctx.send("You're stuck in the past, Marty!")
        else:
            if ctx.message.mention_everyone:
                await add_meetup(organizer=ctx.author, name=name, date=date, invitations=list(ctx.guild.members), reason=reason)
            else:
                await add_meetup(organizer=ctx.author, name=name, date=date, invitations=list(invitations), reason=reason)
            await ctx.send(f'Meet up scheduled to occur {date.humanize()}.')

    @commands.command(usage='`!attending something`')
    async def attending(self, ctx, name):
        """Adds you to the attending list for the specified meetup."""
        msg = await add_attendee(name=name, attendee=ctx.author)
        await ctx.send(msg)

    @commands.command(usage='`!contribute something i have nothing`')
    async def contribute(self, ctx, name, *, stuff):
        """Contributes to the specified meetup."""
        if Contribution.exists(contributor=str(ctx.author.id)):
            msg = await update_contribution(contributor=ctx.author, contribution=stuff)
        else:
            msg = await add_contributor(name=name, contributor=ctx.author, contribution=stuff)
        await ctx.send(msg)

    @tasks.loop(minutes=1)
    async def schedule(self):
        with db_session:
            for meetup in select(meetup for meetup in Meetup):
                date = arrow.get(meetup.date, tzinfo='US/Eastern')
                now = arrow.now('US/Eastern')
                if date.shift(minutes=-31) <= now:
                    organizer = discord.utils.get(self.client.users, id=int(meetup.organizer))
                    attendees = [discord.utils.get(self.client.users, id=m) for m in meetup.attendees]
                    if attendees:
                        await organizer.send(f'Your meetup with {", ".join([m.name for m in attendees[:-1]])} and {attendees[-1].name} is {date.humanize()}!\nMeeting reminder: {meetup.reason}')
                    else:
                        await organizer.send(f'Your meetup is {date.humanize()}! Nobody said they were attending yet sadly.\nMeeting reminder: {meetup.reason}')
                    for member in attendees:
                        if Contribution.exists(contributor=str(member.id)):
                            contr = Contribution.get(contributor=str(member.id))
                            await member.send(f'Your meetup with {organizer.name} is {date.humanize()}!\nMeeting reminder: {meetup.reason}\nYour contribution: {", ".join(contr.contributing)}')
                            contr.delete()
                        else:
                            await member.send(f'Your meetup with {organizer.name} is {date.humanize()}!\nMeeting reminder: {meetup.reason}')
                    meetup.delete()

def setup(client):
    client.add_cog(Meeting(client))
