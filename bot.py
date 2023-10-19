# FILE: Discord bot


# DEPENDENCIES
import discord
import io_2
import asyncio
import common


# CONFIGURATION
common.BOT_TOKEN = io_2.read_json(file_path="secret/api_key.json")["bot_token"]
try:
    common.config = io_2.read_json(file_path="config/config.json")
    if common.config["configured"] != "True":
        # Log
        io_2.log(ticker="bot",
                 message="Config file is corrupted. Using defaults...")
        common.config = io_2.read_json(file_path="defaults/config_defaults.json")
except:
    # Log
    io_2.log(ticker="bot",
             message="Config file could not be read. Using defaults...")
    common.config = io_2.read_json(file_path="defaults/config_defaults.json")

try:
    common.data = io_2.read_json(file_path="data/data.json")
    if common.data["configured"] != "True":
        # Log
        io_2.log(ticker="bot",
                 message="Data file is corrupted. Using defaults...")
        common.data = io_2.read_json(file_path="defaults/data_defaults.json")
except:
    # Log
    io_2.log(ticker="bot",
             message="Data file could not be read. Using defaults...")
    common.data = io_2.read_json(file_path="defaults/data_defaults.json")


# FUNCTIONS
def check_ids(snowflakes: list[str],
              whitelist: list = common.data["whitelist"],
              blacklist: list = common.data["blacklist"]) -> bool:

    # FUNCTION: Check if id is blacklisted or whitelisted. Blacklist overrides whitelist.

    # PARAMS:
    #   * snowflakes: list[str]: List of snowflake ids
    #   * whitelist: list: List of allowed ids
    #   * blacklist: list: List of disallowed ids

    # Check if id is blacklisted
    for snowflake in snowflakes:
        if snowflake in blacklist:
            return False

    # Check if id is allowed
    for snowflake in snowflakes:
        if snowflake in whitelist:
            return True

    # Not allowed
    return False


async def check_allowed(ctx: discord.ApplicationContext,
                        whitelist: list[str] = common.data["whitelist"],
                        blacklist: list[str] = common.data["blacklist"],
                        admin_only: bool = False,
                        admins: list[str] = common.data["admins"],
                        disallowed_response: bool = True) -> bool:

    # FUNCTION: Check if command is allowed to be run in current context.

    # PARAMS:
    #   * ctx: discord.ApplicationContext: Command context
    #   * whitelist: list[str]: Whitelisted roles
    #   * blacklist: list[str]: Blacklisted roles
    #   * admin_only: bool: whether this command is admin only
    #   * disallowed_response: bool: Whether to respond with an error message if not allowed

    # RETURNS:
    #   * allowed: bool: Whether command is allowed or not

    # Get info
    user_id, channel_id, role_ids, server_id = get_info(ctx=ctx)

    # Log
    io_2.log(ticker="bot",
             message=f"Checking if command is allowed for '{user_id}'"
                     f" in channel '{channel_id}'"
                     f" in server '{server_id}'"
                     f" with roles '{role_ids}'")

    # Check if admin
    admin = check_admin(user_id=user_id,
                        admins=admins)
    if admin:

        # Alert for admin override
        embed = discord.Embed(
            title="Admin override",
            description="Permissions overridden with admin access.",
            color=common.config["colors"]["success"]
        )
        await ctx.respond(embed=embed)

        # Log
        io_2.log(ticker="bot",
                 message=f"Command allowed via admin override for {user_id}")

        # Return as allowed
        return True

    # Reject if command is for admins only
    if admin_only:
        embed = discord.Embed(
            title="Admin only command",
            description="Sorry, you must be a bot admin to use this command.",
            color=common.config["colors"]["error"]
        )
        await ctx.respond(embed=embed)
        return False

    # Check if allowed
    snowflakes = role_ids
    snowflakes.extend([user_id, channel_id, server_id])
    allowed = check_ids(snowflakes=snowflakes,
                        whitelist=whitelist,
                        blacklist=blacklist)

    # Respond if not allowed & response setting is on
    if (not allowed) and disallowed_response:
        embed = discord.Embed(
            title="Not allowed",
            description="Sorry, you are not allowed to take this action.",
            color=common.config["colors"]["error"]
        )
        embed.add_field(name="This could be due to:",
                        value="* You have insufficient permissions in this server \n"
                              "* You are restricted from using the bot \n"
                              "* The bot is undergoing maintenance \n")
        await ctx.respond(embed=embed)

    # Log
    io_2.log(ticker="bot",
             message=f"Command {'allowed' if allowed else 'disallowed'} for {user_id}")

    # Return result
    return allowed


def check_admin(user_id: str,
                admins: list[str] = common.data["admins"]):

    # FUNCTION: Check if user is an admin

    # PARAMS:
    #   * user_id: str: Given ID
    #   * admins: list[str]: List of admin IDs

    # Check if admin
    admin = check_ids(snowflakes=[user_id],
                      whitelist=admins,
                      blacklist=[])

    # Return result
    return admin


def get_info(ctx: discord.ApplicationContext) -> (str, str, list[str], str):

    # FUNCTION: Get various ids

    # PARAMS:
    #   * ctx: discord.ApplicationContext: Command context

    # RETURNS:
    #   * user_id: str: ID of user
    #   * channel_id: ID of channel
    #   * role_ids: list[str]: list of role IDs for that user
    #   * server_id: str: ID of server

    # Get info
    user_id = str(ctx.user.id)
    channel_id = str(ctx.channel_id)
    role_ids = []
    for role in ctx.user.roles:
        role_ids.append(str(role.id))
    server_id = str(ctx.guild_id)

    # Return results
    return user_id, channel_id, role_ids, server_id


# MAIN
# Log
io_2.log(ticker="bot",
         message=f"Starting bot...")


# Set bot intents
intents = discord.Intents.default()


# Create various object handles
client = discord.Bot(intents=intents)


# EVENTS
# On ready
@client.event
async def on_ready():
    io_2.log(ticker="bot",
             message=f"Successfully logged in as {client.user}")


# COMMANDS
@client.command(description="Displays information about the bot and its configuration in this server.")
async def about(ctx: discord.ApplicationContext):

    # Create embed
    embed = discord.Embed(
        title="About Raindrop",
        description="Raindrop is a discord bot created by *Osteofelidae*, to perform various tasks for RainCo servers.",
        color=common.config["colors"]["generic"]
    )
    embed.add_field(name="Subscriptions",
                    value="")  # TODO
    embed.add_field(name="Roles",
                    value="")  # TODO
    embed.set_footer(text="version 0.0.1")  # TODO change as necessary
    embed.set_author(name="osteofelidae",
                     icon_url="https://avatars.githubusercontent.com/u/115187283")
    embed.set_thumbnail(url="")  # TODO
    embed.set_image(url="")  # TODO

    # Respond to context
    await ctx.respond(embed=embed)


# STREAM COMMANDS
stream_command_group = client.create_group(name="stream",
                                           description="Commands to interface with subscribeable streams.")


# Create stream command
@stream_command_group.command(description="Create a notification stream anyone can subscribe to.")
async def create(ctx: discord.ApplicationContext,
                 name: str):

    # Check if allowed
    allowed = await check_allowed(ctx=ctx,
                                  whitelist=common.data["whitelist"],
                                  blacklist=common.data["blacklist"])
    if not allowed:
        return

    # Get info
    user_id, channel_id, role_ids, server_id = get_info(ctx=ctx)

    # Check if exists
    if name in common.data["streams"]:

        # Send error embed
        embed = discord.Embed(
            title="Already exists",
            description=f"'{name}' already exists. Streams must have a unique name.",
            color=common.config["colors"]["error"]
        )
        await ctx.respond(embed=embed)
        return

    # Create stream
    common.data["streams"][name] = {
        "locked": "False",
        "origin_server": server_id,
        "channels": [],
        "whitelist": [
            server_id
        ],
        "blacklist": []
    }

    # Send success embed
    embed = discord.Embed(
        title="Stream created",
        description=f"'{name}' has been created.",
        color=common.config["colors"]["success"]
    )
    await ctx.respond(embed=embed)


# Delete stream command
@stream_command_group.command(description="Delete a stream.")
async def delete(ctx: discord.ApplicationContext,
                 name: str):

    # Check if allowed
    allowed = await check_allowed(ctx=ctx,
                                  whitelist=common.data["whitelist"],
                                  blacklist=common.data["blacklist"])
    if not allowed:
        return

    # Check if exists
    if name not in common.data["streams"].keys():

        # Send error embed
        embed = discord.Embed(
            title="Not found",
            description=f"'{name}' does not exist.",
            color=common.config["colors"]["error"]
        )
        await ctx.respond(embed=embed)
        return

    # Check if stream allows it
    stream_allowed = await check_allowed(ctx=ctx,
                                         whitelist=common.data["streams"][name]["whitelist"],
                                         blacklist=common.data["streams"][name]["blacklist"],
                                         disallowed_response=False)
    if not stream_allowed:

        # Send error embed
        embed = discord.Embed(
            title="Not allowed",
            description=f"'{name}' cannot be modified here. A stream can only be modified in the server"
                        f" it was created in, or by authorized users or in authorized servers.",
            color=common.config["colors"]["error"]
        )
        await ctx.respond(embed=embed)
        return

    # Delete stream
    del common.data["streams"][name]

    # Send success embed
    embed = discord.Embed(
        title="Stream deleted",
        description=f"'{name}' has been deleted.",
        color=common.config["colors"]["success"]
    )
    await ctx.respond(embed=embed)


# Subscribe to stream command
@stream_command_group.command(description="Subscribe to a stream.")
async def subscribe(ctx: discord.ApplicationContext,
                    name: str,
                    channel: discord.TextChannel):

    # Check if allowed
    allowed = await check_allowed(ctx=ctx,
                                  whitelist=common.data["whitelist"],
                                  blacklist=common.data["blacklist"])
    if not allowed:
        return

    # Get info
    subscribe_channel_id = str(channel.id)

    # Check if stream exists
    if name not in common.data["streams"]:

        # Send error embed
        embed = discord.Embed(
            title="Not found",
            description=f"'{name}' does not exist.",
            color=common.config["colors"]["error"]
        )
        await ctx.respond(embed=embed)
        return

    # Check if already subscribed
    if subscribe_channel_id in common.data["streams"][name]["channels"]:
        # Send error embed
        embed = discord.Embed(
            title="Already subscribed",
            description=f"'{channel}' is already subscribed to '{name}'.",
            color=common.config["colors"]["error"]
        )
        await ctx.respond(embed=embed)
        return

    # Subscribe to stream
    common.data["streams"][name]["channels"].append(subscribe_channel_id)

    # Send success embed
    embed = discord.Embed(
        title="Subscribed to stream",
        description=f"'{channel}' has been subscribed to '{name}'.",
        color=common.config["colors"]["success"]
    )
    await ctx.respond(embed=embed)


# Unsubscribe from stream command
@stream_command_group.command(description="Unsubscribe from a stream.")
async def unsubscribe(ctx: discord.ApplicationContext,
                      name: str,
                      channel: discord.TextChannel):

    # Check if allowed
    allowed = await check_allowed(ctx=ctx,
                                  whitelist=common.data["whitelist"],
                                  blacklist=common.data["blacklist"])
    if not allowed:
        return

    # Get info
    subscribe_channel_id = str(channel.id)

    # Check if stream exists
    if name not in common.data["streams"]:

        # Send error embed
        embed = discord.Embed(
            title="Not found",
            description=f"'{name}' does not exist.",
            color=common.config["colors"]["error"]
        )
        await ctx.respond(embed=embed)
        return

    # Check if not subscribed
    if subscribe_channel_id not in common.data["streams"][name]["channels"]:
        # Send error embed
        embed = discord.Embed(
            title="Not found",
            description=f"'{channel}' is not subscribed to '{name}'.",
            color=common.config["colors"]["error"]
        )
        await ctx.respond(embed=embed)
        return

    # Subscribe to stream
    common.data["streams"][name]["channels"].remove(subscribe_channel_id)

    # Send success embed
    embed = discord.Embed(
        title="Unsubscribed from stream",
        description=f"'{channel}' has been unsubscribed from '{name}'.",
        color=common.config["colors"]["success"]
    )
    await ctx.respond(embed=embed)


# Whitelist object to stream command
@stream_command_group.command(description="Whitelist an object to a stream.")
async def authorize(ctx: discord.ApplicationContext,
                    name: str,
                    snowflake: str):

    # Check if allowed
    allowed = await check_allowed(ctx=ctx,
                                  whitelist=common.data["whitelist"],
                                  blacklist=common.data["blacklist"])
    if not allowed:
        return

    # Check if stream exists
    if name not in common.data["streams"].keys():

        # Send error embed
        embed = discord.Embed(
            title="Not found",
            description=f"'{name}' does not exist.",
            color=common.config["colors"]["error"]
        )
        await ctx.respond(embed=embed)
        return

    # Check if stream allows it
    stream_allowed = await check_allowed(ctx=ctx,
                                         whitelist=common.data["streams"][name]["whitelist"],
                                         blacklist=common.data["streams"][name]["blacklist"],
                                         disallowed_response=False)
    if not stream_allowed:

        # Send error embed
        embed = discord.Embed(
            title="Not allowed",
            description=f"'{name}' cannot be modified here. A stream can only be modified in the server"
                        f" it was created in, or by authorized users or in authorized servers.",
            color=common.config["colors"]["error"]
        )
        await ctx.respond(embed=embed)
        return

    # Check if object exists
    if snowflake in common.data["streams"][name]["whitelist"]:
        # Send error embed
        embed = discord.Embed(
            title="Already authorized",
            description=f"'{snowflake}' is already authorized to modify '{name}'.",
            color=common.config["colors"]["error"]
        )
        await ctx.respond(embed=embed)
        return

    # Whitelist
    common.data["streams"][name]["whitelist"].append(snowflake)

    # Send success embed
    embed = discord.Embed(
        title="Authorized",
        description=f"'{snowflake}' is now authorized to modify '{name}'.",
        color=common.config["colors"]["success"]
    )
    await ctx.respond(embed=embed)


# De-whitelist object to stream command
@stream_command_group.command(description="De-whitelist an object to a stream.")
async def unauthorize(ctx: discord.ApplicationContext,
                      name: str,
                      snowflake: str):

    # Check if allowed
    allowed = await check_allowed(ctx=ctx,
                                  whitelist=common.data["whitelist"],
                                  blacklist=common.data["blacklist"])
    if not allowed:
        return

    # Check if stream exists
    if name not in common.data["streams"].keys():

        # Send error embed
        embed = discord.Embed(
            title="Not found",
            description=f"'{name}' does not exist.",
            color=common.config["colors"]["error"]
        )
        await ctx.respond(embed=embed)
        return

    # Check if stream allows it
    stream_allowed = await check_allowed(ctx=ctx,
                                         whitelist=common.data["streams"][name]["whitelist"],
                                         blacklist=common.data["streams"][name]["blacklist"],
                                         disallowed_response=False)
    if not stream_allowed:

        # Send error embed
        embed = discord.Embed(
            title="Not allowed",
            description=f"'{name}' cannot be modified here. A stream can only be modified in the server"
                        f" it was created in, or by authorized users or in authorized servers.",
            color=common.config["colors"]["error"]
        )
        await ctx.respond(embed=embed)
        return

    # Check if object exists
    if snowflake not in common.data["streams"][name]["whitelist"]:
        # Send error embed
        embed = discord.Embed(
            title="Already authorized",
            description=f"'{snowflake}' is already not authorized to modify '{name}'.",
            color=common.config["colors"]["error"]
        )
        await ctx.respond(embed=embed)
        return

    # Whitelist
    common.data["streams"][name]["whitelist"].remove(snowflake)

    # Send success embed
    embed = discord.Embed(
        title="Unauthorized",
        description=f"'{snowflake}' is now not authorized to modify '{name}'.",
        color=common.config["colors"]["success"]
    )
    await ctx.respond(embed=embed)


# ANNOUNCEMENT COMMANDS
announcement_command_group = client.create_group(name="announcement",
                                                 description="Commands to interface with announcements.")

# TODO announce send command w/ auto-propagate

# TODO announce new command

# TODO announce send command

# TODO announcement scheduling?


# WHITELIST COMMANDS
whitelist_command_group = client.create_group(name="whitelist",
                                              description="Commands to interface with the whitelist.")


# Add to whitelist command
@whitelist_command_group.command(description="Add to the whitelist.")
async def add(ctx: discord.ApplicationContext,
              snowflake: str):

    # Check if admin
    allowed = await check_allowed(ctx=ctx,
                                  admin_only=True)
    if not allowed:
        return

    # Reinforce type
    snowflake = str(snowflake)

    # Check if already in it
    if snowflake in common.data["whitelist"]:

        # Send error embed
        embed = discord.Embed(
            title="Already whitelisted",
            description=f"'{snowflake}' is already whitelisted.",
            color=common.config["colors"]["error"]
        )
        await ctx.respond(embed=embed)
        return

    # Add to whitelist
    common.data["whitelist"].append(snowflake)

    # Send success embed
    embed = discord.Embed(
        title="Successfully whitelisted",
        description=f"'{snowflake}' has been whitelisted successfully.",
        color=common.config["colors"]["success"]
    )
    await ctx.respond(embed=embed)


# Remove from whitelist command
@whitelist_command_group.command(description="Remove from the whitelist.")
async def remove(ctx: discord.ApplicationContext,
                 snowflake: str):

    # Check if admin
    allowed = await check_allowed(ctx=ctx,
                                  admin_only=True)
    if not allowed:
        return

    # Reinforce type
    snowflake = str(snowflake)

    # Check if not in it
    if snowflake not in common.data["whitelist"]:

        # Send error embed
        embed = discord.Embed(
            title="Not found",
            description=f"'{snowflake}' is not in the whitelist.",
            color=common.config["colors"]["error"]
        )
        await ctx.respond(embed=embed)
        return

    # Remove from whitelist
    common.data["whitelist"].remove(snowflake)

    # Send success embed
    embed = discord.Embed(
        title="Successfully removed",
        description=f"'{snowflake}' has been removed from the whitelist.",
        color=common.config["colors"]["success"]
    )
    await ctx.respond(embed=embed)


# View whitelist command
@whitelist_command_group.command(description="View the whitelist.")
async def view(ctx: discord.ApplicationContext):

    # Check if admin
    allowed = await check_allowed(ctx=ctx,
                                  admin_only=True)
    if not allowed:
        return

    # Write whitelist to file
    with open("temp/whitelist.txt", "w") as file:
        file.writelines(f"{line}\n" for line in common.data["whitelist"])

    # Send file
    with open("temp/whitelist.txt", "r") as file:
        discord_file = discord.File(file, "whitelist.txt")
        await ctx.respond(file=discord_file)


# BLACKLIST COMMANDS
blacklist_command_group = client.create_group(name="blacklist",
                                              description="Commands to interface with the blacklist.")


# Add to blacklist command
@blacklist_command_group.command(description="Add to the blacklist.")
async def add(ctx: discord.ApplicationContext,
              snowflake: str):

    # Check if admin
    allowed = await check_allowed(ctx=ctx,
                                  admin_only=True)
    if not allowed:
        return

    # Reinforce type
    snowflake = str(snowflake)

    # Check if already in it
    if snowflake in common.data["blacklist"]:

        # Send error embed
        embed = discord.Embed(
            title="Already whitelisted",
            description=f"'{snowflake}' is already blacklisted.",
            color=common.config["colors"]["error"]
        )
        await ctx.respond(embed=embed)
        return

    # Add to whitelist
    common.data["blacklist"].append(snowflake)

    # Send success embed
    embed = discord.Embed(
        title="Successfully blacklisted",
        description=f"'{snowflake}' has been blacklisted successfully.",
        color=common.config["colors"]["success"]
    )
    await ctx.respond(embed=embed)


# Remove from blacklist command
@blacklist_command_group.command(description="Remove from the blacklist.")
async def remove(ctx: discord.ApplicationContext,
                 snowflake: str):

    # Check if admin
    allowed = await check_allowed(ctx=ctx,
                                  admin_only=True)
    if not allowed:
        return

    # Reinforce type
    snowflake = str(snowflake)

    # Check if not in it
    if snowflake not in common.data["blacklist"]:

        # Send error embed
        embed = discord.Embed(
            title="Not found",
            description=f"'{snowflake}' is not in the blacklist.",
            color=common.config["colors"]["error"]
        )
        await ctx.respond(embed=embed)
        return

    # Remove from whitelist
    common.data["blacklist"].remove(snowflake)

    # Send success embed
    embed = discord.Embed(
        title="Successfully removed",
        description=f"'{snowflake}' has been removed from the blacklist.",
        color=common.config["colors"]["success"]
    )
    await ctx.respond(embed=embed)


# View blacklist command
@blacklist_command_group.command(description="View the blacklist.")
async def view(ctx: discord.ApplicationContext):

    # Check if admin
    allowed = await check_allowed(ctx=ctx,
                                  admin_only=True)
    if not allowed:
        return

    # Write blacklist to file
    with open("temp/blacklist.txt", "w") as file:
        file.writelines(f"{line}\n" for line in common.data["blacklist"])

    # Send file
    with open("temp/blacklist.txt", "r") as file:
        discord_file = discord.File(file, "blacklist.txt")
        await ctx.respond(file=discord_file)


# Run bot loop
client.run(common.BOT_TOKEN)
