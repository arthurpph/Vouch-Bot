from typing import Any

import discord
from discord import SelectOption, Guild, Interaction
from discord.ui import Select

from vouch import Vouch
from utils import get_date_from_string_date, get_time_from_string_date
from exceptions import DeleteVouchError


class deleteVouchDropdown(Select):
    def __init__(self, guild: Guild, user_id: int, rank_name: str):
        self.user_id = user_id

        formatted_rank = rank_name.replace("ã", "a")

        options = []
        for vouch_id in Vouch.get_user_vouches(user_id):
            if Vouch.get_vouch(user_id, vouch_id) == formatted_rank:
                member = guild.get_member(Vouch.get_attributed_by(user_id, vouch_id))
                date = Vouch.get_date(user_id, vouch_id)

                options.append(
                    SelectOption(label=f"Atribuido por {'Usuário não encontrado' if not member else member.name}",
                                 value=vouch_id,
                                 description=f"{get_date_from_string_date(date)} às {get_time_from_string_date(date)}"))

        if len(options) == 0:
            options.append(SelectOption(label="Usuário não possui nenhum vouch para a divisão selecionada", value="null"))

        super().__init__(placeholder="Escolha um vouch", options=options)

    async def callback(self, interaction: Interaction[ClientT]) -> Any:
        selected_values = interaction.data['values']

        if not selected_values or selected_values[0] == "null":
            return

        deleted_vouch = Vouch.delete_vouch(self.user_id, selected_values[0])

        if not deleted_vouch:
            raise DeleteVouchError("Erro ao deletar o vouch")

        await interaction.response.send_message("Vouch deletado!", ephemeral=True)


class DeleteVouchView(discord.ui.View):
    def __init__(self, guild: Guild, user_id: int, rank_name: str):
        super().__init__()
        self.add_item(deleteVouchDropdown(guild, user_id, rank_name))