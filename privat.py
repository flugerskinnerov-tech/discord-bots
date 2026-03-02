import discord
from discord.ext import commands
import json
import os
from datetime import datetime

# Настройки бота
TOKEN = 'MTQ2ODQ3OTI2Nzc2NjY2NTI1Ng.GFew_7.TzAoMHVYfqNoxpVUPgilbjbKSnbwcbt729t_vk'
PREFIX = '!'
DATA_FILE = 'channels.json'
BOT_ID = 1468479267766665256

# Намерения бота
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

# Загрузка данных
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

# Сохранение данных
def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Получение данных сервера
def get_guild_data(guild_id):
    data = load_data()
    if str(guild_id) not in data:
        data[str(guild_id)] = {
            'private_channels': {},
            'temp_channels': {},
            'config': {
                'max_channels': 50,
                'auto_delete_empty': True,
                'default_limit': 0,
                'category_name': '🔒 Приватные каналы'
            }
        }
        save_data(data)
    return data[str(guild_id)]

# Сохранение данных сервера
def save_guild_data(guild_id, guild_data):
    data = load_data()
    data[str(guild_id)] = guild_data
    save_data(data)

# События бота
@bot.event
async def on_ready():
    print(f'============================================')
    print(f'Бот Instant Private Channels успешно запущен!')
    print(f'Имя: {bot.user.name}')
    print(f'ID: {bot.user.id}')
    print(f'ID из настроек: {BOT_ID}')
    print(f'Префикс команд: {PREFIX}')
    print(f'Количество серверов: {len(bot.guilds)}')
    print(f'============================================')
    
    # Проверяем ID бота
    if bot.user.id != BOT_ID:
        print(f'⚠️  Внимание: ID бота ({bot.user.id}) не совпадает с указанным в настройках ({BOT_ID})')
    
    activity = discord.Activity(
        name=f"{PREFIX}info - список команд",
        type=discord.ActivityType.playing
    )
    await bot.change_presence(activity=activity)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"❌ Команда не найдена. Используйте `{PREFIX}info`")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Недостаточно прав")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Неправильные аргументы. Используйте `{PREFIX}info`")
    else:
        await ctx.send(f"❌ Ошибка: {str(error)}")

@bot.event
async def on_voice_state_update(member, before, after):
    guild_data = get_guild_data(member.guild.id)
    
    # Создание временного канала
    if after.channel and after.channel.name == "➕ Создать приватный":
        try:
            category = after.channel.category
            if not category:
                # Ищем или создаем категорию
                category_name = guild_data['config']['category_name']
                categories = member.guild.categories
                category = discord.utils.get(categories, name=category_name)
                if not category:
                    category = await member.guild.create_category(category_name)
            
            # Проверяем лимит каналов
            if len(guild_data['temp_channels']) >= guild_data['config']['max_channels']:
                await member.move_to(None)
                try:
                    await member.send(f"❌ Достигнут лимит приватных каналов ({guild_data['config']['max_channels']}). Попробуйте позже.")
                except:
                    pass
                return
            
            # Создаем приватный канал
            channel_name = f"🔒 {member.name}"
            overwrites = {
                member.guild.default_role: discord.PermissionOverwrite(connect=False, view_channel=True),
                member: discord.PermissionOverwrite(connect=True, manage_channels=True, view_channel=True)
            }
            
            new_channel = await category.create_voice_channel(
                name=channel_name,
                overwrites=overwrites,
                user_limit=guild_data['config']['default_limit']
            )
            
            # Сохраняем информацию о канале
            guild_data['temp_channels'][str(new_channel.id)] = {
                'owner_id': member.id,
                'created_at': datetime.now().isoformat(),
                'members': [member.id],
                'name': channel_name,
                'locked': False,
                'hidden': False,
                'limit': guild_data['config']['default_limit']
            }
            
            # Перемещаем пользователя в новый канал
            await member.move_to(new_channel)
            
            save_guild_data(member.guild.id, guild_data)
            
            # Отправляем настройки в ЛС
            try:
                embed = discord.Embed(
                    title="🔒 Ваш приватный канал создан!",
                    description=f"Канал: **{new_channel.name}**",
                    color=discord.Color.green()
                )
                embed.add_field(
                    name="⚙️ Команды управления:",
                    value=(
                        f"`{PREFIX}invite @пользователь` - пригласить\n"
                        f"`{PREFIX}kick @пользователь` - удалить\n"
                        f"`{PREFIX}lock` - закрыть канал\n"
                        f"`{PREFIX}unlock` - открыть канал\n"
                        f"`{PREFIX}rename <название>` - переименовать\n"
                        f"`{PREFIX}limit <число>` - установить лимит\n"
                        f"`{PREFIX}hide` - скрыть канал\n"
                        f"`{PREFIX}show` - показать канал"
                    ),
                    inline=False
                )
                embed.add_field(
                    name="💡 Подсказка:",
                    value="Все команды работают только в вашем приватном канале",
                    inline=False
                )
                embed.set_footer(text=f"Для получения помощи используйте {PREFIX}info")
                
                await member.send(embed=embed)
            except:
                pass
                
        except Exception as e:
            print(f"Ошибка создания канала: {e}")
            try:
                await member.send(f"❌ Ошибка при создании канала: {str(e)}")
            except:
                pass
    
    # Проверка пустых каналов
    if before.channel and str(before.channel.id) in guild_data['temp_channels']:
        if len(before.channel.members) == 0 and guild_data['config']['auto_delete_empty']:
            try:
                await before.channel.delete()
                if str(before.channel.id) in guild_data['temp_channels']:
                    del guild_data['temp_channels'][str(before.channel.id)]
                    save_guild_data(member.guild.id, guild_data)
            except:
                pass

# Команды бота
@bot.command(name='info')
async def info(ctx):
    """Показать информацию о командах"""
    
    embed = discord.Embed(
        title="🔒 Instant Private Channels",
        description=f"Бот для создания приватных голосовых каналов\n\n**Все команды начинаются с `{PREFIX}`**",
        color=discord.Color.purple()
    )
    
    if bot.user.avatar:
        embed.set_thumbnail(url=bot.user.avatar.url)
    
    embed.add_field(
        name="📋 **ОСНОВНОЕ**",
        value=(
            f"`{PREFIX}info` - эта информация\n"
            f"`{PREFIX}setup` - настроить сервер (админы)\n"
            f"`{PREFIX}ping` - проверить пинг\n"
            f"`{PREFIX}help` - помощь"
        ),
        inline=False
    )
    
    embed.add_field(
        name="🔧 **СОЗДАНИЕ КАНАЛА**",
        value=(
            "1. Зайдите в канал **'➕ Создать приватный'**\n"
            "2. Автоматически создастся ваш канал\n"
            "3. Вы станете владельцем\n"
            "4. Получите настройки в ЛС"
        ),
        inline=False
    )
    
    embed.add_field(
        name="⚙️ **КОМАНДЫ ДЛЯ ВЛАДЕЛЬЦЕВ**",
        value=(
            f"`{PREFIX}invite @пользователь` - приглашить\n"
            f"`{PREFIX}kick @пользователь` - удалить\n"
            f"`{PREFIX}lock` - закрыть канал\n"
            f"`{PREFIX}unlock` - открыть канал\n"
            f"`{PREFIX}rename <название>` - переименовать\n"
            f"`{PREFIX}limit <число>` - лимит участников\n"
            f"`{PREFIX}hide` - скрыть канал\n"
            f"`{PREFIX}show` - показать канал\n"
            f"`{PREFIX}transfer @пользователь` - передать права"
        ),
        inline=False
    )
    
    embed.add_field(
        name="👥 **КОМАНДЫ ДЛЯ УЧАСТНИКОВ**",
        value=(
            f"`{PREFIX}list` - список каналов\n"
            f"`{PREFIX}members` - участники канала\n"
            f"`{PREFIX}leave` - покинуть канал"
        ),
        inline=False
    )
    
    embed.add_field(
        name="🎮 **ОСОБЕННОСТИ**",
        value=(
            "• Автосоздание каналов\n"
            "• Полный контроль владельца\n"
            "• Автоудаление пустых каналов\n"
            "• Защита от неавторизованных\n"
            "• Настройки в ЛС"
        ),
        inline=False
    )
    
    embed.set_footer(text=f"ID бота: {BOT_ID} | Версия 4.0")
    
    await ctx.send(embed=embed)

@bot.command(name='setup')
@commands.has_permissions(administrator=True)
async def setup(ctx):
    """Настроить сервер для приватных каналов"""
    
    guild_data = get_guild_data(ctx.guild.id)
    
    # Создаем категорию если её нет
    category_name = guild_data['config']['category_name']
    category = discord.utils.get(ctx.guild.categories, name=category_name)
    
    if not category:
        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(view_channel=True),
            ctx.guild.me: discord.PermissionOverwrite(manage_channels=True, view_channel=True)
        }
        category = await ctx.guild.create_category(category_name, overwrites=overwrites)
    
    # Создаем канал для создания приватных каналов
    create_channel_name = "➕ Создать приватный"
    create_channel = discord.utils.get(category.voice_channels, name=create_channel_name)
    
    if not create_channel:
        create_channel = await category.create_voice_channel(
            name=create_channel_name,
            position=0
        )
    
    # Создаем информационный канал
    info_channel_name = "📋-информация"
    info_channel = discord.utils.get(category.text_channels, name=info_channel_name)
    
    if not info_channel:
        info_channel = await category.create_text_channel(
            name=info_channel_name,
            topic="Информация о приватных каналах",
            position=1
        )
        
        # Отправляем информацию в канал
        info_embed = discord.Embed(
            title="🔒 Приватные голосовые каналы",
            description="Добро пожаловать в раздел приватных каналов!",
            color=discord.Color.blue()
        )
        
        info_embed.add_field(
            name="Как создать канал?",
            value="Зайдите в канал **➕ Создать приватный** и ваш канал создастся автоматически",
            inline=False
        )
        
        info_embed.add_field(
            name="Основные команды",
            value=(
                f"`{PREFIX}info` - все команды\n"
                f"`{PREFIX}invite @пользователь` - пригласить\n"
                f"`{PREFIX}lock` / `{PREFIX}unlock` - закрыть/открыть\n"
                f"`{PREFIX}rename название` - переименовать"
            ),
            inline=False
        )
        
        info_embed.add_field(
            name="Правила",
            value=(
                "• Не спамить в каналах\n"
                "• Уважать других пользователей\n"
                "• Пустые каналы удаляются автоматически\n"
                "• Владелец канала несет ответственность за порядок"
            ),
            inline=False
        )
        
        info_embed.set_footer(text=f"Используйте {PREFIX}help для помощи")
        
        await info_channel.send(embed=info_embed)
    
    embed = discord.Embed(
        title="✅ Настройка завершена!",
        description="Сервер готов к использованию приватных каналов",
        color=discord.Color.green()
    )
    
    embed.add_field(name="📁 Категория", value=category.mention, inline=True)
    embed.add_field(name="➕ Канал для создания", value=create_channel.mention, inline=True)
    embed.add_field(name="📋 Информационный канал", value=info_channel.mention, inline=True)
    embed.add_field(name="👑 Администратор", value=ctx.author.mention, inline=True)
    
    embed.add_field(
        name="📋 Как пользоваться:",
        value=(
            "1. Зайдите в канал **➕ Создать приватный**\n"
            "2. Создастся ваш личный канал\n"
            "3. Управляйте им командами\n"
            "4. Приглашайте друзей"
        ),
        inline=False
    )
    
    embed.add_field(
        name="⚙️ Команды владельца:",
        value=(
            f"`{PREFIX}invite` - пригласить\n"
            f"`{PREFIX}lock` - закрыть канал\n"
            f"`{PREFIX}rename` - переименовать"
        ),
        inline=False
    )
    
    await ctx.send(embed=embed)

@bot.command(name='invite')
async def invite(ctx, member: discord.Member):
    """Пригласить пользователя в ваш канал"""
    
    if not ctx.author.voice or not ctx.author.voice.channel:
        await ctx.send("❌ Вы должны быть в голосовом канале")
        return
    
    channel = ctx.author.voice.channel
    guild_data = get_guild_data(ctx.guild.id)
    channel_data = guild_data['temp_channels'].get(str(channel.id))
    
    if not channel_data:
        await ctx.send("❌ Это не приватный канал")
        return
    
    if channel_data['owner_id'] != ctx.author.id:
        await ctx.send("❌ Вы не владелец этого канала")
        return
    
    if member.id == ctx.author.id:
        await ctx.send("❌ Вы не можете пригласить себя")
        return
    
    # Добавляем разрешение для пользователя
    overwrites = channel.overwrites
    overwrites[member] = discord.PermissionOverwrite(connect=True, view_channel=True)
    
    try:
        await channel.edit(overwrites=overwrites)
        
        # Добавляем в список участников
        if member.id not in channel_data['members']:
            channel_data['members'].append(member.id)
            save_guild_data(ctx.guild.id, guild_data)
        
        embed = discord.Embed(
            title="✅ Приглашение отправлено!",
            description=f"{member.mention} был приглашен в канал {channel.mention}",
            color=discord.Color.green()
        )
        embed.add_field(name="👑 Владелец", value=ctx.author.mention, inline=True)
        embed.add_field(name="👥 Участников", value=len(channel.members), inline=True)
        embed.add_field(name="Канал", value=channel.mention, inline=True)
        
        await ctx.send(embed=embed)
        
        # Отправляем уведомление приглашенному
        try:
            invite_embed = discord.Embed(
                title="🎉 Вас пригласили в приватный канал!",
                description=f"Владелец: {ctx.author.mention}\nКанал: {channel.name}",
                color=discord.Color.blue()
            )
            invite_embed.set_footer(text="Зайдите в голосовой чат чтобы присоединиться")
            await member.send(embed=invite_embed)
        except:
            pass
            
    except Exception as e:
        await ctx.send(f"❌ Ошибка: {str(e)}")

@bot.command(name='kick')
async def kick(ctx, member: discord.Member):
    """Удалить пользователя из вашего канала"""
    
    if not ctx.author.voice or not ctx.author.voice.channel:
        await ctx.send("❌ Вы должны быть в голосовом канале")
        return
    
    channel = ctx.author.voice.channel
    guild_data = get_guild_data(ctx.guild.id)
    channel_data = guild_data['temp_channels'].get(str(channel.id))
    
    if not channel_data:
        await ctx.send("❌ Это не приватный канал")
        return
    
    if channel_data['owner_id'] != ctx.author.id:
        await ctx.send("❌ Вы не владелец этого канала")
        return
    
    if member.id == ctx.author.id:
        await ctx.send("❌ Вы не можете удалить себя")
        return
    
    # Убираем разрешение для пользователя
    overwrites = channel.overwrites
    if member in overwrites:
        overwrites[member] = discord.PermissionOverwrite(connect=False, view_channel=False)
    
    try:
        await channel.edit(overwrites=overwrites)
        
        # Удаляем из списка участников
        if member.id in channel_data['members']:
            channel_data['members'].remove(member.id)
            save_guild_data(ctx.guild.id, guild_data)
        
        # Пытаемся кикнуть из канала если пользователь там
        if member.voice and member.voice.channel == channel:
            try:
                await member.move_to(None)
            except:
                pass
        
        embed = discord.Embed(
            title="✅ Пользователь удален",
            description=f"{member.mention} был удален из канала",
            color=discord.Color.orange()
        )
        embed.add_field(name="👑 Владелец", value=ctx.author.mention, inline=True)
        embed.add_field(name="Канал", value=channel.mention, inline=True)
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ Ошибка: {str(e)}")

@bot.command(name='lock')
async def lock(ctx):
    """Закрыть ваш канал для новых участников"""
    
    if not ctx.author.voice or not ctx.author.voice.channel:
        await ctx.send("❌ Вы должны быть в голосовом канале")
        return
    
    channel = ctx.author.voice.channel
    guild_data = get_guild_data(ctx.guild.id)
    channel_data = guild_data['temp_channels'].get(str(channel.id))
    
    if not channel_data:
        await ctx.send("❌ Это не приватный канал")
        return
    
    if channel_data['owner_id'] != ctx.author.id:
        await ctx.send("❌ Вы не владелец этого канала")
        return
    
    # Закрываем канал для всех
    overwrites = {
        ctx.guild.default_role: discord.PermissionOverwrite(connect=False, view_channel=True),
        ctx.author: discord.PermissionOverwrite(connect=True, manage_channels=True, view_channel=True)
    }
    
    # Сохраняем права для текущих участников
    for member in channel.members:
        if member.id != ctx.author.id:
            overwrites[member] = discord.PermissionOverwrite(connect=True, view_channel=True)
    
    try:
        await channel.edit(overwrites=overwrites)
        channel_data['locked'] = True
        save_guild_data(ctx.guild.id, guild_data)
        
        embed = discord.Embed(
            title="🔒 Канал закрыт!",
            description=f"Канал {channel.mention} теперь закрыт для новых участников",
            color=discord.Color.orange()
        )
        embed.add_field(name="👑 Владелец", value=ctx.author.mention, inline=True)
        embed.add_field(name="👥 Участников", value=len(channel.members), inline=True)
        embed.add_field(name="Статус", value="🔒 Закрыт", inline=True)
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ Ошибка: {str(e)}")

@bot.command(name='unlock')
async def unlock(ctx):
    """Открыть ваш канал для всех"""
    
    if not ctx.author.voice or not ctx.author.voice.channel:
        await ctx.send("❌ Вы должны быть в голосовом канале")
        return
    
    channel = ctx.author.voice.channel
    guild_data = get_guild_data(ctx.guild.id)
    channel_data = guild_data['temp_channels'].get(str(channel.id))
    
    if not channel_data:
        await ctx.send("❌ Это не приватный канал")
        return
    
    if channel_data['owner_id'] != ctx.author.id:
        await ctx.send("❌ Вы не владелец этого канала")
        return
    
    # Открываем канал для всех
    overwrites = {
        ctx.guild.default_role: discord.PermissionOverwrite(connect=True, view_channel=True),
        ctx.author: discord.PermissionOverwrite(connect=True, manage_channels=True, view_channel=True)
    }
    
    # Сохраняем права для текущих участников
    for member in channel.members:
        if member.id != ctx.author.id:
            overwrites[member] = discord.PermissionOverwrite(connect=True, view_channel=True)
    
    try:
        await channel.edit(overwrites=overwrites)
        channel_data['locked'] = False
        save_guild_data(ctx.guild.id, guild_data)
        
        embed = discord.Embed(
            title="🔓 Канал открыт!",
            description=f"Канал {channel.mention} теперь открыт для всех",
            color=discord.Color.green()
        )
        embed.add_field(name="👑 Владелец", value=ctx.author.mention, inline=True)
        embed.add_field(name="👥 Участников", value=len(channel.members), inline=True)
        embed.add_field(name="Статус", value="🔓 Открыт", inline=True)
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ Ошибка: {str(e)}")

@bot.command(name='rename')
async def rename(ctx, *, new_name: str):
    """Переименовать ваш канал"""
    
    if not ctx.author.voice or not ctx.author.voice.channel:
        await ctx.send("❌ Вы должны быть в голосовом канале")
        return
    
    channel = ctx.author.voice.channel
    guild_data = get_guild_data(ctx.guild.id)
    channel_data = guild_data['temp_channels'].get(str(channel.id))
    
    if not channel_data:
        await ctx.send("❌ Это не приватный канал")
        return
    
    if channel_data['owner_id'] != ctx.author.id:
        await ctx.send("❌ Вы не владелец этого канала")
        return
    
    # Проверяем длину названия
    if len(new_name) > 32:
        await ctx.send("❌ Название слишком длинное (максимум 32 символа)")
        return
    
    # Добавляем эмодзи если его нет
    if not new_name.startswith("🔒"):
        new_name = f"🔒 {new_name}"
    
    try:
        await channel.edit(name=new_name)
        channel_data['name'] = new_name
        save_guild_data(ctx.guild.id, guild_data)
        
        embed = discord.Embed(
            title="✅ Канал переименован",
            description=f"Канал переименован в **{new_name}**",
            color=discord.Color.green()
        )
        embed.add_field(name="👑 Владелец", value=ctx.author.mention, inline=True)
        embed.add_field(name="Старое название", value=channel_data.get('old_name', channel.name), inline=True)
        embed.add_field(name="Новое название", value=new_name, inline=True)
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ Ошибка: {str(e)}")

@bot.command(name='limit')
async def limit(ctx, limit: int):
    """Установить лимит участников для вашего канала"""
    
    if not ctx.author.voice or not ctx.author.voice.channel:
        await ctx.send("❌ Вы должны быть в голосовом канале")
        return
    
    if limit < 0 or limit > 99:
        await ctx.send("❌ Лимит должен быть от 0 до 99")
        return
    
    channel = ctx.author.voice.channel
    guild_data = get_guild_data(ctx.guild.id)
    channel_data = guild_data['temp_channels'].get(str(channel.id))
    
    if not channel_data:
        await ctx.send("❌ Это не приватный канал")
        return
    
    if channel_data['owner_id'] != ctx.author.id:
        await ctx.send("❌ Вы не владелец этого канала")
        return
    
    try:
        await channel.edit(user_limit=limit)
        channel_data['limit'] = limit
        save_guild_data(ctx.guild.id, guild_data)
        
        embed = discord.Embed(
            title="✅ Лимит установлен",
            color=discord.Color.green()
        )
        
        if limit == 0:
            embed.description = "Лимит участников убран"
            embed.add_field(name="Лимит", value="∞ (без лимита)", inline=True)
        else:
            embed.description = f"Лимит участников установлен: **{limit}**"
            embed.add_field(name="Лимит", value=str(limit), inline=True)
        
        embed.add_field(name="👑 Владелец", value=ctx.author.mention, inline=True)
        embed.add_field(name="Канал", value=channel.mention, inline=True)
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ Ошибка: {str(e)}")

@bot.command(name='hide')
async def hide(ctx):
    """Скрыть ваш канал от всех"""
    
    if not ctx.author.voice or not ctx.author.voice.channel:
        await ctx.send("❌ Вы должны быть в голосовом канале")
        return
    
    channel = ctx.author.voice.channel
    guild_data = get_guild_data(ctx.guild.id)
    channel_data = guild_data['temp_channels'].get(str(channel.id))
    
    if not channel_data:
        await ctx.send("❌ Это не приватный канал")
        return
    
    if channel_data['owner_id'] != ctx.author.id:
        await ctx.send("❌ Вы не владелец этого канала")
        return
    
    # Скрываем канал
    overwrites = channel.overwrites
    overwrites[ctx.guild.default_role] = discord.PermissionOverwrite(view_channel=False)
    
    try:
        await channel.edit(overwrites=overwrites)
        channel_data['hidden'] = True
        save_guild_data(ctx.guild.id, guild_data)
        
        embed = discord.Embed(
            title="🙈 Канал скрыт!",
            description=f"Канал {channel.mention} теперь скрыт от всех",
            color=discord.Color.dark_gray()
        )
        embed.add_field(name="👑 Владелец", value=ctx.author.mention, inline=True)
        embed.add_field(name="👥 Участников", value=len(channel.members), inline=True)
        embed.add_field(name="Статус", value="🙈 Скрыт", inline=True)
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ Ошибка: {str(e)}")

@bot.command(name='show')
async def show(ctx):
    """Показать ваш канал всем"""
    
    if not ctx.author.voice or not ctx.author.voice.channel:
        await ctx.send("❌ Вы должны быть в голосовом канале")
        return
    
    channel = ctx.author.voice.channel
    guild_data = get_guild_data(ctx.guild.id)
    channel_data = guild_data['temp_channels'].get(str(channel.id))
    
    if not channel_data:
        await ctx.send("❌ Это не приватный канал")
        return
    
    if channel_data['owner_id'] != ctx.author.id:
        await ctx.send("❌ Вы не владелец этого канала")
        return
    
    # Показываем канал
    overwrites = channel.overwrites
    overwrites[ctx.guild.default_role] = discord.PermissionOverwrite(view_channel=True)
    
    try:
        await channel.edit(overwrites=overwrites)
        channel_data['hidden'] = False
        save_guild_data(ctx.guild.id, guild_data)
        
        embed = discord.Embed(
            title="👁️ Канал теперь виден!",
            description=f"Канал {channel.mention} теперь виден всем",
            color=discord.Color.green()
        )
        embed.add_field(name="👑 Владелец", value=ctx.author.mention, inline=True)
        embed.add_field(name="👥 Участников", value=len(channel.members), inline=True)
        embed.add_field(name="Статус", value="👁️ Виден", inline=True)
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ Ошибка: {str(e)}")

@bot.command(name='transfer')
async def transfer(ctx, new_owner: discord.Member):
    """Передать права владельца другому пользователю"""
    
    if not ctx.author.voice or not ctx.author.voice.channel:
        await ctx.send("❌ Вы должны быть в голосовом канале")
        return
    
    channel = ctx.author.voice.channel
    guild_data = get_guild_data(ctx.guild.id)
    channel_data = guild_data['temp_channels'].get(str(channel.id))
    
    if not channel_data:
        await ctx.send("❌ Это не приватный канал")
        return
    
    if channel_data['owner_id'] != ctx.author.id:
        await ctx.send("❌ Вы не владелец этого канала")
        return
    
    # Проверяем что новый владелец в канале
    if not new_owner.voice or new_owner.voice.channel != channel:
        await ctx.send("❌ Новый владелец должен быть в этом канале")
        return
    
    if new_owner.id == ctx.author.id:
        await ctx.send("❌ Вы не можете передать права самому себе")
        return
    
    # Обновляем права
    overwrites = channel.overwrites
    overwrites[ctx.author] = discord.PermissionOverwrite(connect=True, view_channel=True)
    overwrites[new_owner] = discord.PermissionOverwrite(connect=True, manage_channels=True, view_channel=True)
    
    try:
        await channel.edit(overwrites=overwrites)
        channel_data['owner_id'] = new_owner.id
        save_guild_data(ctx.guild.id, guild_data)
        
        embed = discord.Embed(
            title="👑 Права переданы!",
            description=f"Права владельца канала переданы {new_owner.mention}",
            color=discord.Color.gold()
        )
        embed.add_field(name="Старый владелец", value=ctx.author.mention, inline=True)
        embed.add_field(name="Новый владелец", value=new_owner.mention, inline=True)
        embed.add_field(name="Канал", value=channel.mention, inline=True)
        
        await ctx.send(embed=embed)
        
        # Отправляем уведомление новому владельцу
        try:
            owner_embed = discord.Embed(
                title="👑 Вы стали владельцем канала!",
                description=f"Канал: {channel.name}\nПредыдущий владелец: {ctx.author.mention}",
                color=discord.Color.gold()
            )
            owner_embed.add_field(
                name="Теперь вы можете:",
                value=(
                    f"`{PREFIX}invite` - приглашать\n"
                    f"`{PREFIX}kick` - удалять\n"
                    f"`{PREFIX}rename` - переименовывать\n"
                    f"`{PREFIX}lock` - закрывать канал"
                ),
                inline=False
            )
            await new_owner.send(embed=owner_embed)
        except:
            pass
        
    except Exception as e:
        await ctx.send(f"❌ Ошибка: {str(e)}")

@bot.command(name='list')
async def list_channels(ctx):
    """Показать список приватных каналов"""
    
    guild_data = get_guild_data(ctx.guild.id)
    channels = guild_data['temp_channels']
    
    if not channels:
        embed = discord.Embed(
            title="📭 Нет активных каналов",
            description="На сервере нет активных приватных каналов",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="Как создать канал?",
            value="Зайдите в канал **➕ Создать приватный** чтобы создать свой канал",
            inline=False
        )
        await ctx.send(embed=embed)
        return
    
    embed = discord.Embed(
        title="📋 Активные приватные каналы",
        description=f"Всего каналов: {len(channels)}",
        color=discord.Color.blue()
    )
    
    active_channels = 0
    for channel_id, data in list(channels.items())[:12]:  # Показываем первые 12
        channel = ctx.guild.get_channel(int(channel_id))
        if channel:
            active_channels += 1
            owner = ctx.guild.get_member(data['owner_id'])
            owner_name = owner.mention if owner else "Неизвестно"
            members_count = len(channel.members) if channel.members else 0
            
            status_icons = ""
            if data.get('locked', False):
                status_icons += "🔒"
            else:
                status_icons += "🔓"
            
            if data.get('hidden', False):
                status_icons += " 🙈"
            else:
                status_icons += " 👁️"
            
            limit = data.get('limit', 0)
            limit_text = str(limit) if limit > 0 else "∞"
            
            embed.add_field(
                name=f"{status_icons} {data.get('name', 'Канал')[:20]}",
                value=(
                    f"Владелец: {owner_name}\n"
                    f"Участников: {members_count}/{limit_text}\n"
                    f"Канал: {channel.mention}"
                ),
                inline=True
            )
    
    if len(channels) > 12:
        embed.set_footer(text=f"И ещё {len(channels) - 12} каналов...")
    
    if active_channels == 0:
        embed.description = "Все каналы в данный момент пусты"
    
    await ctx.send(embed=embed)

@bot.command(name='members')
async def channel_members(ctx):
    """Показать участников текущего канала"""
    
    if not ctx.author.voice or not ctx.author.voice.channel:
        await ctx.send("❌ Вы должны быть в голосовом канале")
        return
    
    channel = ctx.author.voice.channel
    members = channel.members
    
    if not members:
        embed = discord.Embed(
            title=f"📭 Канал пуст",
            description=f"В канале {channel.mention} никого нет",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)
        return
    
    guild_data = get_guild_data(ctx.guild.id)
    channel_data = guild_data['temp_channels'].get(str(channel.id))
    
    embed = discord.Embed(
        title=f"👥 Участники канала: {channel.name}",
        description=f"Всего участников: {len(members)}",
        color=discord.Color.blue()
    )
    
    members_list = []
    for member in members:
        prefix = "👑 " if channel_data and member.id == channel_data.get('owner_id') else "👤 "
        members_list.append(f"{prefix}{member.mention}")
    
    embed.add_field(name="Участники", value="\n".join(members_list), inline=False)
    
    if channel_data:
        owner = ctx.guild.get_member(channel_data['owner_id'])
        if owner:
            embed.add_field(name="Владелец", value=owner.mention, inline=True)
        
        status = "🔒 Закрыт" if channel_data.get('locked', False) else "🔓 Открыт"
        embed.add_field(name="Доступ", value=status, inline=True)
        
        limit = channel_data.get('limit', 0)
        embed.add_field(name="Лимит", value=str(limit) if limit > 0 else "∞", inline=True)
    
    await ctx.send(embed=embed)

@bot.command(name='leave')
async def leave_channel(ctx):
    """Покинуть текущий канал"""
    
    if not ctx.author.voice or not ctx.author.voice.channel:
        await ctx.send("❌ Вы не в голосовом канале")
        return
    
    channel = ctx.author.voice.channel
    guild_data = get_guild_data(ctx.guild.id)
    channel_data = guild_data['temp_channels'].get(str(channel.id))
    
    if channel_data:
        # Если это приватный канал и пользователь владелец
        if ctx.author.id == channel_data['owner_id']:
            embed = discord.Embed(
                title="❌ Вы владелец канала",
                description=f"Вы не можете покинуть канал как владелец",
                color=discord.Color.red()
            )
            embed.add_field(
                name="Доступные опции:",
                value=(
                    f"`{PREFIX}transfer @пользователь` - передать права\n"
                    f"Покинуть канал вручную через Discord"
                ),
                inline=False
            )
            await ctx.send(embed=embed)
            return
        
        # Убираем права если есть
        overwrites = channel.overwrites
        if ctx.author in overwrites:
            overwrites[ctx.author] = discord.PermissionOverwrite(connect=False, view_channel=False)
            try:
                await channel.edit(overwrites=overwrites)
            except:
                pass
        
        # Удаляем из списка участников
        if ctx.author.id in channel_data['members']:
            channel_data['members'].remove(ctx.author.id)
            save_guild_data(ctx.guild.id, guild_data)
    
    try:
        await ctx.author.move_to(None)
        embed = discord.Embed(
            title="✅ Вы покинули канал",
            description="Вы успешно покинули голосовой канал",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
    except:
        await ctx.send("❌ Не удалось покинуть канал")

@bot.command(name='ping')
async def ping(ctx):
    """Проверить пинг бота"""
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
    embed.add_field(name="ID бота", value=str(BOT_ID), inline=True)
    embed.add_field(name="Префикс", value=PREFIX, inline=True)
    embed.add_field(name="Версия", value="4.0", inline=True)
    
    await ctx.send(embed=embed)

@bot.command(name='help')
async def help_command(ctx):
    """Помощь по использованию"""
    
    embed = discord.Embed(
        title="❓ Помощь по использованию",
        description="Часто задаваемые вопросы и решения проблем",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="❓ Как создать приватный канал?",
        value="Зайдите в канал **'➕ Создать приватный'** и он создастся автоматически",
        inline=False
    )
    
    embed.add_field(
        name="❓ Как пригласить друга?",
        value=f"Будучи в своём канале, используйте команду `{PREFIX}invite @друг`",
        inline=False
    )
    
    embed.add_field(
        name="❓ Как переименовать канал?",
        value=f"Используйте команду `{PREFIX}rename новое_название` находясь в канале",
        inline=False
    )
    
    embed.add_field(
        name="❓ Что делать если не приходят настройки в ЛС?",
        value="Проверьте настройки приватности Discord. Разрешите ЛС от участников сервера",
        inline=False
    )
    
    embed.add_field(
        name="❓ Канал не удаляется после выхода?",
        value="Канал удалится автоматически когда все участники выйдут из него",
        inline=False
    )
    
    embed.add_field(
        name="❓ Как передать права владельца?",
        value=f"Используйте команду `{PREFIX}transfer @пользователь` находясь в канале",
        inline=False
    )
    
    embed.add_field(
        name="⚡ Быстрые команды",
        value=(
            f"`{PREFIX}invite` - пригласить\n"
            f"`{PREFIX}lock/unlock` - закрыть/открыть\n"
            f"`{PREFIX}rename` - переименовать\n"
            f"`{PREFIX}limit` - установить лимит"
        ),
        inline=False
    )
    
    embed.set_footer(text=f"Для полного списка команд используйте {PREFIX}info")
    
    await ctx.send(embed=embed)

@bot.command(name='config')
@commands.has_permissions(administrator=True)
async def config_command(ctx, setting: str = None, value: str = None):
    """Настройки бота для администраторов"""
    
    guild_data = get_guild_data(ctx.guild.id)
    
    if not setting:
        # Показать текущие настройки
        embed = discord.Embed(
            title="⚙️ Настройки бота",
            description="Текущие настройки приватных каналов",
            color=discord.Color.blue()
        )
        
        config = guild_data['config']
        embed.add_field(name="📁 Название категории", value=config['category_name'], inline=True)
        embed.add_field(name="🔢 Макс. каналов", value=str(config['max_channels']), inline=True)
        embed.add_field(name="🗑️ Автоудаление", value="✅ Вкл" if config['auto_delete_empty'] else "❌ Выкл", inline=True)
        embed.add_field(name="👥 Лимит по умолчанию", value=str(config['default_limit']) or "∞", inline=True)
        embed.add_field(name="📊 Активных каналов", value=str(len(guild_data['temp_channels'])), inline=True)
        
        embed.add_field(
            name="💡 Доступные настройки:",
            value=(
                f"`{PREFIX}config category_name <название>` - изменить категорию\n"
                f"`{PREFIX}config max_channels <число>` - макс. каналов\n"
                f"`{PREFIX}config auto_delete <on/off>` - автоудаление\n"
                f"`{PREFIX}config default_limit <число>` - лимит по умолч."
            ),
            inline=False
        )
        
        await ctx.send(embed=embed)
        return
    
    # Изменение настроек
    setting = setting.lower()
    
    if setting == 'category_name' and value:
        guild_data['config']['category_name'] = value
        save_guild_data(ctx.guild.id, guild_data)
        
        embed = discord.Embed(
            title="✅ Настройка изменена",
            description=f"Название категории изменено на: **{value}**",
            color=discord.Color.green()
        )
        embed.add_field(name="Важно", value="Изменение вступит в силу при создании новых каналов", inline=False)
        await ctx.send(embed=embed)
    
    elif setting == 'max_channels' and value:
        try:
            max_channels = int(value)
            if max_channels < 1 or max_channels > 100:
                await ctx.send("❌ Макс. количество каналов должно быть от 1 до 100")
                return
            guild_data['config']['max_channels'] = max_channels
            save_guild_data(ctx.guild.id, guild_data)
            
            embed = discord.Embed(
                title="✅ Настройка изменена",
                description=f"Максимальное количество каналов установлено: **{max_channels}**",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        except:
            await ctx.send("❌ Неверное значение. Используйте число")
    
    elif setting == 'auto_delete' and value:
        if value.lower() in ['on', 'true', 'yes', 'вкл', '1']:
            guild_data['config']['auto_delete_empty'] = True
            save_guild_data(ctx.guild.id, guild_data)
            
            embed = discord.Embed(
                title="✅ Настройка изменена",
                description="Автоудаление пустых каналов включено",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        elif value.lower() in ['off', 'false', 'no', 'выкл', '0']:
            guild_data['config']['auto_delete_empty'] = False
            save_guild_data(ctx.guild.id, guild_data)
            
            embed = discord.Embed(
                title="✅ Настройка изменена",
                description="Автоудаление пустых каналов выключено",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ Используйте: on/off, true/false, yes/no, вкл/выкл")
    
    elif setting == 'default_limit' and value:
        try:
            limit = int(value)
            if limit < 0 or limit > 99:
                await ctx.send("❌ Лимит должен быть от 0 до 99")
                return
            guild_data['config']['default_limit'] = limit
            save_guild_data(ctx.guild.id, guild_data)
            
            embed = discord.Embed(
                title="✅ Настройка изменена",
                color=discord.Color.green()
            )
            
            if limit == 0:
                embed.description = "Лимит участников по умолчанию убран"
                embed.add_field(name="Новый лимит", value="∞ (без лимита)", inline=True)
            else:
                embed.description = f"Лимит участников по умолчанию установлен: **{limit}**"
                embed.add_field(name="Новый лимит", value=str(limit), inline=True)
            
            await ctx.send(embed=embed)
        except:
            await ctx.send("❌ Неверное значение. Используйте число от 0 до 99")
    
    else:
        await ctx.send(f"❌ Неизвестная настройка. Используйте `{PREFIX}config` для списка настроек")

@bot.command(name='cleanup')
@commands.has_permissions(administrator=True)
async def cleanup(ctx):
    """Очистить все пустые приватные каналы"""
    
    guild_data = get_guild_data(ctx.guild.id)
    channels_to_delete = []
    
    for channel_id_str in list(guild_data['temp_channels'].keys()):
        channel = ctx.guild.get_channel(int(channel_id_str))
        if channel and len(channel.members) == 0:
            channels_to_delete.append(channel)
    
    if not channels_to_delete:
        await ctx.send("✅ Нет пустых каналов для удаления")
        return
    
    deleted_count = 0
    for channel in channels_to_delete:
        try:
            await channel.delete()
            del guild_data['temp_channels'][str(channel.id)]
            deleted_count += 1
        except:
            pass
    
    save_guild_data(ctx.guild.id, guild_data)
    
    embed = discord.Embed(
        title="🧹 Очистка завершена",
        description=f"Удалено пустых каналов: **{deleted_count}**",
        color=discord.Color.green()
    )
    embed.add_field(name="Осталось каналов", value=str(len(guild_data['temp_channels'])), inline=True)
    
    await ctx.send(embed=embed)

@bot.command(name='stats')
async def stats_command(ctx):
    """Статистика бота и каналов"""
    
    guild_data = get_guild_data(ctx.guild.id)
    
    total_channels = len(guild_data['temp_channels'])
    empty_channels = 0
    total_members = 0
    
    for channel_id, data in guild_data['temp_channels'].items():
        channel = ctx.guild.get_channel(int(channel_id))
        if channel:
            if len(channel.members) == 0:
                empty_channels += 1
            else:
                total_members += len(channel.members)
    
    embed = discord.Embed(
        title="📊 Статистика приватных каналов",
        color=discord.Color.blue()
    )
    
    embed.add_field(name="Всего каналов", value=str(total_channels), inline=True)
    embed.add_field(name="Активных каналов", value=str(total_channels - empty_channels), inline=True)
    embed.add_field(name="Пустых каналов", value=str(empty_channels), inline=True)
    embed.add_field(name="Всего участников", value=str(total_members), inline=True)
    embed.add_field(name="Макс. каналов", value=str(guild_data['config']['max_channels']), inline=True)
    embed.add_field(name="Автоудаление", value="✅ Вкл" if guild_data['config']['auto_delete_empty'] else "❌ Выкл", inline=True)
    
    # Информация о боте
    embed.add_field(name="🤖 Бот", value=bot.user.name, inline=True)
    embed.add_field(name="📈 Пинг", value=f"{round(bot.latency * 1000)}мс", inline=True)
    embed.add_field(name="🔧 Префикс", value=PREFIX, inline=True)
    
    embed.set_footer(text=f"ID бота: {BOT_ID}")
    
    await ctx.send(embed=embed)

# Запуск бота
if __name__ == "__main__":
    print(f"Запуск бота Instant Private Channels...")
    print(f"ID бота: {BOT_ID}")
    print(f"Префикс команд: {PREFIX}")
    bot.run(TOKEN)