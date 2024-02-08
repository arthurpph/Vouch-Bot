"""
:author: Shau
"""

import discord
from discord import Member, Embed, Forbidden

from datetime import datetime

from config import Config
import vouch

data_format = "%Y-%m-%d %H:%M:%S"
brazilian_date_format = "%d/%m/%Y"


def convert_data_to_discord_format(string_date: str):
    data_object = datetime.strptime(string_date, data_format)

    data_discord = discord.utils.format_dt(data_object, style="f")

    return data_discord


def get_date_from_string_date(string_date: str):
    return datetime.strptime(string_date, data_format).date()


def get_time_from_string_date(string_date: str):
    return datetime.strptime(string_date, data_format).time()


def get_past_time_in_months(string_date: str):
    date = datetime.strptime(string_date, data_format)

    current_date = datetime.now()

    months_difference = (current_date.year - date.year) * 12 + current_date.month - date.month

    return months_difference


def convert_name_to_role(name):
    global role_id

    if name == "Divisao 1":
        role_id = Config.get_div_role_id(1)
    elif name == "Divisao 2":
        role_id = Config.get_div_role_id(2)
    elif name == "Divisao 3":
        role_id = Config.get_div_role_id(3)
    elif name == "Casual":
        role_id = Config.get_casual_role_id()
    else:
        return None

    return role_id


def convert_role_to_name(member: Member):
    div_roles = Config.get_div_roles_id()
    casual_role = Config.get_casual_role_id()

    for role in member.roles:
        if role.id in div_roles:
            if div_roles[0] == role.id:
                return "Divisao 1"
            elif div_roles[1] == role.id:
                return "Divisao 2"
            elif div_roles[2] == role.id:
                return "Divisao 3"
            else:
                return None
        elif role.id == casual_role:
            return "Casual"

    return None


async def promote_player(guild: discord.Guild, member: Member):
    casual_role = guild.get_role(int(Config.get_casual_role_id()))
    div_roles = Config.get_div_roles_id()
    promotion_role_name = vouch.Vouch.get_vouch_name(member)
    role = guild.get_role(convert_name_to_role(promotion_role_name))
    channel = guild.get_channel(int(Config.get_promotions_channel_id()))

    for member_role in member.roles:
        if member_role.id in div_roles:
            await member.remove_roles(member_role)

        if casual_role in member.roles:
            await member.remove_roles(casual_role)

        await member.add_roles(role)

    try:
        await member.send(
            embed=Embed(color=role.color,
                        description=f"Parabéns! Você foi promovido para {promotion_role_name.replace('a', 'ã')}!"))
    except Forbidden:
        pass

    await channel.send(embed=Embed(color=discord.Color.blue(), title="Promoção",
                                   description=f"{member.mention} foi promovido automaticamente para {role.mention}!"))


async def get_previous_role(ctx, user):
    role_name = convert_role_to_name(ctx.guild.get_member(user.id))
    if not role_name:
        await ctx.response.send_message(
            embed=Embed(color=discord.Color.blue(), description="Role name inválido"), ephemeral=True)
        return

    if role_name == "Divisao 1":
        return Config.get_div_role_id(2)
    elif role_name == "Divisao 2":
        return Config.get_div_role_id(3)
    elif role_name == "Divisao 3":
        return Config.get_casual_role_id()

    await ctx.response.send_message(
        embed=Embed(color=discord.Color.blue(), description=f"{user.mention} já está no rank Casual"),
        ephemeral=True)

def get_next_role(guild, user):
    role_name = convert_role_to_name(guild.get_member(user.id))

    if role_name == "Divisao 1":
        return "Divisao 1A"
    elif role_name == "Divisao 2":
        return "Divisao 1"
    elif role_name == "Divisao 3":
        return "Divisao 2"
    else:
        return "Divisao 3"


def check_permission(ctx):
    div_council_roles_id = Config.get_div_council_roles_id()
    staff_roles = Config.get_staff_roles_id()

    for role in ctx.user.roles:
        if any(role.id in list for list in [div_council_roles_id, staff_roles]):
            return True

    return False


def check_permission_only_staff(ctx):
    staff_roles = Config.get_staff_roles_id()

    for role in ctx.user.roles:
        for staff_role_id in staff_roles:
            if role.id == staff_role_id:
                return True

    return False

def check_div_or_above_permission(ctx):
    div_roles = Config.get_div_roles_id()

    for role in ctx.user.roles:
        if role.id in div_roles:
            return True

    return False


def get_minimum_promotion_vouches(guild: discord.Guild, user_id: int):
    role_name = convert_role_to_name(guild.get_member(user_id))
    if role_name == "Divisao 2":
        return 2
    elif role_name == "Divisao 3":
        return 4
    elif role_name == "Casual":
        return 5
    else:
        return None


def get_promotion_vouches(guild: discord.Guild, user_id):
    next_role = get_next_role(guild, guild.get_member(user_id))

    vouches = 0

    for vouch_id in vouch.Vouch.get_user_vouches(user_id):
        if vouch.Vouch.get_vouch(user_id, vouch_id) == next_role:
            vouches += 1

    return vouches


def check_promotion(guild: discord.Guild, user_id: int):
    user_vouches = vouch.Vouch.get_user_vouches(user_id)
    minimum_promotion = get_minimum_promotion_vouches(guild, user_id)
    vouches_for_next_rank = get_promotion_vouches(guild, user_id)

    if user_vouches and minimum_promotion is not None and vouches_for_next_rank >= minimum_promotion:
        return True

    return False
