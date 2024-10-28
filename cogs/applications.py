import disnake
from disnake.ext import commands
import config


class ApplicationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Команда для создания заявки
    @commands.command()
    async def apply(self, ctx):
        embed = disnake.Embed(
            title="Набор",
            description="**Требования**\n\n"
                        "```От вас: ```\n"
                        "Возраст от 15-ти лет.\n"
                        "Адекватное поведение.\n"
                        "Иметь уже 14-ть отсиженных часов в войсе.\n"
                        "```От нас:```\n"
                        "Приятный коллектив.\n"
                        "Развитие и повышение.\n"
                        "Достойная зп.\n"
                        "Розыгрыши между стаффом.\n\n"
                        "**По вопросам пишите в ЛС**"
                        "<@1248631962038567042> или <@614131343030485002>",
            color=0x6d6161
        )

        button = disnake.ui.Button(
            label="Создать заявку",
            style=disnake.ButtonStyle.primary,
            custom_id="create_application"
        )

        view = disnake.ui.View()
        view.add_item(button)
        embed.set_footer(text="Неадекватные заявки будут наказываться")

        await ctx.send(embed=embed, view=view)

    # Обработка нажатия кнопки
    @commands.Cog.listener()
    async def on_interaction(self, interaction: disnake.MessageInteraction):
        if interaction.data['custom_id'] == "create_application":
            modal = disnake.ui.Modal(
                title="Форма Заявки",
                custom_id="application_form",
                components=[
                    disnake.ui.TextInput(
                        label="Ваше имя и возраст",
                        placeholder="Введите ваше имя и возраст",
                        custom_id="name_age"
                    ),
                    disnake.ui.TextInput(
                        label="Ваша адекватность (1/10)",
                        placeholder="",
                        custom_id="purpose",
                    ),
                    disnake.ui.TextInput(
                        label="В какие игры играете?",
                        placeholder="",
                        custom_id="time",
                        style=disnake.TextInputStyle.paragraph
                    ),
                ]
            )
            await interaction.response.send_modal(modal)

    # Обработка отправки формы
    @commands.Cog.listener()
    async def on_modal_submit(self, interaction: disnake.ModalInteraction):
        if interaction.custom_id == "application_form":
            name_age = interaction.text_values["name_age"]
            purpose = interaction.text_values["purpose"]
            time = interaction.text_values["time"]

            admin_channel = self.bot.get_channel(config.chanelid)

            embed = disnake.Embed(
                title="Новая заявка",
                description=f"{interaction.author.mention} ({interaction.author.id})\n\n"
                            f"**Имя и возраст**\n```{name_age}```\n"
                            f"**Ваша адекватность (1/10)**\n```{purpose}```\n"
                            f"**В какие игры играете?**\n```{time}```",
                color=0x6d6161
            )
            embed.set_thumbnail(url=interaction.author.avatar.url)

            view = disnake.ui.View()
            view.add_item(disnake.ui.Button(label="", style=disnake.ButtonStyle.green, emoji="✅",
                                            custom_id=f"approve_{interaction.author.id}"))
            view.add_item(disnake.ui.Button(label="", style=disnake.ButtonStyle.red, emoji="❌",
                                            custom_id=f"reject_{interaction.author.id}"))

            await admin_channel.send(embed=embed, view=view)
            await interaction.response.send_message("Ваша заявка была отправлена.", ephemeral=True)

    # Обработка нажатий на кнопки "Одобрить" и "Отклонить"
    @commands.Cog.listener()
    async def on_button_click(self, interaction: disnake.MessageInteraction):
        if interaction.user.id not in [config.checker]:
            await interaction.response.send_message("Вы не имеете права выполнять это действие.", ephemeral=True)
            return

        custom_id_parts = interaction.data['custom_id'].split('_')
        action = custom_id_parts[0]
        user_id = int(custom_id_parts[1])

        embed = interaction.message.embeds[0]
        if action == "approve":
            role_id = 1295695656987525120  # Укажите ID роли
            role = disnake.utils.get(interaction.guild.roles, id=role_id)
            member = interaction.guild.get_member(user_id)
            embed.description += f"\n\n**Статус**: Одобрено"
            embed.color = 0x2ecc71
            await interaction.message.edit(embed=embed, view=None)

            try:
                await member.add_roles(role)
            except disnake.errors.Forbidden:
                await interaction.response.send_message(
                    f"У меня нет прав для выдачи роли {role.name}. Свяжитесь с администратором сервера.",
                    ephemeral=True)

            try:
                embed_dm = disnake.Embed(
                    title="Ваша заявка была одобрена",
                    description="Ваша заявка одобрена.",
                    color=0x2ecc71
                )
                await member.send(embed=embed_dm)
            except disnake.errors.HTTPException:
                pass
        elif action == "reject":
            embed.description += f"\n\n**Статус**: Отклонено"
            embed.color = 0xe74c3c
            await interaction.message.edit(embed=embed, view=None)
            await interaction.response.send_message("Заявка отклонена.", ephemeral=True)

            member = interaction.guild.get_member(user_id)
            try:
                embed_dm = disnake.Embed(
                    title="Ваша заявка была отклонена",
                    description="Ваша заявка отклонена.",
                    color=0xe74c3c
                )
                await member.send(embed=embed_dm)
            except disnake.errors.HTTPException:
                pass


def setup(bot):
    bot.add_cog(ApplicationCog(bot))
