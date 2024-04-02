from discord.ext import commands
from yt_dlp import YoutubeDL
from pytube import Playlist
import discord
import asyncio
import pytube
import dotenv
import os

global queue, i, play_flag, video_title_name, playlist_added_msg, first_added_of_pl, playlist_urls, dwnld_pl_flag

old_files = os.listdir('D:/ITAN/')
for fil in range(len(old_files)):
    os.remove(f'D:/ITAN/{old_files[fil]}')

intents = discord.Intents().all()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='!', intents=intents)

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
    global i, play_flag, dwnld_pl_flag
    while True:
        if play_flag:
            global queue
            try:
                voice_channel.play(discord.FFmpegPCMAudio(executable="ffmpeg.exe", source=f'D:/ITAN/{queue[i]}'))
                await ctx.send(f'**Пою: **`{queue[i]}`'.replace('.webm', '').replace('_', ' '))
                try:
                    os.remove(f'D:/ITAN/{queue[i-1]}')
                except: pass
                i += 1
            except:
                if dwnld_pl_flag:
                    try:
                        await download_playlist()
                    except: pass
                else: pass

            await asyncio.sleep(3)

        elif not play_flag:
            break


async def download(url, ctx):
    global queue, playlist_urls, first_of_pl, playlist_added_msg
    global dwnld_msg_text, added, first_added_of_pl, dwnld_pl_flag

    if '/playlist' in url:
        dwnld_pl_flag = True
        playlist_urls = Playlist(url)
        first_of_pl = [playlist_urls[0], pytube.YouTube(playlist_urls[0]).streams[0].title]
        YoutubeDL(set_video_name(first_of_pl[1])).download(url)

        files = os.listdir('D:/ITAN/')
        for n in range(len(files)):
            if files[n] not in queue:
                queue.append(files[n])
                first_added_of_pl = files[n]
            else:
                pass
        dwnld_msg_text_pl = f'**Добавлен плейлист: **`\n-{first_added_of_pl}`'.replace('.webm', '\n...').replace('_', ' ')
        playlist_added_msg = await ctx.send(dwnld_msg_text_pl)

    else:
        added = None
        video_title_name = pytube.YouTube(url).streams[0].title
        YoutubeDL(set_video_name(video_title_name)).download(url)
        files = os.listdir('D:/ITAN/')
        for n in range(len(files)):
            if files[n] not in queue:
                queue.append(files[n])
                added = files[n]
                dwnld_msg_text = (f'**Добавлен: **`{added}`'.replace('.webm', '').replace('_', ' '))
            else:
                pass

        if added is None:
            dwnld_msg_text = '**Трек уже в очереди**'

        await ctx.send(dwnld_msg_text)


async def download_playlist():
    global playlist_added_msg, queue, dwnld_pl_flag, first_added_of_pl
    pl_urls = []
    for url in playlist_urls:
        pl_urls.append(url)
    added = []
    for url in pl_urls[1:]:
        try:
            name = pytube.YouTube(url).streams[0].title
            YoutubeDL(set_video_name(name)).download(url)

            files = os.listdir('D:/ITAN/')
            for n in range(len(files)):
                if files[n] not in queue:
                    queue.append(files[n])
                    added.append(files[n])
                else:
                    pass
            if added:
                text = f'**Плейлист добавлен**\n```-{first_added_of_pl}\n{added}```'
                text = text.replace("', '", '\n-')
                text = text.replace("['", '-').replace("']", '')
                text = text.replace('_', ' ').replace('.webm', '')
                await playlist_added_msg.edit(content=text)
        except Exception as err:print('1 ', err)

    dwnld_pl_flag = False


def set_video_name(video_name):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'D:/ITAN/{video_name}.%(ext)s',
        'restrictfilenames': True,
        'nocheckcertificate': True,
        'ignoreerrors': True,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0',
    }
    return ydl_opts


@bot.command(name='дауби', help='Остановать/Продолжить')
async def pause_resume(ctx):
    global play_flag
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        play_flag = False
        voice_client.pause()
    elif voice_client.is_paused():
        play_flag = True
        voice_client.resume()
    else:
        await ctx.send("`а я и не пою`")


@bot.command(name='другую', help='Включить следущую')
async def next_track(ctx):
    global queue
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await ctx.send('**да есть же**')
        voice_client.stop()
    else:
        await ctx.send('**В очереди нет треков**')


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
        queue_msg = queue_msg.replace("', '", '\n-')
        queue_msg = queue_msg.replace("['", '-').replace("']", '')
        queue_msg = queue_msg.replace('_', ' ').replace('.webm', '')
        await ctx.send(queue_msg)
    else:
        queue_msg = '**В очереди нет треков**'
        await ctx.send(queue_msg)

dotenv.load_dotenv('.env')
TOKEN = os.getenv('TOKEN')

if __name__ == "__main__":
    bot.run(TOKEN)
