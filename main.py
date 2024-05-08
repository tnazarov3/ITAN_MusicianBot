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

music_dir = 'D:/ITAN/Download/'
vibe_dir = 'D:/ITAN/вайб/'

old_files = os.listdir(music_dir)
for fil in old_files:
    os.remove(music_dir+fil)

intents = discord.Intents().all()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='!', intents=intents)

ffmpeg_options = {'options': '-vn'}
track_id = 0

async def start_playing(voice_channel, ctx):
    global i, play_flag, dwnld_pl_flag, queue
    while True:
        if play_flag:
            try:
                print('i = ', i)
                voice_channel.play(discord.FFmpegPCMAudio(executable="ffmpeg.exe", source=queue[i]))
                track_title = f'{queue[i]}'.split(sep='/')[-1].split(sep='.')[0]
                track_title = track_title[2:] if track_title[0].isnumeric() else track_title
                await ctx.send(f'**Пою: **`{track_title}`'.replace('.webm', '').replace('_', ' '))

                await asyncio.sleep(1)
                if queue[i-1].split(sep='/')[-2] == 'Download':
                    if i > 0:
                        try:
                            os.remove(queue[i-1])
                            queue[i-1] = ''
                        except Exception as err:
                            print('>>dlt_err ', err)
                    else:
                        pass
                i += 1
            except:
                if dwnld_pl_flag:
                    print('pl dwnld started')
                    await asyncio.sleep(1)
                    global pl_urls
                    await download_playlist(pl_urls)
                else:
                    pass

            await asyncio.sleep(4)

        elif not play_flag:
            break


async def download(url, ctx, tr_id, m_dir=music_dir):
    global queue, pl_urls, first_of_pl, playlist_added_msg
    global dwnld_msg_text, added, first_added_of_pl, dwnld_pl_flag

    if '/playlist' in url:
        playlist_urls = Playlist(url)
        pl_urls = []
        for url in playlist_urls:
            pl_urls.append(url)
        first_of_pl = [pl_urls[0], f'{tr_id} ' + get_video_title(pl_urls[0])]
        try:
            YoutubeDL(set_video_name(first_of_pl[1], m_dir=m_dir)).download(pl_urls[0])
        except:
            YoutubeDL(set_video_name(f'{tr_id}_N_{tr_id}',m_dir=m_dir)).download(pl_urls[0])

        files = os.listdir(m_dir)
        for n in range(len(files)):
            if (m_dir + files[n]) not in queue:
                queue.append(m_dir + files[n])
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
        video_title_name = f'{tr_id} ' + get_video_title(url)
        YoutubeDL(set_video_name(video_title_name, m_dir=m_dir)).download(url)
        files = os.listdir(m_dir)
        for n in range(len(files)):
            if (m_dir + files[n]) not in queue:
                queue.append(m_dir + files[n])
                added = files[n][2:]
                dwnld_msg_text = f'**Добавлен: **`{added}`'.replace('.webm', '').replace('_', ' ')
            else:
                pass
        await ctx.send(dwnld_msg_text)


async def download_playlist(urls, m_dir=music_dir):
    global playlist_added_msg, queue, dwnld_pl_flag, first_added_of_pl, track_id
    dwnld_pl_flag = False
    added = []
    for url in urls[1:]:
        try:
            name = f'{track_id} ' + get_video_title(url)
            YoutubeDL(set_video_name(name, m_dir=m_dir)).download(url)
            track_id += 1

            files = os.listdir(m_dir)
            for n in range(len(files)):
                if (m_dir + files[n]) not in queue:
                    queue.append(m_dir + files[n])
                    added.append(files[n][2:])
                else:
                    pass
            if added:
                dots = '.' * (len(urls) - len(added) - 1)
                pl_append_text = f'**Плейлист добавлен**\n```-{first_added_of_pl}\n{added}\n{dots}```'
                pl_append_text = pl_append_text.replace("', '", '\n-')
                pl_append_text = pl_append_text.replace("['", '-').replace("']", '')
                pl_append_text = pl_append_text.replace('- ', '-').replace('.webm', '')
                await playlist_added_msg.edit(content=pl_append_text)
        except Exception as err:
            print('>>dwnld_playlist_err ', err)
    print('pl downloaded')


def get_video_title(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    title = soup.find('title').text
    title = title.replace('- YouTube', '').replace('/', '!').replace('|', 'I').replace('<', '%').replace('>', '%')
    title = title.replace(':', ';').replace('*', '^').replace('?', 'a').replace('"', '`').replace("\\", '!').replace('.', ' ')
    return title


def set_video_name(video_name, m_dir):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{m_dir}{video_name}.%(ext)s',
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


@bot.command(name='пой', help='Воспроизвести')
async def play_song(ctx, url):
    global queue, i, track_id, dwnld_pl_flag, play_flag
    if not ctx.message.author.voice:
        await ctx.send("{} is not connected to a voice channel".format(ctx.message.author.name))
        return
    else:
        channel = ctx.message.author.voice.channel
    try:
        await channel.connect()
    except Exception as err:
        print('>>connect_err', err)

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
            await download(url, ctx, tr_id=track_id)
            track_id += 1
        play_flag = True
        try:
            await start_playing(voice_channel, ctx)
        except Exception as err:
            print('>>play err ', err)

    except Exception as err:
        print('>>download err ', err)
        await ctx.send(f"Something went wrong - {err}")


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
    queue_next = []
    if len(queue[i:]) > 0:
        for n in queue[i:]:
            queue_next.append(n.split('/')[-1])
        queue_msg = f'**Дальше по списку: **```{queue_next}```'
        queue_msg = queue_msg.replace("', '", '\n-').replace('.mp3', '')
        queue_msg = queue_msg.replace("['", '-').replace("']", '')
        queue_msg = queue_msg.replace('_', ' ').replace('.webm', '')
        await ctx.send(queue_msg)
    else:
        queue_msg = '**В очереди нет треков**'
        await ctx.send(queue_msg)


@bot.command(name='вайб', help='+вайб')
async def play_vibe(ctx, msg='', misc_msg=''):

    import random
    global queue, i, track_id, dwnld_pl_flag, play_flag
    global vibe_list, vibe_user

    if not ctx.message.author.voice:
        await ctx.send("{} is not connected to a voice channel".format(ctx.message.author.name))
        return
    else:
        channel = ctx.message.author.voice.channel
    try:
        await channel.connect()
    except Exception as err:
        print('>>connectV_err ', err)

    try:
        queue
    except NameError:
        queue = []
        track_id = i = 0
        dwnld_pl_flag = False
    except Exception as err:
        print('>>+vibe not name err ', err)

    voice_client = ctx.message.guild.voice_client
    users = {'d1ezelll': 'И', 'dvorovoygnom': 'Т', '_zugy_': 'А', 'legendaq': 'Н'}
    vibe_user = users[f'{ctx.message.author}']

    if msg in ['И', 'Т', 'А', 'Н'] or msg == misc_msg == '':
        if msg == misc_msg == '':
            vibe_user = users[f'{ctx.message.author}']
            try:
                queue = []
                i = 0
                voice_client.stop()
            except Exception as err:
                print('>>force_vibe_err', err)
            play_flag = True
            await asyncio.sleep(0.05)
            old_files = os.listdir(music_dir)
            for fil in old_files:
                os.remove(music_dir + fil)
        else:
            vibe_user = msg

        vibe_list = os.listdir(f'{vibe_dir}{vibe_user}')
        if vibe_list:
            if misc_msg == '--стоп':
                queue[i:] = []
                try: voice_client.stop()
                except: pass

            random.shuffle(vibe_list)
            dots = '.' * len(vibe_list)
            vibe_msg_text = f'**Добавлен +вайб: **```\n{dots}```'
            vibe_added_msg = await ctx.send(vibe_msg_text)

            added = []
            for vibe in vibe_list:
                if vibe not in queue:
                    queue.append(vibe_dir + vibe_user + '/' + vibe)
                    added.append(vibe)
                else:
                    pass

                if added:
                    dots = '.' * (len(vibe_list) - len(added))
                    pl_append_text = f'**Добавлен +вайб:**\n```{added}\n{dots}```'
                    pl_append_text = pl_append_text.replace("', '", '\n-')
                    pl_append_text = pl_append_text.replace("['", '-').replace("']", '')
                    pl_append_text = pl_append_text.replace('- ', '-').replace('.mp3', '')
                    await vibe_added_msg.edit(content=pl_append_text)

            play_flag = True
            try:
                await start_playing(voice_client, ctx)
            except Exception as err:
                print('>>playV err ', err)

        elif not vibe_list:
            await ctx.send('**В этом плейлисте нет треков**')

    elif msg == '+' and 'http' in misc_msg:
        vibe_list = os.listdir(f'{vibe_dir}{vibe_user}/')
        nn = []
        for n in vibe_list:
            nn.append(int(n[0:1].strip()))
        try:
            _id = max(nn) + 1
        except:
            _id = 0

        try:
            await download(misc_msg, ctx, m_dir=f'{vibe_dir}{vibe_user}/', tr_id=_id)
        except Exception as err:
            print('>>vibe dwnld err ', err)

    elif msg == '?':
        global vibe_user_list
        vibe_user_list = str(os.listdir(vibe_dir + vibe_user + '/'))

        if vibe_user_list == '[]':
            vibe_user_list = 'В вашем плейлисте нет треков'

        vibe_user_list = vibe_user_list.replace("', '", '\n-')
        vibe_user_list = vibe_user_list.replace("['", '-').replace("']", '')
        vibe_user_list = vibe_user_list.replace('_', ' ')

        await ctx.send(f'```{vibe_user_list}```')

    elif msg == '-' and misc_msg.isnumeric():
        vibe_user_list = os.listdir(f'{vibe_dir}{vibe_user}/')
        try:
            misc_music_deleted = vibe_user_list[int(misc_msg)]
            os.remove(f'{vibe_dir}{vibe_user}/{vibe_user_list[int(misc_msg)]}')
            await ctx.send(f'`Удалено {misc_music_deleted}`')
        except IndexError:
            await ctx.send(f'Трек с номером `{misc_msg}` не найден\n'
                           'напишите `!вайб ?` что бы посмотреть какие треки у вас в плейлисте')
        except PermissionError:
            await ctx.send('```Остановите или переключите трек и попробуйте ещё раз```')
        except Exception as err:
            print('>>vibe-_err', err)


@bot.command(name='хелп')
async def print_help(ctx):
    await ctx.send('''
`!пой {url}` **- воспроизвести/добавить в очередь**
`!другую` **- некст**
`!яколян` **- стоп воспроизведения и очистка очереди**
`!очередь` **- очередь**
`!п` **- пауза/продолжить**
_____________________________________________________
_____________________________________________________

`!вайб` **- воспроизвести ваш перемешанный плейлист**
`!вайб [И Т А Н] (--стоп)` **- добавить в очередь чужой плейлист** *(`--` - остановив текущую очередь)*
`!вайб + {url}` **- скачать и добавить трек в свой плейлист**
`!вайб ?` **- посмотреть треки в своём плейлисте**
`!вайб - {номер}` **- удалить трек под этим номером** *(`!вайб ?`)*
''')

dotenv.load_dotenv('D:/Users/tortm/PyProjects/ITAN_MusicianBot/.env')
TOKEN = os.getenv('TOKEN')

if __name__ == "__main__":
    bot.run(TOKEN)
