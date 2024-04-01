from discord.ext import commands
import yt_dlp as youtube_dl
import discord
import asyncio
import dotenv
import os

global queue, i, play_flag

old_files = os.listdir('D:/ITAN/')
for fil in range(len(old_files)):
    os.remove(f'D:/ITAN/{old_files[fil]}')

intents = discord.Intents().all()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='!', intents=intents)

ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': 'D:/ITAN/%(title)s.%(ext)s',
    'restrictfilenames': True,
    'nocheckcertificate': True,
    'ignoreerrors': True,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
}
ydl = youtube_dl.YoutubeDL(ydl_opts)
ffmpeg_options = {'options': '-vn'}


@bot.command(name='пой', help='Воспроизвести')
async def play_song(ctx, url):
    global queue, play_flag, i
    if not ctx.message.author.voice:
        await ctx.send("{} is not connected to a voice channel".format(ctx.message.author.name))
        return
    else:
        channel = ctx.message.author.voice.channel
    try: await channel.connect()
    except Exception as err: print(err)

    try:
        queue = queue
    except NameError:
        queue = []
        i = 0
    print(queue)
    try:
        server = ctx.message.guild
        voice_channel = server.voice_client

        async with ctx.typing():
            await download(url, ctx)
        play_flag = True
        try:
            await start_playing(voice_channel, ctx)
        except Exception as err:
            print('>>play err', err)

    except Exception as err:
        print('>>download err', err)
        await ctx.send("Somenthing went wrong - please try again later!")


async def start_playing(voice_channel, ctx):
    global i, play_flag
    while True:
        if play_flag:
            global queue
            try:
                voice_channel.play(discord.FFmpegPCMAudio(executable="ffmpeg.exe", source=f'D:/ITAN/{queue[i]}'))
                await ctx.send(f'**Пою: **`{queue[i]}`'.replace('.webm', '').replace('_', ' '))
                i += 1
                try: os.remove(queue[i-1]) if i > 0 else 0
                except: pass
            except: pass
            await asyncio.sleep(3)
        elif not play_flag:
            break


async def download(url, ctx):
    global queue
    global dwnld_msg, added
    added = None
    if '/playlist' in url:
        added = []
        ydl.download([url])
        files = os.listdir('D:/ITAN/')
        for n in range(len(files)):
            if files[n] not in queue:
                queue.append(files[n])
                added.append(files[n])
            else:
                pass
        dwnld_msg = f'**Плейлист добавлен**\n```{added}```'
        dwnld_msg = dwnld_msg.replace('[', '-').replace(']', '')
        dwnld_msg = dwnld_msg.replace("'", '').replace('_', ' ')
        dwnld_msg = dwnld_msg.replace('.webm', '').replace(', ', '\n-')

    else:
        ydl.download([url])
        files = os.listdir('D:/ITAN/')
        for n in range(len(files)):
            if files[n] not in queue:
                queue.append(files[n])
                added = files[n]
                dwnld_msg = f'**Добавлен: **`{added}`'
                dwnld_msg = dwnld_msg.replace('.webm', '').replace('_', ' ')
            else:
                pass

        if added is None:
            dwnld_msg = '**Трек уже в очереди**'

    await ctx.send(dwnld_msg)


@bot.command(name='дауби', help='Остановать/Продолжить')
async def pause_resume(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_paused():
        voice_client.resume()
    elif voice_client.is_playing():
        voice_client.pause()
    else:
        await ctx.send("`а я и не пою`")


@bot.command(name='другую', help='Включить следущую')
async def next_track(ctx):
    global queue
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await ctx.send('**да есть же**')
        voice_client.stop()


@bot.command(name='яколян', help='Остановить и сбросить очередь')
async def clear_queue(ctx):
    global queue, i, play_flag
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await ctx.send('**Ну всё, надеюсь, напелся**')
        voice_client.stop()
    else:
        await ctx.send("The bot is not playing anything at the moment.")
    play_flag = False
    queue = []
    i = 0
    await asyncio.sleep(1)
    old_tracks = os.listdir('D:/ITAN/')
    for track in range(len(old_tracks)):
        os.remove(f'D:/ITAN/{old_tracks[track]}')


@bot.command(name='очередь', help='Посмотреть что дальше')
async def print_queue(ctx):
    global queue, i
    if len(queue[i:]) > 0:
        queue_msg = f'**Дальше по списку: **```{queue[i:]}```'
        queue_msg = queue_msg.replace('.webm', f'').replace(', ', '\n-')
        queue_msg = queue_msg.replace('[', '-').replace(']', '')
        queue_msg = queue_msg.replace("'", '').replace('_', ' ')
        await ctx.send(queue_msg)
    else:
        queue_msg = '**В очереди нет треков**'
        await ctx.send(queue_msg)

dotenv.load_dotenv('.env')
TOKEN = os.getenv('TOKEN')

if __name__ == "__main__":
    bot.run(TOKEN)
