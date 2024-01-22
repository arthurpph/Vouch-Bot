from discord import app_commands, User, Role, Forbidden
from discord.ext import commands
from main import div_roles

from exceptions import InsufficientPermission, InvalidChannelId

from config import Config


class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="disponivel", description="Anúncia que você está disponível para batalha")
    @app_commands.describe(modo="modo")
    async def disponivel(self, ctx: commands.Context, modo: str):
        global channelId
        guild = ctx.guild

        if modo == "1v1":
            channelId = Config.get_div_log_channel_id(1)
        elif modo == "2v2":
            channelId = Config.get_div_log_channel_id(2)
        else:
            await ctx.response.send_message("Modo de jogo inválido")
            return

        channel = guild.get_channel(int(channelId))
        if not channel:
            await ctx.response.send_message("Chat inválido, nenhuma ação foi realizada")
            return

        council_duels_role = guild.get_role(int(Config.get_council_duels_role_id()))
        if not council_duels_role:
            await ctx.response.send_message("Cargo 'Council Duels' inválido, nenhuma ação foi realizada")

        await channel.send(f"{ctx.user.mention} está disponível para duelos de vouch {modo} {council_duels_role.mention}!")
        await ctx.response.send_message("Aviso criado!", ephemeral=True)

    @app_commands.command(name="promote", description="Promove um usuário para uma divisão")
    @app_commands.describe(user="usuário", role="cargo")
    async def promote(self, ctx: commands.Context, user: User, role: Role):
        guild = ctx.guild
        member = await guild.fetch_member(user.id)
        channel = guild.get_channel(int(Config.get_promotions_channel_id()))

        try:
            if not guild.me.guild_permissions.manage_roles:
                raise InsufficientPermission("Não tenho permissão para gerenciar cargos")

            if not channel:
                raise InvalidChannelId("ID do canal de promoções é inválido")

            if role in member.roles:
                await ctx.response.send_message(f"{member.mention} já está nesta divisão", ephemeral=True)
                return

            for member_role in member.roles:
                if member_role.id in div_roles:
                    await member.remove_roles(member_role)

            casual_role = guild.get_role(int(Config.get_casual_role_id()))
            if casual_role in member.roles:
                await member.remove_roles(casual_role)

            await member.add_roles(role)
            await channel.send(f"{ctx.user.mention} promoveu {member.mention}!")
            await ctx.response.send_message("Usuário promovido com sucesso!", ephemeral=True)
        except InsufficientPermission as e:
            await ctx.response.send_message(f"Erro: {e}", ephemeral=True)
        except InvalidChannelId as e:
            await ctx.response.send_message(f"Erro: {e}", ephemeral=True)

    @app_commands.command(name="purge", description="comando teste")
    @app_commands.describe(user="usuário")
    async def purge(self, ctx: commands.Context, user: User):
        guild = ctx.guild
        member = await guild.fetch_member(user.id)
        casual = guild.get_role(int(Config.get_casual_role_id()))

        if not guild.me.guild_permissions.manage_roles:
            await ctx.response.send_message("Não tenho permissão para alterar cargos", ephemeral=True)
            return

        if not member:
            await ctx.response.send_message("Usuário não encontrado no servidor", ephemeral=True)
            return

        try:
            if not casual:
                await ctx.response.send_message("Cargo 'Casual' não existe, nenhuma ação foi realizada", ephemeral=True)
                return

            for role in member.roles:
                if role.id in div_roles:
                    await member.remove_roles(role)

            await member.add_roles(casual)
            await ctx.response.send_message("Usuário removido com sucesso", ephemeral=True)
        except Forbidden:
            await ctx.response.send_message("Não tenho permissão para executar isso", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Commands(bot))
