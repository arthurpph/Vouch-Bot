import discord

from datetime import datetime

data_format = "%Y-%m-%d %H:%M:%S"


def convert_data_to_discord_format(string_date: str):
    data_object = datetime.strptime(string_date, data_format)

    data_discord = discord.utils.format_dt(data_object, style="f")

    return data_discord


def get_past_time_in_months(string_date: str):
    date = datetime.strptime(string_date, data_format)

    current_date = datetime.now()

    months_difference = (current_date.year - date.year) * 12 + current_date.month - date.month

    return months_difference
