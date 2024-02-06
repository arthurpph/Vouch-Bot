import discord
from discord import app_commands, User, Forbidden, Embed
from discord.ext import commands

import utils
from utils import check_permission, check_permission_only_staff
from main import div_roles

from config import Config
from vouch import Vouch
from utils import convert_data_to_discord_format, get_past_time_in_months, convert_name_to_role, convert_role_to_name, \
    promote_player
from logger import get_logger
from exceptions import InsufficientPermission, InvalidChannelId, InvalidUser, InvalidRole
from dropdowns import delete_vouch

logger = get_logger()


class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="disponivel", description="Anúncia que você está disponível para batalha")
    @app_commands.describe(modo="Escolha o modo")
    @app_commands.choices(modo=[
        app_commands.Choice(name="1v1", value=1),
        app_commands.Choice(name="2v2", value=2),
        app_commands.Choice(name="3v3", value=3),
        app_commands.Choice(name="4v4", value=4)
    ])
    async def disponivel(self, ctx: commands.Context, modo: app_commands.Choice[int]):
        logger.info(f"Command: /disponivel {modo} by {ctx.user.name}")

        if not check_permission(ctx):
            await ctx.response.send_message(
                embed=Embed(color=discord.Color.blue(), description="Você não tem permissão para executar isso!"),
                ephemeral=True)
            return

        guild = ctx.guild

        div_council_roles = Config.get_div_council_roles_id()
        allowed = False
        for role_2 in ctx.user.roles:
            if role_2.id in div_council_roles:
                allowed = True
                break

        if not allowed:
            await ctx.response.send_message(
                embed=Embed(color=discord.Color.blue(), description="Você não tem permissão para executar isso!"),
                ephemeral=True)
            return

        council_duels_id = Config.get_council_duels_role_id()
        council_duels_role = guild.get_role(council_duels_id)
        if not council_duels_role:
            await ctx.response.send_message(
                embed=Embed(color=discord.Color.blue(), description="Cargo council duels inválido"), ephemeral=True)
            return

        await ctx.response.send_message("Mensagem criada!", ephemeral=True)
        await ctx.channel.send(
            f"{ctx.user.mention} está disponível para duelos de vouch {modo.name} {council_duels_role.mention}!")

    @app_commands.command(name="give_vouch", description="Atribui um vouch a um usuário")
    @app_commands.describe(usuario="Escolha o usuário", descricao="Adicione uma descrição")
    async def give_vouch(self, ctx: commands.Context, usuario: User, descricao: str):
        logger.info(f"Command: /give_vouch {usuario} {descricao} by {ctx.user.name}")

        if not check_permission(ctx):
            await ctx.response.send_message(
                embed=Embed(color=discord.Color.blue(), description="Você não tem permissão para executar isso!"),
                ephemeral=True)
            return

        Vouch.add_vouch(usuario, descricao, ctx.user.id)

        try:
            await usuario.send(
                embed=Embed(color=discord.Color.blue(), description=f"Você recebeu um vouch por {ctx.user.mention}!"))
        except Forbidden:
            pass

        embed = Embed(color=discord.Color.blue(), description="Vouch adicionado!")
        await ctx.response.send_message(embed=embed, ephemeral=True)

        guild = ctx.guild
        if utils.check_promotion(guild, usuario.id):
            await promote_player(guild, guild.get_member(usuario.id))

    @app_commands.command(name="delete_vouch", description="Deleta um vouch de um jogador")
    @app_commands.describe(usuario="Escolha o usuário", rank="Escolha um rank")
    @app_commands.choices(rank=[
        app_commands.Choice(name="Divisão 1", value=1),
        app_commands.Choice(name="Divisão 2", value=2),
        app_commands.Choice(name="Divisão 3", value=3),
    ])
    async def delete_vouch(self, ctx: commands.Context, usuario: User, rank: app_commands.Choice[int]):
        logger.info(f"Command: /delete_vouch {usuario} {rank.name} by {ctx.user.name}")

        if not check_permission_only_staff(ctx):
            await ctx.response.send_message(
                embed=Embed(color=discord.Color.blue(), description="Você não tem permissão para executar isso!"),
                ephemeral=True)
            return

        await ctx.response.send_message(view=delete_vouch.DeleteVouchView(ctx.guild, usuario.id, rank.name),
                                        ephemeral=True)

    @app_commands.command(name="vouches", description="Mostra os vouches de um jogador")
    @app_commands.describe(usuario="Escolha o usuário", rank="Escolha um rank")
    @app_commands.choices(rank=[
        app_commands.Choice(name="Divisão 1", value=1),
        app_commands.Choice(name="Divisão 2", value=2),
        app_commands.Choice(name="Divisão 3", value=3),
    ])
    async def vouches(self, ctx: commands.Context, usuario: User, rank: app_commands.Choice[int]):
        logger.info(f"Command: /vouches {usuario} {rank.name} by {ctx.user.name}")

        guild = ctx.guild

        if not Vouch.user_has_vouches(usuario.id):
            embed = Embed(description=f"{usuario.mention} nunca recebeu nenhum vouch.", color=discord.Color.blue())
            await ctx.response.send_message(embed=embed)
            return

        expired = 0

        embed = Embed(title=f"{rank.name} Vouches", color=discord.Color.blue())
        embed.set_author(name=f"{usuario.name} ({usuario.id})", icon_url=usuario.avatar)

        formatted_rank = rank.name.replace("ã", "a")

        try:
            for vouch_id in Vouch.get_user_vouches(usuario.id):
                attributed_by_user = guild.get_member(Vouch.get_attributed_by(usuario.id, vouch_id))
                if not attributed_by_user:
                    raise InvalidUser("Usuário que atribuiu o vouch é inválido")

                vouch_issued_at = Vouch.get_date(usuario.id, vouch_id)

                if get_past_time_in_months(vouch_issued_at) >= 4:
                    expired += 1

                if Vouch.get_vouch(usuario.id, vouch_id) == formatted_rank:
                    embed.add_field(
                        name=f"{attributed_by_user.name} Vouch | {convert_data_to_discord_format(vouch_issued_at)}",
                        value=f"Concedido por {attributed_by_user.mention} por {Vouch.get_description(usuario.id, vouch_id)}",
                        inline=False)

            if len(embed.fields) == 0:
                embed_temp = Embed(color=discord.Color.blue(),
                                   description=f"{usuario.mention} não tem nenhum vouch para esta divisão")
                await ctx.response.send_message(embed=embed_temp)
                return

        except InvalidUser as e:
            embed = Embed(color=discord.Color.blue(), description=f"Erro: {e}")
            await ctx.response.send_message(embed=embed, ephemeral=True)
            return

        embed.set_footer(text=f"+ {str(expired)} Vouch(es) expirados\n"
                              f"(Vouches expiram depois de 4 meses)")

        await ctx.response.send_message(embed=embed)

    @app_commands.command(name="promote", description="Promove um usuário para uma divisão")
    @app_commands.describe(usuario="Escolha um usuário", rank="Escolha um rank")
    @app_commands.choices(rank=[
        app_commands.Choice(name="Divisão 1", value=1),
        app_commands.Choice(name="Divisão 2", value=2),
        app_commands.Choice(name="Divisão 3", value=3),
    ])
    async def promote(self, ctx: commands.Context, usuario: User, rank: app_commands.Choice[int]):
        logger.info(f"Command: /promote {usuario} {rank.name} by {ctx.user.name}")

        if not check_permission_only_staff(ctx):
            await ctx.response.send_message(
                embed=Embed(color=discord.Color.blue(), description="Você não tem permissão para executar isso!"),
                ephemeral=True)
            return

        guild = ctx.guild
        member = await guild.fetch_member(usuario.id)
        channel = guild.get_channel(int(Config.get_promotions_channel_id()))

        try:
            if not guild.me.guild_permissions.manage_roles:
                raise InsufficientPermission("Não tenho permissão para gerenciar cargos")

            if not channel:
                raise InvalidChannelId("ID do canal de promoções é inválido")

            role_name_formatted = rank.name.replace("ã", "a")
            role = guild.get_role(convert_name_to_role(role_name_formatted))

            if not role:
                raise InvalidRole("Cargo da divisão é inválido")

            if role in member.roles:
                embed = Embed(color=discord.Color.blue(), description=f"{member.mention} já está nesta divisão")
                await ctx.response.send_message(embed=embed, ephemeral=True)
                return

            casual_role = guild.get_role(int(Config.get_casual_role_id()))

            if not casual_role:
                raise InvalidRole("Cargo 'casual' é inválido")

            try:
                for member_role in member.roles:
                    if member_role.id in div_roles:
                        await member.remove_roles(member_role)

                if casual_role in member.roles:
                    await member.remove_roles(casual_role)

                await member.add_roles(role)
            except Forbidden:
                await ctx.response.send_message(
                    embed=Embed(color=discord.Color.blue(), description="Eu não tenho permissão para editar cargos."),
                    ephemeral=True)
                return

            embed = Embed(color=discord.Color.blue(), description="Usuário promovido com sucesso!")
            await ctx.response.send_message(embed=embed, ephemeral=True)

            try:
                await usuario.send(
                    embed=Embed(color=role.color, description=f"Parabéns! Você foi promovido para {rank.name}!"))
            except Forbidden:
                pass

            await channel.send(embed=Embed(color=discord.Color.blue(), title="Promoção",
                                           description=f"{ctx.user.mention} promoveu {member.mention} para {role.mention}!"))
        except InsufficientPermission as e:
            embed = Embed(description=f"Erro: {e}")
            await ctx.response.send_message(embed=embed, ephemeral=True)
        except InvalidChannelId as e:
            embed = Embed(description=f"Erro: {e}")
            await ctx.response.send_message(embed=embed, ephemeral=True)
        except InvalidRole as e:
            embed = Embed(description=f"Erro: {e}")
            await ctx.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="purge", description="Rebaixa um usuário")
    @app_commands.describe(usuario="Escolha o usuário")
    async def purge(self, ctx: commands.Context, usuario: User):
        logger.info(f"Command: /purge {usuario} by {ctx.user.name}")

        if not check_permission_only_staff(ctx):
            await ctx.response.send_message(
                embed=Embed(color=discord.Color.blue(), description="Você não tem permissão para executar isso!"),
                ephemeral=True)
            return

        guild = ctx.guild
        member = await guild.fetch_member(usuario.id)
        casual = guild.get_role(int(Config.get_casual_role_id()))

        if not guild.me.guild_permissions.manage_roles:
            embed = Embed(color=discord.Color.blue(), description="Não tenho permissão para alterar cargos")
            await ctx.response.send_message(embed=embed, ephemeral=True)
            return

        if not member:
            embed = Embed(color=discord.Color.blue(), description="Usuário não encontrado no servidor")
            await ctx.response.send_message(embed=embed, ephemeral=True)
            return

        try:
            if not casual:
                embed = Embed(color=discord.Color.blue(), description="Cargo 'casual' não existe")
                await ctx.response.send_message(embed=embed, ephemeral=True)
                return

            role = await utils.get_previous_role(ctx, usuario)

            guild_role = guild.get_role(role)
            if not guild_role:
                await ctx.response.send_message(embed=Embed(color=discord.Color.blue(), description="Cargo não encontrado no servidor"), ephemeral=True)
                return

            for role in member.roles:
                if role.id in div_roles:
                    await member.remove_roles(role)

            await member.add_roles(guild_role)
            await ctx.response.send_message(
                embed=Embed(color=discord.Color.blue(), description="Usuário rebaixado com sucesso"), ephemeral=True)
        except Forbidden:
            await ctx.response.send_message(
                embed=Embed(color=discord.Color.blue(), description="Não tenho permissão para executar isso"),
                ephemeral=True)

    @app_commands.command(name="purge_list", description="Cria um tópico para votação")
    @app_commands.describe(usuario="Escolha o usuário")
    async def purge_list(self, ctx: commands.Context, usuario: User):
        logger.info(f"Command: /purge_list {usuario} by {ctx.user.name}")

        if not check_permission_only_staff(ctx):
            await ctx.response.send_message(
                embed=Embed(color=discord.Color.blue(), description="Você não tem permissão para executar isso!"),
                ephemeral=True)
            return

        await ctx.response.defer(ephemeral=True)

        guild = ctx.guild
        member = await guild.fetch_member(usuario.id)
        member_div = utils.convert_role_to_name(member)
        member_div_int = int(member_div.split(" ")[1])
        forum_channel = guild.get_channel(Config.get_div_purge_forum_id(member_div_int))
        div_council_role = guild.get_role(Config.get_div_council_role_id(member_div_int))

        if not member:
            await ctx.followup.send(embed=Embed(color=discord.Color.blue(), description="Usuário não encontrado no servidor"), ephemeral=True)
            return

        if not forum_channel:
            await ctx.followup.send(embed=Embed(color=discord.Color.blue(), description="Canal de purges não encontrado no servidor"), ephemeral=True)
            return

        if not div_council_role:
            await ctx.followup.send(embed=Embed(color=discord.Color.blue(), description="Cargo de div council não encontrado no servidor"), ephemeral=True)
            return

        new_thread = await forum_channel.create_thread(name=ctx.user.name, content=div_council_role.mention)
        await new_thread.message.add_reaction("✅")
        await new_thread.message.add_reaction("❌")

        await ctx.followup.send(embed=Embed(color=discord.Color.blue(), description="Thread criada!"), ephemeral=True)

    async def cog_app_command_error(self, ctx: commands.Context, error: Exception) -> None:
        logger.error(error)

        try:
            await ctx.response.defer(ephemeral=True)
        except Exception:
            pass

        await ctx.followup.send(embed=Embed(color=discord.Color.blue(), title="Erro", description=f"{error.original}\n\n Por favor reporte para shauuu\_"))

async def setup(bot):
    await bot.add_cog(Commands(bot))
