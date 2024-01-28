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
