import discord
from discord.ext import commands as discordcommands
import Common

# list of all cogs to add
initial_extensions = ['commands.test', 'commands.information', 'commands.support', 'commands.leaderboards']

bot = discordcommands.Bot(command_prefix="?")
for extension in initial_extensions:
    bot.load_extension(extension)

# global check that applies to all commands
# checks if commands was sent from an expected channel
@bot.check
async def global_channel_check(ctx):  # TODO: Can this be one-lined without losing readability?
    # reads as, message was sent in a command channel and a command, other than claim, was not sent in support channel
    if str(ctx.message.channel) not in Common.command_channel_list:
        return False
    elif (str(ctx.invoked_with) != "claim"):
        if (str(ctx.message.channel) == Common.command_channel_list[2]):
            return False
        return True
    else:
        return True


@bot.event
async def on_command_error(ctx, error):
    for dev in Common.developers:
        user = ctx.bot.get_user(dev)
        await user.send(f"""GENERIC error in command: {error}""")


def startup():
    print("Starting..")
    # Printing client info
    @bot.event
    async def on_ready():
        print('Logged in as: ' + bot.user.display_name)
        print("Ready for action")
        print('------')
        await bot.change_presence(activity=discord.Game(name='Pokémon GO'))
