from datetime import datetime, timedelta

import discord
import requests
from discord.ext import commands

import common
import common_instances
from sneaselcommands.raids.utils.raid_scheduler import schedule_edit_embed, schedule_reminding_task, \
    schedule_delete_channel_at, update_raids_channel
from utils.database_connector import execute_statement, create_insert_query, create_select_query
from utils.exception_wrapper import pm_dev_error
from utils.global_error_manager import in_channel_list
from utils.time_wrapper import valid_time_hhmm, valid_time_mm, format_as_hhmm


def _validate_report(*args) -> str:
    """Validates the format of the report."""
    if len(args) < 2:
        return f"Missing information, please provide name and gym. Type *?help raid* for help"

    hatch_time = valid_time_hhmm(args[-1])
    earliest_possible_hatch_time = (datetime.now() - timedelta(minutes=45))
    if hatch_time is not None and hatch_time.time() < earliest_possible_hatch_time.time():
        return f"A raid that hatched at **{args[-1]}** should have already despawned by now"

    latest_possible_hatch_time = (datetime.now() + timedelta(hours=1))
    if hatch_time is not None and hatch_time.time() >  latest_possible_hatch_time.time():
        return f"A raid that hatches at **{args[-1]}** can not have spawned yet"

    despawn_time = valid_time_mm(args[-1])
    if despawn_time is not None and (despawn_time.minute <= 0 or despawn_time.minute > 45):
        return f"Incorrect despawn time of **{despawn_time.minute}** minutes, should be between 1 and 45 minutes"
    return ""


async def _send_embed(bot, ctx, channel, pokemon_name: str, gym: str, hatch_time: str):
    """Creates the embed to be posted in the new raid channel"""
    embed = create_raid_embed(ctx, pokemon_name, gym, hatch_time)
    await channel.send(embed=embed)

    maybe_valid_time = valid_time_hhmm(hatch_time)
    if maybe_valid_time is not None:
        if maybe_valid_time.time() > datetime.now().time():
            schedule_edit_embed(bot, ctx=ctx, channel=channel, at_time=format_as_hhmm(maybe_valid_time))
    return embed


def create_raid_embed(ctx, pokemon_name: str, gym_name: str, hatch_time: str) -> discord.Embed:
    maybe_valid_time = valid_time_hhmm(hatch_time)
    if maybe_valid_time is None:
        description = f"Gym: {gym_name.capitalize()}\nHatch time: {hatch_time}"
    elif maybe_valid_time.time() > datetime.now().time():
        description = f"Gym: {gym_name.capitalize()}\nHatch time: {hatch_time}"
    else:
        description = f"Gym: {gym_name.capitalize()}\nDespawn time: {format_as_hhmm((maybe_valid_time + timedelta(minutes=45)))}"

    pokemon = common_instances.POKEDEX.lookup(pokemon_name)
    pokemon_icon = "https://www.pokencyclopedia.info/sprites/misc/spr_substitute/art__substitute.png"
    fast_moves = "N/A"
    charge_moves = "N/A"
    max_cp_20 = "N/A"
    max_cp_25 = "N/A"
    max_cp_40 = "N/A"
    types = "N/A"

    if pokemon_name.upper() in common.RAID_EGG_TYPES:
        pokemon_name = pokemon_name.upper()
        pokemon_icon = common.RAID_EGG_ICON_URLS[pokemon_name]
    elif pokemon is not None:
        pokemon_name = pokemon_name.title()
        if requests.get(pokemon.sprite_url).status_code == 200:
            pokemon_icon = pokemon.sprite_url
        fast_moves = " ".join(pokemon.movepool.fast_moves)
        charge_moves = " ".join(pokemon.movepool.charge_moves)
        max_cp_20 = pokemon.stats.calculate_cp_at_level(20)
        max_cp_25 = pokemon.stats.calculate_cp_at_level(25)
        max_cp_40 = pokemon.stats.calculate_cp_at_level(40)

        types = discord.utils.get(ctx.message.guild.emojis, name=f"{pokemon.type1.lower()}_type")
        if pokemon.type2 is not None:
            types = f"{types} {discord.utils.get(ctx.message.guild.emojis, name=f'{pokemon.type2.lower()}_type')}"

    embed = discord.Embed(title=f"Raid - {pokemon_name}",
                          color=0xff9900,
                          description=description,
                          timestamp=datetime.utcnow())
    embed.set_thumbnail(url=pokemon_icon)
    embed.set_footer(text="Sprite: https://pokemondb.net/sprites • Data: https://www.pokebattler.com")
    embed.add_field(name="Type: ", value=types, inline=True)
    embed.add_field(name="\u200b", value="\u200b", inline=True)
    embed.add_field(name="Max CP:",
                    value=f"Raid: **{max_cp_20}**, Raid (weather boost): **{max_cp_25}**, Max: **{max_cp_40}**",
                    inline=False)
    embed.add_field(name="Fast moves:", value=fast_moves, inline=True)
    embed.add_field(name="\u200b", value="\u200b", inline=True)
    embed.add_field(name="Charge moves:", value=charge_moves, inline=True)
    return embed


def filter_pokemon_leftovers_from_gym(report: list) -> list:
    """Removes pokemon leftovers such as 'form' from the gym name"""
    filter_list = ["form"]
    return [word for word in report if word.lower() not in filter_list]


def _remove_found_pokemon_from_report(report: list, pokemon: str) -> str:
    """Attempts to remove the pokemon"""
    report = filter_pokemon_leftovers_from_gym(report)
    pokemon_list = pokemon.upper().split(" ")
    report_list = list(map(str.upper, report))

    [report_list.remove(word) for word in pokemon_list if word in report_list]
    return " ".join(report_list).title()


def _find_pokemon_and_gym(*report) -> (str, str):
    """Attempts to find the pokemon and gym in a printreport"""
    if valid_time_hhmm(report[-1]) is not None or valid_time_mm(report[-1]):
        report = report[:-1]

    pokemon = report[0]
    pokemon_and_gym_converted = list(map(str.upper, report))

    proper_matches = []
    backup_matches = []
    for key in common_instances.POKEDEX.pokedict.keys():
        set_key = set(key.split(" "))
        if set_key.issubset(set(pokemon_and_gym_converted)):
            proper_matches.append(key)
        if pokemon.upper() in key:
            backup_matches.append(key)

    if proper_matches:
        pokemon = max(proper_matches, key=len)
    elif backup_matches:
        pokemon = min(backup_matches, key=len)

    if report[0].upper() in common.RAID_EGG_TYPES:
        intersection = set(pokemon_and_gym_converted).intersection(pokemon.split(" "))
        if len(intersection) < 2:
            pokemon = report[0].upper()

    return pokemon, _remove_found_pokemon_from_report(pokemon_and_gym_converted, pokemon)


def _find_channel_index_by_hatch_time(hatch_time: datetime):
    """Finds the position the channel should be created in by comparing hatch_times"""
    active_raids = execute_statement(create_select_query(table_name=common.ACTIVE_RAID_CHANNEL_OWNERS)).all(as_dict=True)
    hatch_times = [hatch_time]
    for raid in active_raids:
        hatch_times.append(valid_time_hhmm(raid.get("hatch_time")))
    return sorted(hatch_times).index(hatch_time)


async def _create_channel_and_information(bot, ctx, *report):
    at_time_or_train = report[-1]
    pokemon, gym = _find_pokemon_and_gym(*report)

    if not gym:
        await ctx.send(f"Your raid does not include a gym name {ctx.author.mention}, use *?help raid* for details")
        return

    if common_instances.POKEDEX.lookup(pokemon) is None:
        pokemon_spell_checked = common_instances.SPELLCHECKER.correction(pokemon)
        if common_instances.POKEDEX.lookup(pokemon_spell_checked) is not None:
            pokemon = pokemon_spell_checked

    maybe_valid_hatch_time = valid_time_hhmm(at_time_or_train)
    maybe_valid_despawn_time = valid_time_mm(at_time_or_train)

    # TODO: position argument doesn't set channel at that position, temp commented until fixed
    if maybe_valid_despawn_time is not None:
        created_channel = await ctx.guild.create_text_channel(
            name=f"{pokemon}_{gym}_{format_as_hhmm(datetime.now() - timedelta(minutes=45-maybe_valid_despawn_time.minute))}",
            category=ctx.channel.category)
            # position=_find_channel_index_by_hatch_time(datetime.now() - timedelta(minutes=45-maybe_valid_despawn_time.minute)) + 1)
    elif maybe_valid_hatch_time is not None:
        created_channel = await ctx.guild.create_text_channel(
            name=f"{pokemon}_{gym}_{at_time_or_train}",
            category=ctx.channel.category)
            # position=_find_channel_index_by_hatch_time(maybe_valid_hatch_time) + 1)
    else:
        created_channel = await ctx.guild.create_text_channel(name=f"{pokemon}_{gym}", category=ctx.channel.category)

    if maybe_valid_hatch_time is None and maybe_valid_despawn_time is None:
        if at_time_or_train == "train":
            hatch_time = "Train channel, discuss hatch times"
            schedule_reminding_task(bot, ctx, created_channel, f"Do not forget to *?close* this channel when you are done {ctx.author.mention}", "empty", "hourly")
        else:
            hatch_time = "Hatched!"
            schedule_reminding_task(bot, ctx, created_channel, f"This channel will close in 1 minute", format_as_hhmm(datetime.now() + timedelta(minutes=59)), "daily")
            schedule_delete_channel_at(bot, ctx, created_channel, format_as_hhmm(datetime.now() + timedelta(hours=1)))
    elif maybe_valid_hatch_time is not None:
        hatch_time = format_as_hhmm(maybe_valid_hatch_time)
        schedule_reminding_task(bot, ctx, created_channel, f"This channel will close in 1 minute", format_as_hhmm(maybe_valid_hatch_time + timedelta(minutes=59)), "daily")
        schedule_delete_channel_at(bot, ctx, created_channel, format_as_hhmm(maybe_valid_hatch_time + timedelta(hours=1)))
    else:
        calculated_hatch_time = datetime.now() - timedelta(minutes=45-maybe_valid_despawn_time.minute)
        hatch_time = format_as_hhmm(calculated_hatch_time)
        schedule_reminding_task(bot, ctx, created_channel, f"This channel will close in 1 minute", format_as_hhmm(calculated_hatch_time + timedelta(minutes=59)), "daily")
        schedule_delete_channel_at(bot, ctx, created_channel, format_as_hhmm(calculated_hatch_time + timedelta(hours=1)))

    execute_statement(create_insert_query(
        table_name=common.ACTIVE_RAID_CHANNEL_OWNERS,
        keys="(channel_id, reporter_id, pokemon, gym, hatch_time, last_updated)",
        values=f"('{created_channel.id}', '{ctx.author.id}', '{pokemon}', '{gym}', '{hatch_time}', 'empty')"))

    await ctx.send(f"{ctx.author.mention} has created a raid in {created_channel.mention}, why don't you join them?")
    await _send_embed(bot, ctx, created_channel, pokemon, gym, hatch_time)


class Raid(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="raid")
    @in_channel_list(common.RAID_REPORT_CHANNEL_LIST)
    async def raid(self, ctx, *args):
        """
        ?raid <pokemon/egg_type> <gym> [hatch time/minutes to despawn]

        Example (if T5 egg hatches at 18:15): ?raid T5 Klockstapeln 18:15
        Example (if a Mewtwo raid despawns in 33 minutes): ?raid Mewtwo Klockstapeln 33

        Creates a raid channel that will automatically be deleted 15 minutes after the raid despawns
        Egg types: [T1, T3, T5, MEGA]

        Type ?help update, when you are in the created raid channel, for more information.
        """
        validated_report = _validate_report(*args)
        if len(validated_report) > 1:
            await ctx.send(f"{validated_report} {ctx.author.mention}")
            return

        await _create_channel_and_information(self.bot, ctx, *args)
        await update_raids_channel(self.bot, ctx)

    @raid.error
    async def raid_on_error(self, _, error):
        await pm_dev_error(bot=self.bot, error_message=error, source="Raid")


def setup(bot):
    bot.add_cog(Raid(bot))