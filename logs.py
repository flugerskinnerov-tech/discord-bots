import discord
from discord.ext import commands
import json
import os
from datetime import datetime
import asyncio

# Настройки бота
TOKEN = 'MTQ3NTg3MzI0MDAzMDExODAwOA.GIuWs0.bxFe2SEVmx4LCNWodol25Aew7kHDG2pK5L_Yjg'
PREFIX = '+'  # Префикс изменен на +
DATA_FILE = 'logs_config.json'
BOT_ID = 1475873240030118008

# Намерения бота (нужно включить все для отслеживания)
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True
intents.guilds = True
intents.bans = True
intents.invites = True
intents.moderation = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

# Цвета для разных типов событий
COLORS = {
    'join': discord.Color.green(),
    'leave': discord.Color.orange(),
    'ban': discord.Color.red(),
    'unban': discord.Color.green(),
    'kick': discord.Color.red(),
    'message_delete': discord.Color.red(),
    'message_edit': discord.Color.blue(),
    'voice_join': discord.Color.green(),
    'voice_leave': discord.Color.orange(),
    'voice_move': discord.Color.blue(),
    'channel_create': discord.Color.green(),
    'channel_delete': discord.Color.red(),
    'channel_edit': discord.Color.blue(),
    'role_create': discord.Color.green(),
    'role_delete': discord.Color.red(),
    'role_edit': discord.Color.blue(),
    'member_update': discord.Color.purple(),
    'nickname_change': discord.Color.purple(),
    'bot_add': discord.Color.teal(),
    'bot_remove': discord.Color.orange(),
    'invite_create': discord.Color.green(),
    'invite_delete': discord.Color.orange(),
    'emoji_create': discord.Color.green(),
    'emoji_delete': discord.Color.orange(),
    'sticker_create': discord.Color.green(),
    'sticker_delete': discord.Color.orange()
}

# Эмодзи для разных типов событий
EMOJIS = {
    'join': '📥',
    'leave': '📤',
    'ban': '🔨',
    'unban': '🔓',
    'kick': '👢',
    'message_delete': '🗑️',
    'message_edit': '📝',
    'voice_join': '🔊',
    'voice_leave': '🔇',
    'voice_move': '🔄',
    'channel_create': '➕',
    'channel_delete': '➖',
    'channel_edit': '✏️',
    'role_create': '➕',
    'role_delete': '➖',
    'role_edit': '✏️',
    'member_update': '👤',
    'nickname_change': '📛',
    'bot_add': '🤖',
    'bot_remove': '🤖',
    'invite_create': '🔗',
    'invite_delete': '🔗',
    'emoji_create': '😀',
    'emoji_delete': '😀',
    'sticker_create': '🖼️',
    'sticker_delete': '🖼️'
}

# Загрузка конфигурации
def load_config():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

# Сохранение конфигурации
def save_config(config):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

# Получение канала логов для сервера
def get_log_channel(guild_id):
    config = load_config()
    return config.get(str(guild_id))

# Установка канала логов для сервера
def set_log_channel(guild_id, channel_id):
    config = load_config()
    config[str(guild_id)] = channel_id
    save_config(config)

# Удаление канала логов для сервера
def remove_log_channel(guild_id):
    config = load_config()
    if str(guild_id) in config:
        del config[str(guild_id)]
        save_config(config)

# Форматирование времени
def format_time():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Создание embed для логов
async def send_log(guild, embed, event_type=None):
    if not guild:
        return
    
    log_channel_id = get_log_channel(guild.id)
    if not log_channel_id:
        return
    
    log_channel = guild.get_channel(log_channel_id)
    if not log_channel:
        return
    
    # Добавляем эмодзи если есть
    if event_type and event_type in EMOJIS:
        embed.title = f"{EMOJIS[event_type]} {embed.title}"
    
    # Добавляем время
    embed.set_footer(text=f"Время: {format_time()}")
    
    try:
        await log_channel.send(embed=embed)
    except:
        pass

# События бота
@bot.event
async def on_ready():
    print(f'============================================')
    print(f'Бот Logging Bot успешно запущен!')
    print(f'Имя: {bot.user.name}')
    print(f'ID: {bot.user.id}')
    print(f'Префикс команд: {PREFIX}')
    print(f'Количество серверов: {len(bot.guilds)}')
    print(f'============================================')
    
    # Проверяем ID бота
    if bot.user.id != BOT_ID:
        print(f'⚠️  Внимание: ID бота ({bot.user.id}) не совпадает с указанным в настройках ({BOT_ID})')
    
    activity = discord.Activity(
        name=f"{PREFIX}log-setup | Логирование",
        type=discord.ActivityType.watching
    )
    await bot.change_presence(activity=activity)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"❌ Команда не найдена. Используйте `{PREFIX}help`")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ У вас недостаточно прав для этой команды")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Неправильные аргументы. Используйте `{PREFIX}help`")
    else:
        await ctx.send(f"❌ Ошибка: {str(error)}")

# Команды бота
@bot.command(name='help')
async def help_command(ctx):
    """Показать список команд"""
    
    embed = discord.Embed(
        title="📋 Команды Logging Bot",
        description=f"Бот для логирования событий на сервере\n**Префикс команд: `{PREFIX}`**",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="⚙️ **Настройка логов**",
        value=(
            f"`{PREFIX}log-setup #канал` - установить канал для логов\n"
            f"`{PREFIX}log-remove` - удалить канал логов\n"
            f"`{PREFIX}log-status` - проверить статус логов\n"
            f"`{PREFIX}log-test` - отправить тестовый лог"
        ),
        inline=False
    )
    
    embed.add_field(
        name="📊 **Типы логируемых событий**",
        value=(
            "**Участники:**\n"
            "📥 Присоединение | 📤 Выход | 🔨 Бан | 🔓 Разбан | 👢 Кик\n"
            "📛 Смена ника | 👤 Обновление профиля\n\n"
            "**Голосовые каналы:**\n"
            "🔊 Вход в канал | 🔇 Выход | 🔄 Перемещение\n\n"
            "**Сообщения:**\n"
            "🗑️ Удаление | 📝 Редактирование\n\n"
            "**Каналы и роли:**\n"
            "➕ Создание | ➖ Удаление | ✏️ Изменение\n\n"
            "**Другое:**\n"
            "🤖 Добавление/удаление ботов | 🔗 Приглашения | 😀 Эмодзи"
        ),
        inline=False
    )
    
    embed.add_field(
        name="ℹ️ **Информация**",
        value=(
            f"`{PREFIX}stats` - статистика бота\n"
            f"`{PREFIX}ping` - пинг бота\n"
            f"`{PREFIX}info` - информация о боте"
        ),
        inline=False
    )
    
    embed.set_footer(text=f"ID бота: {BOT_ID}")
    
    await ctx.send(embed=embed)

@bot.command(name='info')
async def info_command(ctx):
    """Информация о боте"""
    
    embed = discord.Embed(
        title="ℹ️ Информация о боте",
        description="Бот для логирования событий на Discord сервере",
        color=discord.Color.blue()
    )
    
    if bot.user.avatar:
        embed.set_thumbnail(url=bot.user.avatar.url)
    
    embed.add_field(name="📛 Имя", value=bot.user.name, inline=True)
    embed.add_field(name="🆔 ID", value=str(BOT_ID), inline=True)
    embed.add_field(name="🔧 Префикс", value=PREFIX, inline=True)
    embed.add_field(name="📊 Серверов", value=str(len(bot.guilds)), inline=True)
    embed.add_field(name="📅 Создан", value=bot.user.created_at.strftime('%d.%m.%Y'), inline=True)
    embed.add_field(name="📈 Пинг", value=f"{round(bot.latency * 1000)}мс", inline=True)
    
    embed.add_field(
        name="📋 Возможности",
        value=(
            "• Логирование всех событий\n"
            "• Настраиваемый канал логов\n"
            "• Красивые embed сообщения\n"
            "• Детальная информация о событиях"
        ),
        inline=False
    )
    
    await ctx.send(embed=embed)

@bot.command(name='log-setup')
@commands.has_permissions(administrator=True)
async def log_setup(ctx, channel: discord.TextChannel = None):
    """Установить канал для логов"""
    
    if not channel:
        channel = ctx.channel
    
    set_log_channel(ctx.guild.id, channel.id)
    
    embed = discord.Embed(
        title="✅ Канал логов установлен",
        description=f"Логи будут отправляться в {channel.mention}",
        color=discord.Color.green()
    )
    embed.add_field(name="👑 Администратор", value=ctx.author.mention, inline=True)
    embed.add_field(name="📊 Типов событий", value="Более 20", inline=True)
    
    await ctx.send(embed=embed)

@bot.command(name='log-remove')
@commands.has_permissions(administrator=True)
async def log_remove(ctx):
    """Удалить канал логов"""
    
    remove_log_channel(ctx.guild.id)
    
    embed = discord.Embed(
        title="✅ Канал логов удален",
        description="Логи больше не будут отправляться",
        color=discord.Color.orange()
    )
    embed.add_field(name="👑 Администратор", value=ctx.author.mention, inline=True)
    
    await ctx.send(embed=embed)

@bot.command(name='log-status')
async def log_status(ctx):
    """Проверить статус логов"""
    
    log_channel_id = get_log_channel(ctx.guild.id)
    
    embed = discord.Embed(
        title="📊 Статус логов",
        color=discord.Color.blue()
    )
    
    if log_channel_id:
        channel = ctx.guild.get_channel(log_channel_id)
        if channel:
            embed.add_field(
                name="✅ Логи активны",
                value=f"Канал логов: {channel.mention}",
                inline=False
            )
        else:
            embed.add_field(
                name="⚠️ Канал не найден",
                value="Канал логов был удален. Используйте `+log-setup` чтобы установить новый канал",
                inline=False
            )
    else:
        embed.add_field(
            name="❌ Логи не настроены",
            value=f"Используйте `{PREFIX}log-setup #канал` чтобы настроить логи",
            inline=False
        )
    
    await ctx.send(embed=embed)

@bot.command(name='log-test')
@commands.has_permissions(administrator=True)
async def log_test(ctx):
    """Отправить тестовый лог"""
    
    embed = discord.Embed(
        title="🧪 Тестовый лог",
        description="Это тестовое сообщение для проверки работы логов",
        color=discord.Color.gold()
    )
    embed.add_field(name="👑 Тест", value=ctx.author.mention, inline=True)
    embed.add_field(name="📊 Статус", value="✅ Работает", inline=True)
    
    await send_log(ctx.guild, embed)
    await ctx.send("✅ Тестовый лог отправлен!")

@bot.command(name='stats')
async def stats_command(ctx):
    """Статистика бота"""
    
    log_channel_id = get_log_channel(ctx.guild.id)
    log_status = "✅ Активен" if log_channel_id else "❌ Не настроен"
    
    embed = discord.Embed(
        title="📊 Статистика",
        color=discord.Color.blue()
    )
    
    embed.add_field(name="👥 Участников", value=str(ctx.guild.member_count), inline=True)
    embed.add_field(name="💬 Каналов", value=str(len(ctx.guild.channels)), inline=True)
    embed.add_field(name="🎭 Ролей", value=str(len(ctx.guild.roles)), inline=True)
    embed.add_field(name="📊 Логи", value=log_status, inline=True)
    embed.add_field(name="🤖 Ботов", value=str(len([m for m in ctx.guild.members if m.bot])), inline=True)
    embed.add_field(name="📅 Создан", value=ctx.guild.created_at.strftime('%d.%m.%Y'), inline=True)
    
    await ctx.send(embed=embed)

@bot.command(name='ping')
async def ping_command(ctx):
    """Проверить пинг бота"""
    
    latency = round(bot.latency * 1000)
    
    embed = discord.Embed(
        title="🏓 Понг!",
        description=f"Задержка бота: **{latency}мс**",
        color=discord.Color.green() if latency < 100 else discord.Color.orange()
    )
    
    await ctx.send(embed=embed)

# ==================== СОБЫТИЯ УЧАСТНИКОВ ====================

@bot.event
async def on_member_join(member):
    """Логирование входа участника"""
    
    embed = discord.Embed(
        title="Участник присоединился",
        description=f"{member.mention} **{member.name}**#{member.discriminator}",
        color=COLORS['join']
    )
    
    embed.add_field(name="🆔 ID", value=member.id, inline=True)
    embed.add_field(name="📅 Аккаунт создан", value=member.created_at.strftime('%d.%m.%Y %H:%M'), inline=True)
    embed.add_field(name="👥 Всего участников", value=str(len(member.guild.members)), inline=True)
    
    await send_log(member.guild, embed, 'join')

@bot.event
async def on_member_remove(member):
    """Логирование выхода участника"""
    
    embed = discord.Embed(
        title="Участник покинул сервер",
        description=f"{member.mention} **{member.name}**#{member.discriminator}",
        color=COLORS['leave']
    )
    
    embed.add_field(name="🆔 ID", value=member.id, inline=True)
    embed.add_field(name="📅 Присоединился", value=member.joined_at.strftime('%d.%m.%Y %H:%M') if member.joined_at else "Неизвестно", inline=True)
    embed.add_field(name="👥 Осталось участников", value=str(len(member.guild.members)), inline=True)
    
    await send_log(member.guild, embed, 'leave')

@bot.event
async def on_member_ban(guild, user):
    """Логирование бана"""
    
    embed = discord.Embed(
        title="Участник забанен",
        description=f"{user.mention if isinstance(user, discord.Member) else user.name}",
        color=COLORS['ban']
    )
    
    embed.add_field(name="🆔 ID", value=user.id, inline=True)
    embed.add_field(name="👮 Модератор", value="Неизвестно", inline=True)
    
    # Пытаемся получить информацию о бане
    try:
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.ban):
            if entry.target.id == user.id:
                embed.set_field_at(1, name="👮 Модератор", value=entry.user.mention, inline=True)
                if entry.reason:
                    embed.add_field(name="📝 Причина", value=entry.reason, inline=False)
                break
    except:
        pass
    
    await send_log(guild, embed, 'ban')

@bot.event
async def on_member_unban(guild, user):
    """Логирование разбана"""
    
    embed = discord.Embed(
        title="Участник разбанен",
        description=f"{user.name}#{user.discriminator}",
        color=COLORS['unban']
    )
    
    embed.add_field(name="🆔 ID", value=user.id, inline=True)
    
    # Пытаемся получить информацию о разбане
    try:
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.unban):
            if entry.target.id == user.id:
                embed.add_field(name="👮 Модератор", value=entry.user.mention, inline=True)
                break
    except:
        pass
    
    await send_log(guild, embed, 'unban')

@bot.event
async def on_member_update(before, after):
    """Логирование обновления участника"""
    
    guild = after.guild
    
    # Проверка смены ника
    if before.nick != after.nick:
        embed = discord.Embed(
            title="Смена ника",
            description=after.mention,
            color=COLORS['nickname_change']
        )
        
        embed.add_field(name="👤 Старый ник", value=before.nick or before.name, inline=True)
        embed.add_field(name="👤 Новый ник", value=after.nick or after.name, inline=True)
        embed.add_field(name="🆔 ID", value=after.id, inline=True)
        
        await send_log(guild, embed, 'nickname_change')
    
    # Проверка смены ролей
    elif before.roles != after.roles:
        added_roles = [role for role in after.roles if role not in before.roles]
        removed_roles = [role for role in before.roles if role not in after.roles]
        
        if added_roles:
            embed = discord.Embed(
                title="Добавлены роли",
                description=after.mention,
                color=COLORS['member_update']
            )
            
            embed.add_field(name="📥 Добавленные роли", value=", ".join([role.mention for role in added_roles]), inline=False)
            embed.add_field(name="🆔 ID", value=after.id, inline=True)
            
            await send_log(guild, embed, 'member_update')
        
        if removed_roles:
            embed = discord.Embed(
                title="Удалены роли",
                description=after.mention,
                color=COLORS['member_update']
            )
            
            embed.add_field(name="📤 Удаленные роли", value=", ".join([role.mention for role in removed_roles]), inline=False)
            embed.add_field(name="🆔 ID", value=after.id, inline=True)
            
            await send_log(guild, embed, 'member_update')

# ==================== СОБЫТИЯ ГОЛОСОВЫХ КАНАЛОВ ====================

@bot.event
async def on_voice_state_update(member, before, after):
    """Логирование изменений в голосовых каналах"""
    
    guild = member.guild
    
    # Вход в голосовой канал
    if before.channel is None and after.channel is not None:
        embed = discord.Embed(
            title="Вход в голосовой канал",
            description=f"{member.mention} зашел в {after.channel.mention}",
            color=COLORS['voice_join']
        )
        
        embed.add_field(name="👤 Участник", value=member.mention, inline=True)
        embed.add_field(name="🔊 Канал", value=after.channel.name, inline=True)
        embed.add_field(name="👥 В канале", value=str(len(after.channel.members)), inline=True)
        
        await send_log(guild, embed, 'voice_join')
    
    # Выход из голосового канала
    elif before.channel is not None and after.channel is None:
        embed = discord.Embed(
            title="Выход из голосового канала",
            description=f"{member.mention} вышел из {before.channel.mention}",
            color=COLORS['voice_leave']
        )
        
        embed.add_field(name="👤 Участник", value=member.mention, inline=True)
        embed.add_field(name="🔊 Канал", value=before.channel.name, inline=True)
        embed.add_field(name="⏱️ Время в канале", value="Неизвестно", inline=True)
        
        await send_log(guild, embed, 'voice_leave')
    
    # Перемещение между каналами
    elif before.channel is not None and after.channel is not None and before.channel != after.channel:
        embed = discord.Embed(
            title="Перемещение в голосовом канале",
            description=f"{member.mention} переместился",
            color=COLORS['voice_move']
        )
        
        embed.add_field(name="👤 Участник", value=member.mention, inline=True)
        embed.add_field(name="📤 Из канала", value=before.channel.name, inline=True)
        embed.add_field(name="📥 В канал", value=after.channel.name, inline=True)
        
        await send_log(guild, embed, 'voice_move')

# ==================== СОБЫТИЯ СООБЩЕНИЙ ====================

@bot.event
async def on_message_delete(message):
    """Логирование удаления сообщения"""
    
    if message.author.bot:
        return
    
    guild = message.guild
    if not guild:
        return
    
    embed = discord.Embed(
        title="Сообщение удалено",
        color=COLORS['message_delete']
    )
    
    embed.add_field(name="👤 Автор", value=message.author.mention, inline=True)
    embed.add_field(name="💬 Канал", value=message.channel.mention, inline=True)
    
    if message.content:
        content = message.content[:1000] + "..." if len(message.content) > 1000 else message.content
        embed.add_field(name="📝 Содержание", value=content, inline=False)
    else:
        embed.add_field(name="📝 Содержание", value="*Нет текста (возможно вложение)*", inline=False)
    
    await send_log(guild, embed, 'message_delete')

@bot.event
async def on_message_edit(before, after):
    """Логирование редактирования сообщения"""
    
    if before.author.bot:
        return
    
    if before.content == after.content:
        return
    
    guild = before.guild
    if not guild:
        return
    
    embed = discord.Embed(
        title="Сообщение отредактировано",
        color=COLORS['message_edit']
    )
    
    embed.add_field(name="👤 Автор", value=before.author.mention, inline=True)
    embed.add_field(name="💬 Канал", value=before.channel.mention, inline=True)
    embed.add_field(name="🔗 Ссылка", value=f"[Перейти]({after.jump_url})", inline=True)
    
    if before.content:
        old_content = before.content[:500] + "..." if len(before.content) > 500 else before.content
        embed.add_field(name="📝 До", value=old_content, inline=False)
    
    if after.content:
        new_content = after.content[:500] + "..." if len(after.content) > 500 else after.content
        embed.add_field(name="📝 После", value=new_content, inline=False)
    
    await send_log(guild, embed, 'message_edit')

# ==================== СОБЫТИЯ КАНАЛОВ ====================

@bot.event
async def on_guild_channel_create(channel):
    """Логирование создания канала"""
    
    embed = discord.Embed(
        title="Канал создан",
        description=f"Создан канал {channel.mention}",
        color=COLORS['channel_create']
    )
    
    embed.add_field(name="📛 Название", value=channel.name, inline=True)
    embed.add_field(name="🔧 Тип", value=str(channel.type).capitalize(), inline=True)
    embed.add_field(name="📁 Категория", value=channel.category.name if channel.category else "Нет", inline=True)
    
    # Пытаемся получить информацию о создателе
    try:
        async for entry in channel.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_create):
            if entry.target.id == channel.id:
                embed.add_field(name="👮 Создал", value=entry.user.mention, inline=True)
                break
    except:
        pass
    
    await send_log(channel.guild, embed, 'channel_create')

@bot.event
async def on_guild_channel_delete(channel):
    """Логирование удаления канала"""
    
    embed = discord.Embed(
        title="Канал удален",
        description=f"Удален канал **{channel.name}**",
        color=COLORS['channel_delete']
    )
    
    embed.add_field(name="📛 Название", value=channel.name, inline=True)
    embed.add_field(name="🔧 Тип", value=str(channel.type).capitalize(), inline=True)
    
    # Пытаемся получить информацию об удалившем
    try:
        async for entry in channel.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_delete):
            if entry.target.id == channel.id:
                embed.add_field(name="👮 Удалил", value=entry.user.mention, inline=True)
                break
    except:
        pass
    
    await send_log(channel.guild, embed, 'channel_delete')

@bot.event
async def on_guild_channel_update(before, after):
    """Логирование изменения канала"""
    
    if before.name != after.name:
        embed = discord.Embed(
            title="Канал переименован",
            description=f"Изменен канал {after.mention}",
            color=COLORS['channel_edit']
        )
        
        embed.add_field(name="📛 Старое название", value=before.name, inline=True)
        embed.add_field(name="📛 Новое название", value=after.name, inline=True)
        
        await send_log(after.guild, embed, 'channel_edit')

# ==================== СОБЫТИЯ РОЛЕЙ ====================

@bot.event
async def on_guild_role_create(role):
    """Логирование создания роли"""
    
    embed = discord.Embed(
        title="Роль создана",
        description=f"Создана роль {role.mention}",
        color=COLORS['role_create']
    )
    
    embed.add_field(name="📛 Название", value=role.name, inline=True)
    embed.add_field(name="🎨 Цвет", value=str(role.color) if role.color.value != 0 else "Нет", inline=True)
    embed.add_field(name="👥 Участников", value=str(len(role.members)), inline=True)
    
    # Пытаемся получить информацию о создателе
    try:
        async for entry in role.guild.audit_logs(limit=1, action=discord.AuditLogAction.role_create):
            if entry.target.id == role.id:
                embed.add_field(name="👮 Создал", value=entry.user.mention, inline=True)
                break
    except:
        pass
    
    await send_log(role.guild, embed, 'role_create')

@bot.event
async def on_guild_role_delete(role):
    """Логирование удаления роли"""
    
    embed = discord.Embed(
        title="Роль удалена",
        description=f"Удалена роль **{role.name}**",
        color=COLORS['role_delete']
    )
    
    embed.add_field(name="📛 Название", value=role.name, inline=True)
    embed.add_field(name="🎨 Цвет", value=str(role.color) if role.color.value != 0 else "Нет", inline=True)
    
    # Пытаемся получить информацию об удалившем
    try:
        async for entry in role.guild.audit_logs(limit=1, action=discord.AuditLogAction.role_delete):
            if entry.target.id == role.id:
                embed.add_field(name="👮 Удалил", value=entry.user.mention, inline=True)
                break
    except:
        pass
    
    await send_log(role.guild, embed, 'role_delete')

@bot.event
async def on_guild_role_update(before, after):
    """Логирование изменения роли"""
    
    if before.name != after.name:
        embed = discord.Embed(
            title="Роль переименована",
            description=f"Изменена роль {after.mention}",
            color=COLORS['role_edit']
        )
        
        embed.add_field(name="📛 Старое название", value=before.name, inline=True)
        embed.add_field(name="📛 Новое название", value=after.name, inline=True)
        
        await send_log(after.guild, embed, 'role_edit')
    
    elif before.color != after.color:
        embed = discord.Embed(
            title="Изменен цвет роли",
            description=f"Изменен цвет роли {after.mention}",
            color=after.color if after.color.value != 0 else discord.Color.default()
        )
        
        embed.add_field(name="🎨 Старый цвет", value=str(before.color) if before.color.value != 0 else "Нет", inline=True)
        embed.add_field(name="🎨 Новый цвет", value=str(after.color) if after.color.value != 0 else "Нет", inline=True)
        
        await send_log(after.guild, embed, 'role_edit')

# ==================== СОБЫТИЯ ПРИГЛАШЕНИЙ ====================

@bot.event
async def on_invite_create(invite):
    """Логирование создания приглашения"""
    
    embed = discord.Embed(
        title="Создано приглашение",
        description=f"Создано приглашение в канал {invite.channel.mention}",
        color=COLORS['invite_create']
    )
    
    embed.add_field(name="👮 Создатель", value=invite.inviter.mention if invite.inviter else "Неизвестно", inline=True)
    embed.add_field(name="🔗 Код", value=invite.code, inline=True)
    embed.add_field(name="⏱️ Истекает", value=invite.max_age_text if hasattr(invite, 'max_age_text') else "Никогда", inline=True)
    embed.add_field(name="👥 Макс. использований", value=str(invite.max_uses) if invite.max_uses else "∞", inline=True)
    
    await send_log(invite.guild, embed, 'invite_create')

@bot.event
async def on_invite_delete(invite):
    """Логирование удаления приглашения"""
    
    embed = discord.Embed(
        title="Приглашение удалено",
        description=f"Удалено приглашение в канал {invite.channel.mention}",
        color=COLORS['invite_delete']
    )
    
    embed.add_field(name="🔗 Код", value=invite.code, inline=True)
    embed.add_field(name="👮 Создатель", value=invite.inviter.mention if invite.inviter else "Неизвестно", inline=True)
    
    await send_log(invite.guild, embed, 'invite_delete')

# ==================== СОБЫТИЯ ЭМОДЗИ ====================

@bot.event
async def on_guild_emojis_update(guild, before, after):
    """Логирование изменений эмодзи"""
    
    # Добавлены эмодзи
    added_emojis = [emoji for emoji in after if emoji not in before]
    for emoji in added_emojis:
        embed = discord.Embed(
            title="Эмодзи добавлен",
            description=f"Добавлен эмодзи {emoji}",
            color=COLORS['emoji_create']
        )
        
        embed.add_field(name="📛 Название", value=emoji.name, inline=True)
        embed.add_field(name="🆔 ID", value=emoji.id, inline=True)
        embed.add_field(name="🔗 Строка", value=f"`{emoji}`", inline=True)
        
        await send_log(guild, embed, 'emoji_create')
    
    # Удалены эмодзи
    removed_emojis = [emoji for emoji in before if emoji not in after]
    for emoji in removed_emojis:
        embed = discord.Embed(
            title="Эмодзи удален",
            description=f"Удален эмодзи **{emoji.name}**",
            color=COLORS['emoji_delete']
        )
        
        embed.add_field(name="📛 Название", value=emoji.name, inline=True)
        
        await send_log(guild, embed, 'emoji_delete')

# ==================== ЗАПУСК БОТА ====================

if __name__ == "__main__":
    print(f"Запуск бота Logging Bot...")
    print(f"ID бота: {BOT_ID}")
    print(f"Префикс команд: {PREFIX}")
    
    # Создаем файл конфигурации если его нет
    if not os.path.exists(DATA_FILE):
        save_config({})
    
    bot.run(TOKEN)