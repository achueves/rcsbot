import discord
import requests
from discord.ext import commands
from config import settings
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

# Connect to Google Sheets
scope = "https://www.googleapis.com/auth/spreadsheets.readonly"
spreadsheet_id = settings['google']['commLogId']
store = file.Storage("token.json")
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets("credentials.json", scope)
    creds = tools.run_flow(flow, store)
service = build("sheets", "v4", http=creds.authorize(Http()), cache_discovery=False)
sheet = service.spreadsheets()


class Contact(commands.Cog):
    """Cog for handling Council Tasks"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="tasks", aliases=["task", "tasklist", "list"], hidden=True)
    async def task_list(self, ctx, cmd: str = ""):
        if ctx.guild is None or ctx.channel.id == settings['rcsChannels']['council']:
            if cmd.lower() == "all":
                if ctx.channel.id == settings['rcsChannels']['council']:
                    await ctx.send("This is a long list. I'm going to send it to your DM. To view items "
                                   "in the Council Chat, please request them individually (`++tasks suggestions`).")
                # Suggestions
                result = sheet.values().get(spreadsheetId=spreadsheet_id, range="Suggestions!A2:I").execute()
                values = result.get("values", [])
                embed = discord.Embed(title="RCS Council Suggestions", color=discord.Color.blurple())
                flag = 0
                for row in values:
                    if len(row) < 9:
                        embed.add_field(name=f"Suggestion from {row[1]}\n{row[7]}",
                                        value=f"{row[3][:500]}\nDated {row[0]}",
                                        inline=False)
                if len(embed.fields) > 0:
                    flag = 1
                    await ctx.author.send(embed=embed)
                # Council Nominations
                result = sheet.values().get(spreadsheetId=spreadsheet_id, range="Council!A2:J").execute()
                values = result.get("values", [])
                embed = discord.Embed(title="RCS Council Nominations", color=discord.Color.dark_gold())
                for row in values:
                    if row[8] == "":
                        embed.add_field(name=f"Council Nomination for {row[3]}\n{row[9]}",
                                        value=f"Submitted by {row[1]}\nDated {row[0]}",
                                        inline=False)
                if len(embed.fields) > 0:
                    flag = 1
                    await ctx.author.send(embed=embed)
                # Verification Requests
                result = sheet.values().get(spreadsheetId=spreadsheet_id, range="Verification!A2:I").execute()
                values = result.get("values", [])
                embed = discord.Embed(title="RCS Council Verification Requests", color=discord.Color.dark_blue())
                for row in values:
                    if len(row) < 9 or row[8] in ("1", "2", "3", "4"):
                        status = "has not been addressed"
                        try:
                            if row[8] == "1": status = " is awaiting a scout"
                            if row[8] == "2": status = " is currently being scouted"
                            if row[8] == "3": status = " is awaiting the post-scout survey"
                            if row[8] == "4": status = " is awaiting a decision by Council"
                        except:
                            self.bot.logger.debug("row is shorter than 9")
                        embed.add_field(name=f"Verification for {row[1]} {status}.\n{row[7]}",
                                        value=f"Leader: {row[3]}\nDated {row[0]}",
                                        inline=False)
                if len(embed.fields) > 0:
                    flag = 1
                    await ctx.author.send(embed=embed)
                # Other Submissions
                result = sheet.values().get(spreadsheetId=spreadsheet_id, range="Other!A2:I").execute()
                values = result.get("values", [])
                embed = discord.Embed(title="RCS Council Other Items", color=discord.Color.gold())
                for row in values:
                    if len(row) < 9:
                        embed.add_field(name=f"Other Comment from {row[1]}\n{row[7]}",
                                        value=f"{row[3][:500]}\nDated {row[0]}",
                                        inline=False)
                if len(embed.fields) > 0:
                    flag = 1
                    await ctx.author.send(embed=embed)
                # Tasks (Individual Action Items)
                result = sheet.values().get(spreadsheetId=spreadsheet_id, range="Tasks!A2:I").execute()
                values = result.get("values", [])
                embed = discord.Embed(title="RCS Council Action Items", color=discord.Color.dark_magenta())
                for row in values:
                    if len(row) < 9:
                        embed.add_field(name=f"Task {row[7]} - {row[0]}",
                                        value=f"<@{row[2]}>\n{row[1]}",
                                        inline=False)
                embed.set_footer(text="Use ++done <Task ID> to complete a task")
                if len(embed.fields) > 0:
                    flag = 1
                    await ctx.author.send(embed=embed)
                if flag == 0:
                    await ctx.send("No incomplete tasks at this time! Well done!")
            if cmd.lower() in ("suggestions", "suggest", "suggestion", "sugg", "sug"):
                result = sheet.values().get(spreadsheetId=spreadsheet_id, range="Suggestions!A2:I").execute()
                values = result.get("values", [])
                embed = discord.Embed(title="RCS Council Suggestions", color=discord.Color.blurple())
                for row in values:
                    if len(row) < 9:
                        embed.add_field(name=f"Suggestion from {row[1]}\n{row[7]}\nDated {row[0]}",
                                        value=row[3][:1023],
                                        inline=True)
                embed.set_footer(text="Please review the Communication Log if the suggestions is cut off.")
                if len(embed.fields) > 0:
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("No incomplete suggestions at this time.")
            if cmd.lower() in ("council", "nomination", "nominations", "nomi", "coun"):
                result = sheet.values().get(spreadsheetId=spreadsheet_id, range="Council!A2:J").execute()
                values = result.get("values", [])
                embed = discord.Embed(title="RCS Council Nominations", color=discord.Color.dark_gold())
                for row in values:
                    if row[8] == "":
                        embed.add_field(name=f"Council Nomination for {row[3]}\n{row[9]}\nDated {row[0]}",
                                        value=f"Submitted by {row[1]}",
                                        inline=True)
                if len(embed.fields) > 0:
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("No incomplete Council nominations at this time.")
            if cmd.lower() in ("verification", "verifications", "veri"):
                result = sheet.values().get(spreadsheetId=spreadsheet_id, range="Verification!A2:I").execute()
                values = result.get("values", [])
                embed = discord.Embed(title="RCS Council Verification Requests", color=discord.Color.dark_blue())
                for row in values:
                    if len(row) < 9:
                        embed.add_field(name=f"Verification for {row[1]}\n{row[7]}\nDated {row[0]}",
                                        value=f"Leader: {row[3]}",
                                        inline=True)
                await ctx.send(embed=embed)
            if cmd.lower() in ("other", "oth", "othe"):
                result = sheet.values().get(spreadsheetId=spreadsheet_id, range="Other!A2:I").execute()
                values = result.get("values", [])
                embed = discord.Embed(title="RCS Council Other Items", color=discord.Color.gold())
                for row in values:
                    if len(row) < 9:
                        embed.add_field(name=f"Other Comment from {row[1]}\n{row[7]}\nDated {row[0]}",
                                        value=row[3][:1023],
                                        inline=True)
                if len(embed.fields) > 0:
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("No tasks in the Other category at this time.")
            if cmd.lower() in ("tasks", "task", "action", "agenda", "act"):
                result = sheet.values().get(spreadsheetId=spreadsheet_id, range="Tasks!A2:I").execute()
                values = result.get("values", [])
                embed = discord.Embed(title="RCS Council Action Items", color=discord.Color.gold())
                for row in values:
                    if len(row) < 9:
                        embed.add_field(name=f"Task {row[7]} - {row[0]}",
                                        value=f"<@{row[2]}>\n{row[1]}",
                                        inline=False)
                if len(embed.fields):
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("No incomplete action items at this time.")
            if cmd.lower() == "":
                await ctx.author.send(ctx.author, "Here's your personalized list")
        else:
            await ctx.send("This very special and important command is reserved for #council-chat only!")

    @commands.command(name="add", aliases=["new", "newtask", "addtask"], hidden=True)
    async def add_task(self, ctx, user: discord.Member, *task):
        if is_council(ctx.author.roles) and ctx.channel.id == settings['rcsChannels']['council']:
            url = (f"{settings['google']['commLog']}?call=addtask&task={' '.join(task)}&"
                   f"discord={user.id}")
            r = requests.get(url)
            if r.status_code == requests.codes.ok:
                await ctx.send(f"Task {r.text} - {' '.join(task)} added for <@{user.id}>")
                await user.send(f"Task {r.text} - {' '.join(task)} was assigned to you by {ctx.author.display_name}.")
            else:
                await ctx.send(f"Something went wrong. Here's an error code for you to play with.\n{r.text}")
        else:
            await ctx.send("This very special and important command is reserved for council members only!")

    @commands.command(name="assign", hidden=True)
    async def assign_task(self, ctx, user: discord.Member):
        if is_council(ctx.author.roles):
            await ctx.send("Task assigned")
            await user.send("A new task was assigned to you by ...")
        else:
            await ctx.send("This very special and important command is reserved for council members only!")

    @commands.command(name="change", aliases=["modify", "alter"], hidden=True)
    async def change_task(self, ctx, task_id, new_task):
        if is_council(ctx.author.roles):
            await ctx.send("Task changed")
        else:
            await ctx.send("This very special and important command is reserved for council members only!")

    @commands.command(name="complete", aliases=["done", "finished", "x"], hidden=True)
    async def complete_task(self, ctx, task_id):
        if is_council(ctx.author.roles):
            await ctx.send("Task marked complete")
        else:
            await ctx.send("This very special and important command is reserved for council members only!")

    async def send_text(self, channel, text, block=None):
        """ Sends text to channel, splitting if necessary
        Discord has a 2000 character limit
        """
        if len(text) < 2000:
            if block:
                await channel.send(f"```{text}```")
            else:
                await channel.send(text)
        else:
            coll = ""
            for line in text.splitlines(keepends=True):
                if len(coll) + len(line) > 1994:
                    # if collection is going to be too long, send  what you have so far
                    if block:
                        await channel.send(f"```{coll}```")
                    else:
                        await channel.send(coll)
                    coll = ""
                coll += line
            await channel.send(coll)


def is_council(user_roles):
    for role in user_roles:
        if role.id == settings['rcsRoles']['council']:
            return True
    return False


def setup(bot):
    bot.add_cog(Contact(bot))
