from discord.ext import commands
from bs4 import BeautifulSoup
from yt_dlp import YoutubeDL
from pytube import Playlist
import requests
import discord
import asyncio
import dotenv
import os

global queue, i, video_title_name, playlist_added_msg, first_added_of_pl, pl_urls, track_id
global play_flag, dwnld_pl_flag

music_dir = 'D:/ITAN/'

old_files = os.listdir(music_dir)
for fil in old_files:
    os.remove(music_dir+fil)

intents = discord.Intents().all()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='!', intents=intents)

ffmpeg_options = {'options': '-vn'}


@bot.command(name='пой', help='Воспроизвести')
async def play_song(ctx, url):
    global queue, i, track_id, dwnld_pl_flag, play_flag
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
        track_id = i = 0
        dwnld_pl_flag = False

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
        await ctx.send(f"Somenthing went wrong - {err}")


async def start_playing(voice_channel, ctx):
    global i, play_flag, dwnld_pl_flag, queue
    while True:
        if play_flag:
            try:
                voice_channel.play(discord.FFmpegPCMAudio(executable="ffmpeg.exe", source=music_dir + queue[i]))
                await ctx.send(f'**Пою: **`{queue[i][2:]}`'.replace('.webm', '').replace('_', ' '))
                try:
                    os.remove(music_dir + queue[i-1])
                    queue[i-1] = ''
                except: pass
                i += 1
            except:
                if dwnld_pl_flag:
                    print('pl dwnld started')
                    await asyncio.sleep(1)
                    global pl_urls
                    await download_playlist(pl_urls)
                else: pass

            await asyncio.sleep(3)

        elif not play_flag:
            break


async def download(url, ctx):
    global queue, pl_urls, first_of_pl, playlist_added_msg
    global dwnld_msg_text, added, first_added_of_pl, dwnld_pl_flag, track_id

    if '/playlist' in url:
        playlist_urls = Playlist(url)
        pl_urls = []
        for url in playlist_urls:
            pl_urls.append(url)
        print(pl_urls)
        first_of_pl = [pl_urls[0], f'{track_id} ' + get_video_title(pl_urls[0])]
        YoutubeDL(set_video_name(first_of_pl[1])).download(pl_urls[0])
        track_id += 1

        files = os.listdir(music_dir)
        for n in range(len(files)):
            if files[n] not in queue:
                queue.append(files[n])
                first_added_of_pl = files[n][2:]
            else:
                pass
        dots = '.' * len(pl_urls)
        dwnld_msg_text_pl = f'**Добавлен плейлист: **```\n-{first_added_of_pl}\n{dots}```'
        dwnld_msg_text_pl = dwnld_msg_text_pl.replace('.webm', '').replace('_', ' ')
        playlist_added_msg = await ctx.send(dwnld_msg_text_pl)
        dwnld_pl_flag = True

    else:
        added = None
        video_title_name = f'{track_id} ' + get_video_title(url)
        YoutubeDL(set_video_name(video_title_name)).download(url)
        track_id += 1
        files = os.listdir(music_dir)
        for n in range(len(files)):
            if files[n] not in queue:
                queue.append(files[n])
                added = files[n][2:]
                dwnld_msg_text = f'**Добавлен: **`{added}`'.replace('.webm', '').replace('_', ' ')
            else:
                pass
        await ctx.send(dwnld_msg_text)

    old_files = os.listdir(music_dir)
    for fil in old_files:
        if fil not in queue:
            try:
                os.remove(music_dir + fil)
            except:
                pass


async def download_playlist(urls):
    global playlist_added_msg, queue, dwnld_pl_flag, first_added_of_pl, track_id
    dwnld_pl_flag = False
    added = []
    for url in urls[1:]:
        try:
            name = f'{track_id} ' + get_video_title(url)
            YoutubeDL(set_video_name(name)).download(url)
            track_id += 1

            files = os.listdir(music_dir)
            for n in range(len(files)):
                if files[n] not in queue:
                    queue.append(files[n])
                    added.append(files[n][2:])
                else:
                    pass
            if added:
                dots = '.' * (len(urls) - len(added) - 1)
                text = f'**Плейлист добавлен**\n```-{first_added_of_pl}\n{added}\n{dots}```'
                text = text.replace("', '", '\n-')
                text = text.replace("['", '-').replace("']", '')
                text = text.replace('- ', '-').replace('.webm', '')
                await playlist_added_msg.edit(content=text)
        except Exception as err: print('1 ', err)
    print('pl dwnlded')


def get_video_title(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    title = soup.find('title').text
    title = title.replace('- YouTube', '')
    return title


def set_video_name(video_name):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{music_dir}{video_name.title()}.%(ext)s',
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


@bot.command(name='п', help='Остановать/Продолжить')
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
    try:
        queue[i] = queue[i]
        if voice_client.is_playing():
            await ctx.send('**да есть же**')
            voice_client.stop()
    except IndexError:
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

    old_tracks = os.listdir(music_dir)
    for track in range(len(old_tracks)):
        os.remove(music_dir + old_tracks[track])


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

dotenv.load_dotenv('C:/Users/tortm/PyProjects/ITAN_MusicianBot/.env')
TOKEN = os.getenv('TOKEN')

if __name__ == "__main__":
    bot.run(TOKEN)
