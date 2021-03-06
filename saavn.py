from pyrogram import filters, types, Client
from pyrogram.types import Message,ForceReply
import wget
import os
import json
import requests
app = Client(
    ":memory:",
    bot_token="5215408911:AAGbY_nVChtSd4w-3cYkzwaTzN9tEg71jb4",
    api_id=15046785,
    api_hash="bbe87b697e24c7fb868272d8361d90ea",
)
curr_user=None
search_base_url = "https://www.jiosaavn.com/api.php?__call=autocomplete.get&_format=json&_marker=0&cc=in&includeMetaTags=1&query="
song_details_base_url = "https://www.jiosaavn.com/api.php?__call=song.getDetails&cc=in&_marker=0%3F_marker%3D0&_format=json&pids="
lyrics_base_url = "https://www.jiosaavn.com/api.php?__call=lyrics.getLyrics&ctx=web6dot0&api_version=4&_format=json&_marker=0%3F_marker%3D0&lyrics_id="

@app.on_message(filters.command("saavn") & filters.group & ~filters.edited)
async def saavn(_,message:Message):
    global curr_user,songs
    songs = []
    search = message.text.split(None, 2)[1:]
    search_url=search_base_url+ str(search)
    response = requests.get(search_url).text.encode().decode('unicode-escape')
    response = json.loads(response)
    song_resp = response['songs']['data']
    for song in song_resp:
        idl = song['id']
        song_details_url = song_details_base_url+idl
        song_resp = requests.get(song_details_url).text.encode().decode('unicode-escape')
        song_resp = json.loads(song_resp)
        data = song_resp[idl]
        try:
            url = (data['media_preview_url'])
            url = url.replace("preview", "aac")
            if data['320kbps']=="true":
                url = url.replace("_96_p.mp4", "_320.mp4")
            else:
                url = url.replace("_96_p.mp4", "_160.mp4")
            data['media_url'] = url
            try:
             data['song']= format(data['song']).replace('&quot;','')
            except:
             data['song'] = format(data['song'])
            data['music'] = format(data['music'])
            try:
             data['singers']= format(data['singers']).replace('&quot;','')
            except:
             data['singers'] = format(data['singers'])
            data['starring'] = format(data['starring'])
            data['album'] = format(data['album'])
            data["primary_artists"] = format(data["primary_artists"])
            data['image'] = data['image'].replace("150x150","500x500")
            songs.append(data)
        except:
            pass
    s_list='**Choose a song number to Download:**'
    for i,lis in enumerate(songs):
        a=f"{str(i+1)} - {lis['song']} from {lis['album']} by {lis['singers']}"
        s_list='\n'.join((s_list,a))
    m= await message.reply_text(
        text=f'{s_list}',
        reply_markup=ForceReply(True))
    curr_user= message.from_user.id
    
@app.on_message(filters.group)
async def send(_,message:Message):
    global curr_user,songs
    try:
        if (len(songs)+1)>= int(message.text):
            m = await message.reply_text(f"On the way **{songs[int(message.text)-1]['song']} by {songs[int(message.text)-1]['singers']}**")
            file= wget.download(songs[int(message.text)-1]['media_url'])
            ffile = file.replace("mp4", "m4a")
            os.rename(file, ffile)
            await message.reply_audio(audio=ffile, title=songs[int(message.text)-1]['song'], performer=songs[int(message.text)-1]['singers'])
            os.remove(ffile)
            await m.delete()
            curr_user=None
            songs=[]
    except Exception as e:
        print(e)
        songs=[]
        curr_user=None
app.run()
