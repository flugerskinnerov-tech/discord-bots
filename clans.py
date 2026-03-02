import discord
from discord.ext import commands
import json
import os
from datetime import datetime

# Настройки бота
TOKEN = 'MTQ2ODU0MjgzNzEwNzk4NjY0Ng.GGEW5a.xxaAw4RsnW1FiKE1L7Pfv0TLEzdk7VdgjiFLZQ'
PREFIX = '*'
CLAN_DATA_FILE = 'clans.json'
ADMIN_ROLE_NAME = 'Clan Admin'

# Намерения бота
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

# Загрузка данных кланов
def load_clan_data():
    if os.path.exists(CLAN_DATA_FILE):
        with open(CLAN_DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

# Сохранение данных кланов
def save_clan_data(data):
    with open(CLAN_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Получение данных клана
def get_clan_data(guild_id):
    data = load_clan_data()
    if str(guild_id) not in data:
        data[str(guild_id)] = {
            'clans': {},
            'config': {
                'max_clans': 10,
                'max_members_per_clan': 50,
                'clan_leader_role': 'Clan Leader',
                'clan_member_role': 'Clan Member'
            }
        }
        save_clan_data(data)
    return data[str(guild_id)]

# Сохранение данных клана для конкретного сервера
def save_guild_clan_data(guild_id, guild_data):
    data = load_clan_data()
    data[str(guild_id)] = guild_data
    save_clan_data(data)

# Создание ролей и каналов для клана
async def create_clan_resources(guild, clan_name):
    # Создаем роль для клана
    clan_role = await guild.create_role(
        name=f"Clan: {clan_name}",
        color=discord.Color.random(),
        hoist=True,
        mentionable=True
    )
    
    # Создаем приватную категорию для клана
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        clan_role: discord.PermissionOverwrite(read_messages=True)
    }
    
    category = await guild.create_category(
        name=f"⚔️ {clan_name}",
        overwrites=overwrites
    )
    
    # Создаем текстовые каналы
    general_channel = await category.create_text_channel(
        name="общее",
        topic=f"Основной чат клана {clan_name}"
    )
    
    voice_channel = await category.create_voice_channel(
        name=f"Голосовой {clan_name}"
    )
    
    return clan_role, category, general_channel, voice_channel

# События бота
@bot.event
async def on_ready():
    print(f'============================================')
    print(f'Бот Instant Clans успешно запущен!')
    print(f'Имя: {bot.user.name}')
    print(f'ID: {bot.user.id}')
    print(f'Префикс команд: {PREFIX}')
    print(f'============================================')
    
    # Устанавливаем статус бота
    activity = discord.Activity(
        name=f"{PREFIX}info - информация о командах",
        type=discord.ActivityType.playing
    )
    await bot.change_presence(activity=activity)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"❌ Команда не найдена. Используйте `{PREFIX}info` для списка команд")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ У вас недостаточно прав для выполнения этой команды")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Неправильное использование команды. Используйте `{PREFIX}info` для помощи")
    else:
        await ctx.send(f"❌ Произошла ошибка: {str(error)}")

# Команды бота
@bot.command(name='info', help='Показать информацию о командах бота')
async def info(ctx):
    """Показать информацию о командах бота"""
    
    embed = discord.Embed(
        title="🏰 Instant Clans - Управление кланами",
        description="Бот для создания и управления кланами на вашем сервере Discord\n\n**Все команды начинаются с `*`**",
        color=discord.Color.purple()
    )
    
    embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else bot.user.default_avatar.url)
    
    # Основные команды
    embed.add_field(
        name="📋 **Основные команды**",
        value="```"
              f"{PREFIX}info - Эта информация о командах\n"
              f"{PREFIX}clan_create <название> @лидер - Создать новый клан (только админы)\n"
              f"{PREFIX}clan_join <название> - Вступить в клан\n"
              f"{PREFIX}clan_leave - Покинуть клан\n"
              f"{PREFIX}clan_info [название] - Информация о клане\n"
              f"{PREFIX}clan_list - Список всех кланов\n"
              f"{PREFIX}clan_members <название> - Участники клана\n"
              "```",
        inline=False
    )
    
    # Команды для лидеров
    embed.add_field(
        name="👑 **Команды для лидеров кланов**",
        value="```"
              f"{PREFIX}clan_kick @участник - Исключить участника из клана\n"
              f"{PREFIX}clan_transfer @новый_лидер - Передать лидерство\n"
              f"{PREFIX}clan_description <текст> - Изменить описание клана\n"
              "```",
        inline=False
    )
    
    # Административные команды
    embed.add_field(
        name="⚙️ **Административные команды**",
        value="```"
              f"{PREFIX}clan_delete <название> - Удалить клан\n"
              f"{PREFIX}clan_stats <название> <победы/поражения> - Обновить статистику\n"
              f"{PREFIX}clan_settings - Настройки системы кланов\n"
              "```",
        inline=False
    )
    
    # Статистические команды
    embed.add_field(
        name="📊 **Статистика**",
        value="```"
              f"{PREFIX}top_clans - Топ кланов по рейтингу\n"
              f"{PREFIX}top_players - Топ игроков\n"
              "```",
        inline=False
    )
    
    embed.set_footer(text=f"Версия 1.0 | Всего команд: {len(bot.commands)}")
    
    await ctx.send(embed=embed)

@bot.command(name='clan_create', help='Создать новый клан')
@commands.has_permissions(administrator=True)
async def clan_create(ctx, clan_name: str, leader: discord.Member):
    """Создание нового клана"""
    guild_data = get_clan_data(ctx.guild.id)
    
    # Проверка максимального количества кланов
    if len(guild_data['clans']) >= guild_data['config']['max_clans']:
        await ctx.send(f"❌ Достигнуто максимальное количество кланов ({guild_data['config']['max_clans']})")
        return
    
    # Проверка существования клана с таким именем
    if clan_name in guild_data['clans']:
        await ctx.send(f"❌ Клан с именем '{clan_name}' уже существует")
        return
    
    # Проверка, что лидер уже не состоит в другом клане
    for clan_info in guild_data['clans'].values():
        if leader.id in clan_info['members']:
            await ctx.send(f"❌ {leader.mention} уже состоит в клане '{clan_info['name']}'")
            return
    
    try:
        # Создаем ресурсы для клана
        clan_role, category, general_channel, voice_channel = await create_clan_resources(ctx.guild, clan_name)
        
        # Создаем структуру данных клана
        guild_data['clans'][clan_name] = {
            'name': clan_name,
            'leader_id': leader.id,
            'members': [leader.id],
            'created_at': datetime.now().isoformat(),
            'description': f"Добро пожаловать в клан {clan_name}!",
            'role_id': clan_role.id,
            'category_id': category.id,
            'channels': {
                'general': general_channel.id,
                'voice': voice_channel.id
            },
            'stats': {
                'wins': 0,
                'losses': 0,
                'rating': 1000,
                'total_matches': 0
            }
        }
        
        # Даем лидеру роль клана
        await leader.add_roles(clan_role)
        
        # Сохраняем данные
        save_guild_clan_data(ctx.guild.id, guild_data)
        
        embed = discord.Embed(
            title="✅ Клан создан!",
            description=f"Клан **{clan_name}** успешно создан",
            color=discord.Color.green()
        )
        embed.add_field(name="Лидер", value=leader.mention, inline=True)
        embed.add_field(name="Участников", value="1", inline=True)
        embed.add_field(name="Категория", value=category.name, inline=False)
        embed.add_field(name="Текстовый канал", value=general_channel.mention, inline=True)
        embed.add_field(name="Голосовой канал", value=voice_channel.mention, inline=True)
        embed.set_footer(text=f"Создано {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        await ctx.send(embed=embed)
        
        # Отправляем приветствие в канал клана
        welcome_embed = discord.Embed(
            title=f"Добро пожаловать в клан {clan_name}!",
            description=f"Лидер: {leader.mention}\n\nИспользуйте команды:\n`*clan_info` - информация о клане\n`*clan_members {clan_name}` - список участников",
            color=discord.Color.gold()
        )
        await general_channel.send(embed=welcome_embed)
        
    except Exception as e:
        await ctx.send(f"❌ Произошла ошибка при создании клана: {str(e)}")

@bot.command(name='clan_join', help='Вступить в клан')
async def clan_join(ctx, clan_name: str):
    """Вступление в клан"""
    guild_data = get_clan_data(ctx.guild.id)
    
    if clan_name not in guild_data['clans']:
        await ctx.send(f"❌ Клан '{clan_name}' не найден")
        return
    
    clan_info = guild_data['clans'][clan_name]
    
    # Проверка максимального количества участников
    if len(clan_info['members']) >= guild_data['config']['max_members_per_clan']:
        await ctx.send(f"❌ Клан '{clan_name}' уже заполнен")
        return
    
    # Проверка, что пользователь уже не состоит в клане
    if ctx.author.id in clan_info['members']:
        await ctx.send(f"❌ Вы уже состоите в клане '{clan_name}'")
        return
    
    # Проверка, что пользователь не состоит в другом клане
    for other_clan_name, other_clan_info in guild_data['clans'].items():
        if other_clan_name != clan_name and ctx.author.id in other_clan_info['members']:
            await ctx.send(f"❌ Вы уже состоите в клане '{other_clan_name}'")
            return
    
    # Добавляем пользователя в клан
    clan_info['members'].append(ctx.author.id)
    
    # Даем пользователю роль клана
    clan_role = ctx.guild.get_role(clan_info['role_id'])
    if clan_role:
        await ctx.author.add_roles(clan_role)
    
    save_guild_clan_data(ctx.guild.id, guild_data)
    
    embed = discord.Embed(
        title="✅ Успешное вступление!",
        description=f"{ctx.author.mention} вступил в клан **{clan_name}**",
        color=discord.Color.green()
    )
    embed.add_field(name="Теперь участников", value=str(len(clan_info['members'])), inline=True)
    embed.add_field(name="Лидер", value=f"<@{clan_info['leader_id']}>", inline=True)
    
    await ctx.send(embed=embed)

@bot.command(name='clan_leave', help='Покинуть клан')
async def clan_leave(ctx):
    """Выход из клана"""
    guild_data = get_clan_data(ctx.guild.id)
    
    # Поиск клана пользователя
    user_clan = None
    for clan_name, clan_info in guild_data['clans'].items():
        if ctx.author.id in clan_info['members']:
            user_clan = (clan_name, clan_info)
            break
    
    if not user_clan:
        await ctx.send("❌ Вы не состоите ни в одном клане")
        return
    
    clan_name, clan_info = user_clan
    
    # Проверка, что пользователь не лидер
    if ctx.author.id == clan_info['leader_id']:
        await ctx.send("❌ Лидер не может покинуть клан. Используйте `*clan_transfer` чтобы передать лидерство")
        return
    
    # Удаляем пользователя из клана
    clan_info['members'].remove(ctx.author.id)
    
    # Убираем роль клана
    clan_role = ctx.guild.get_role(clan_info['role_id'])
    if clan_role:
        await ctx.author.remove_roles(clan_role)
    
    save_guild_clan_data(ctx.guild.id, guild_data)
    
    await ctx.send(f"✅ Вы успешно покинули клан **{clan_name}**")

@bot.command(name='clan_info', help='Информация о клане')
async def clan_info(ctx, clan_name: str = None):
    """Получение информации о клане"""
    guild_data = get_clan_data(ctx.guild.id)
    
    # Если клан не указан, показываем клан пользователя
    if clan_name is None:
        for name, clan_info in guild_data['clans'].items():
            if ctx.author.id in clan_info['members']:
                clan_name = name
                break
    
    if not clan_name or clan_name not in guild_data['clans']:
        await ctx.send("❌ Клан не найден. Укажите название клана или вступите в клан")
        return
    
    clan_info = guild_data['clans'][clan_name]
    
    # Получаем список участников
    members_list = []
    for member_id in clan_info['members']:
        member = ctx.guild.get_member(member_id)
        if member:
            prefix = "👑 " if member_id == clan_info['leader_id'] else "👤 "
            members_list.append(f"{prefix}{member.mention}")
    
    # Формируем строку с участниками
    members_text = "\n".join(members_list[:10])
    if len(members_list) > 10:
        members_text += f"\n...и ещё {len(members_list) - 10} участников"
    
    # Статистика
    stats = clan_info['stats']
    winrate = stats['wins'] / (stats['wins'] + stats['losses']) * 100 if (stats['wins'] + stats['losses']) > 0 else 0
    
    embed = discord.Embed(
        title=f"🏰 Клан: {clan_name}",
        description=clan_info.get('description', 'Описание отсутствует'),
        color=discord.Color.blue()
    )
    
    # Информация о лидере
    leader = ctx.guild.get_member(clan_info['leader_id'])
    leader_name = leader.mention if leader else "Не найден"
    
    # Дата создания
    created_date = datetime.fromisoformat(clan_info['created_at']).strftime('%d.%m.%Y')
    
    embed.add_field(name="👑 Лидер", value=leader_name, inline=True)
    embed.add_field(name="📅 Создан", value=created_date, inline=True)
    embed.add_field(name="👥 Участников", value=str(len(clan_info['members'])), inline=True)
    embed.add_field(name="🏆 Победы", value=str(stats['wins']), inline=True)
    embed.add_field(name="💀 Поражения", value=str(stats['losses']), inline=True)
    embed.add_field(name="📈 Рейтинг", value=str(stats['rating']), inline=True)
    embed.add_field(name="📊 Винрейт", value=f"{winrate:.1f}%", inline=True)
    embed.add_field(name="👥 Участники", value=members_text, inline=False)
    
    embed.set_footer(text=f"Используйте *clan_members {clan_name} для полного списка")
    
    await ctx.send(embed=embed)

@bot.command(name='clan_list', help='Список всех кланов')
async def clan_list(ctx):
    """Показать список всех кланов на сервере"""
    guild_data = get_clan_data(ctx.guild.id)
    
    if not guild_data['clans']:
        await ctx.send("📭 На сервере ещё нет кланов. Используйте `*clan_create` чтобы создать первый клан")
        return
    
    embed = discord.Embed(
        title="📋 Список кланов на сервере",
        description=f"Всего кланов: {len(guild_data['clans'])}",
        color=discord.Color.gold()
    )
    
    for clan_name, clan_info in guild_data['clans'].items():
        leader = ctx.guild.get_member(clan_info['leader_id'])
        leader_name = leader.mention if leader else "Не найден"
        
        stats = clan_info['stats']
        total_matches = stats['wins'] + stats['losses']
        winrate = stats['wins'] / total_matches * 100 if total_matches > 0 else 0
        
        embed.add_field(
            name=f"🏰 {clan_name}",
            value=f"Лидер: {leader_name}\n"
                  f"Участников: {len(clan_info['members'])}\n"
                  f"Рейтинг: {stats['rating']} ({winrate:.1f}% винрейт)\n"
                  f"Используйте `*clan_join {clan_name}` чтобы вступить",
            inline=True
        )
    
    await ctx.send(embed=embed)

@bot.command(name='clan_members', help='Показать участников клана')
async def clan_members(ctx, clan_name: str):
    """Показать всех участников клана"""
    guild_data = get_clan_data(ctx.guild.id)
    
    if clan_name not in guild_data['clans']:
        await ctx.send(f"❌ Клан '{clan_name}' не найден")
        return
    
    clan_info = guild_data['clans'][clan_name]
    
    # Получаем список участников
    members_list = []
    leader_id = clan_info['leader_id']
    
    for member_id in clan_info['members']:
        member = ctx.guild.get_member(member_id)
        if member:
            role = "👑 Лидер" if member_id == leader_id else "👤 Участник"
            join_date = member.joined_at.strftime('%d.%m.%Y') if member.joined_at else "Неизвестно"
            members_list.append(f"{role} | {member.mention} | Вступил: {join_date}")
    
    embed = discord.Embed(
        title=f"👥 Участники клана {clan_name}",
        description=f"Всего участников: {len(members_list)}",
        color=discord.Color.blue()
    )
    
    # Разбиваем список на части по 10 человек
    for i in range(0, len(members_list), 10):
        chunk = members_list[i:i+10]
        embed.add_field(
            name=f"Участники {i+1}-{min(i+10, len(members_list))}",
            value="\n".join(chunk),
            inline=False
        )
    
    await ctx.send(embed=embed)

@bot.command(name='clan_kick', help='Исключить участника из клана')
async def clan_kick(ctx, member: discord.Member):
    """Исключение участника из клана"""
    guild_data = get_clan_data(ctx.guild.id)
    
    # Поиск клана автора команды
    author_clan = None
    for clan_name, clan_info in guild_data['clans'].items():
        if ctx.author.id in clan_info['members'] and ctx.author.id == clan_info['leader_id']:
            author_clan = (clan_name, clan_info)
            break
    
    if not author_clan:
        await ctx.send("❌ Вы не являетесь лидером клана")
        return
    
    clan_name, clan_info = author_clan
    
    # Проверка, что участник состоит в клане
    if member.id not in clan_info['members']:
        await ctx.send(f"❌ {member.mention} не состоит в вашем клане")
        return
    
    # Проверка, что лидер не пытается исключить себя
    if member.id == ctx.author.id:
        await ctx.send("❌ Вы не можете исключить себя из клана")
        return
    
    # Исключаем участника
    clan_info['members'].remove(member.id)
    
    # Убираем роль клана
    clan_role = ctx.guild.get_role(clan_info['role_id'])
    if clan_role:
        await member.remove_roles(clan_role)
    
    save_guild_clan_data(ctx.guild.id, guild_data)
    
    await ctx.send(f"✅ {member.mention} был исключен из клана **{clan_name}**")

@bot.command(name='clan_transfer', help='Передать лидерство')
async def clan_transfer(ctx, new_leader: discord.Member):
    """Передача лидерства клана"""
    guild_data = get_clan_data(ctx.guild.id)
    
    # Поиск клана автора команды
    author_clan = None
    for clan_name, clan_info in guild_data['clans'].items():
        if ctx.author.id in clan_info['members'] and ctx.author.id == clan_info['leader_id']:
            author_clan = (clan_name, clan_info)
            break
    
    if not author_clan:
        await ctx.send("❌ Вы не являетесь лидером клана")
        return
    
    clan_name, clan_info = author_clan
    
    # Проверка, что новый лидер состоит в клане
    if new_leader.id not in clan_info['members']:
        await ctx.send(f"❌ {new_leader.mention} не состоит в вашем клане")
        return
    
    # Передаем лидерство
    clan_info['leader_id'] = new_leader.id
    save_guild_clan_data(ctx.guild.id, guild_data)
    
    await ctx.send(f"✅ Лидерство клана **{clan_name}** передано {new_leader.mention}")

@bot.command(name='clan_description', help='Изменить описание клана')
async def clan_description(ctx, *, description: str):
    """Изменение описания клана"""
    guild_data = get_clan_data(ctx.guild.id)
    
    # Поиск клана автора команды
    author_clan = None
    for clan_name, clan_info in guild_data['clans'].items():
        if ctx.author.id in clan_info['members'] and ctx.author.id == clan_info['leader_id']:
            author_clan = (clan_name, clan_info)
            break
    
    if not author_clan:
        await ctx.send("❌ Вы не являетесь лидером клана")
        return
    
    clan_name, clan_info = author_clan
    
    # Обновляем описание
    clan_info['description'] = description
    save_guild_clan_data(ctx.guild.id, guild_data)
    
    await ctx.send(f"✅ Описание клана **{clan_name}** обновлено")

@bot.command(name='clan_delete', help='Удалить клан')
@commands.has_permissions(administrator=True)
async def clan_delete(ctx, clan_name: str):
    """Удаление клана"""
    guild_data = get_clan_data(ctx.guild.id)
    
    if clan_name not in guild_data['clans']:
        await ctx.send(f"❌ Клан '{clan_name}' не найден")
        return
    
    clan_info = guild_data['clans'][clan_name]
    
    # Удаляем ресурсы клана
    try:
        # Удаляем роль
        clan_role = ctx.guild.get_role(clan_info['role_id'])
        if clan_role:
            await clan_role.delete()
        
        # Удаляем категорию (автоматически удалятся все каналы)
        category = ctx.guild.get_channel(clan_info['category_id'])
        if category:
            await category.delete()
    except:
        pass
    
    # Удаляем клан из данных
    del guild_data['clans'][clan_name]
    save_guild_clan_data(ctx.guild.id, guild_data)
    
    await ctx.send(f"✅ Клан **{clan_name}** успешно удален")

@bot.command(name='clan_stats', help='Обновить статистику клана')
@commands.has_permissions(administrator=True)
async def clan_stats(ctx, clan_name: str, wins: int = 0, losses: int = 0):
    """Обновление статистики клана"""
    guild_data = get_clan_data(ctx.guild.id)
    
    if clan_name not in guild_data['clans']:
        await ctx.send(f"❌ Клан '{clan_name}' не найден")
        return
    
    clan_info = guild_data['clans'][clan_name]
    
    # Обновляем статистику
    clan_info['stats']['wins'] += wins
    clan_info['stats']['losses'] += losses
    clan_info['stats']['total_matches'] = clan_info['stats']['wins'] + clan_info['stats']['losses']
    
    # Рассчитываем рейтинг (простая формула)
    winrate = clan_info['stats']['wins'] / clan_info['stats']['total_matches'] if clan_info['stats']['total_matches'] > 0 else 0
    clan_info['stats']['rating'] = 1000 + (winrate * 200)
    
    save_guild_clan_data(ctx.guild.id, guild_data)
    
    embed = discord.Embed(
        title="📊 Статистика обновлена",
        description=f"Статистика клана **{clan_name}** успешно обновлена",
        color=discord.Color.green()
    )
    embed.add_field(name="Победы", value=f"+{wins} → {clan_info['stats']['wins']}", inline=True)
    embed.add_field(name="Поражения", value=f"+{losses} → {clan_info['stats']['losses']}", inline=True)
    embed.add_field(name="Всего матчей", value=str(clan_info['stats']['total_matches']), inline=True)
    embed.add_field(name="Винрейт", value=f"{winrate*100:.1f}%", inline=True)
    embed.add_field(name="Новый рейтинг", value=f"{clan_info['stats']['rating']:.0f}", inline=True)
    
    await ctx.send(embed=embed)

@bot.command(name='top_clans', help='Топ кланов по рейтингу')
async def top_clans(ctx):
    """Показать топ кланов по рейтингу"""
    guild_data = get_clan_data(ctx.guild.id)
    
    if not guild_data['clans']:
        await ctx.send("📭 На сервере ещё нет кланов")
        return
    
    # Сортируем кланы по рейтингу
    sorted_clans = sorted(
        guild_data['clans'].items(),
        key=lambda x: x[1]['stats']['rating'],
        reverse=True
    )
    
    embed = discord.Embed(
        title="🏆 Топ кланов по рейтингу",
        description="Список самых сильных кланов на сервере",
        color=discord.Color.gold()
    )
    
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    
    for i, (clan_name, clan_info) in enumerate(sorted_clans[:10]):
        medal = medals[i] if i < len(medals) else f"{i+1}."
        stats = clan_info['stats']
        winrate = stats['wins'] / (stats['wins'] + stats['losses']) * 100 if (stats['wins'] + stats['losses']) > 0 else 0
        
        embed.add_field(
            name=f"{medal} {clan_name}",
            value=f"Рейтинг: {stats['rating']:.0f}\n"
                  f"Винрейт: {winrate:.1f}%\n"
                  f"Участников: {len(clan_info['members'])}",
            inline=True
        )
    
    await ctx.send(embed=embed)

@bot.command(name='ping', help='Проверить пинг бота')
async def ping(ctx):
    """Проверка пинга бота"""
    latency = round(bot.latency * 1000)
    
    embed = discord.Embed(
        title="🏓 Понг!",
        description=f"Задержка бота: **{latency}мс**",
        color=discord.Color.green() if latency < 100 else discord.Color.orange()
    )
    
    if latency < 100:
        status = "Отличное соединение ✅"
    elif latency < 200:
        status = "Хорошее соединение ⚡"
    elif latency < 300:
        status = "Среднее соединение ⚠️"
    else:
        status = "Медленное соединение 🐌"
    
    embed.add_field(name="Статус", value=status, inline=False)
    embed.set_footer(text="Instant Clans | Версия 1.0")
    
    await ctx.send(embed=embed)

# Запуск бота
if __name__ == "__main__":
    print("Запуск бота Instant Clans...")
    bot.run(TOKEN)