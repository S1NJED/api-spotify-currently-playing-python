import requests, json
from discord_webhook import DiscordWebhook, DiscordEmbed
from time import sleep
from datetime import datetime

TOKEN = "" #
HEADERS = {
    'Accept':'application/json',
    'Content-Type':'application/json',
    'Authorization':f'Bearer {TOKEN}'
}

def refresh_token(): # get new token after the ancient expired (every hour)
    url = 'https://accounts.spotify.com/api/token'
    s = requests.Session()

    REFRESH_TOKEN = "" # YOUR REFRESH TOKEN HERE
    PARAMS = {
        'client_id':'', # YOUR CLIENT-ID HERE
        'client_secret':'', # YOUR SECRET CLIENT-ID HERE
        'grant_type':'refresh_token',
        'code':'', # your code. tutorial below 
        'refresh_token':REFRESH_TOKEN
    }
    
    """
    Tutorial how to get a 'code' for your parameters:
    
    https://accounts.spotify.com/authorize?response_type=code&client_id=<YOUR_CLIENT_ID>&scope=user-read-currently-playing&user-modify-playback-state&redirect_uri=<YOUR_CALLBACK_URL_IN_URL-ENCODED_FORMAT>
    
    Click to this link and check in the new url your 'code', i am sure that this is not the right way to do it, but it works lol
    """
    
    HEADERS = {
        'Content-Type':'application/x-www-form-urlencoded'
    }

    r = s.post(url, params=PARAMS, headers=HEADERS)
    res = json.loads(r.text)
    s.close()
    return res['access_token']

def convert(ms):
    if len(str(ms)) >= 4:
        div = 1000
    elif len(str(ms)) < 4:
        div = 100
    millis= ms
    millis = int(millis)
    seconds=(millis/div)%60
    seconds = int(seconds)
    minutes=(millis/(div*60))%60
    minutes = int(minutes)
    if len(str(minutes)) >= 1 and len(str(seconds)) == 1:
        return f"{minutes}:0{seconds}"
    elif len(str(minutes)) >= 1 and len(str(seconds)) == 2:
        return f"{minutes}:{seconds}"
    elif len(str(minutes)) == 0 and len(str(seconds)) == 1:
        return f'00:0{seconds}'
    elif len(str(minutes)) == 0 and len(str(seconds)) == 2:
        return f'00:{seconds}'


def main():
    current_song = ''
    
    while True:
        r = requests.get(url='https://api.spotify.com/v1/me/player/currently-playing', headers=HEADERS)
        if r.status_code == 200:
            try:
                code = r.json()

                artist = code['item']['artists'][0]['name']
                #print(f"Artiste: {artist}")

                titre = code['item']['name']
                #print(f"Titre: {titre}")
                #print(f"{titre} - {artist}")

                link = code['item']['external_urls']['spotify']
                #print(f"Link: {link}")

                thumbnail = code['item']['album']['images'][2]['url']
                #print(f"Thumbnail: {thumbnail}")

                duration_ms = code['item']['duration_ms']
                progress_ms = code['progress_ms']
                #print(f"00:00 ━━⬤──── {convert(duration_ms)}")

                global TOKEN
                if current_song != titre:
                    current_song = titre
                    url = '' # webhook url
                    webhook = DiscordWebhook(url=url, rate_limit_retry=True)
                    embed = DiscordEmbed(description=f'[**{titre} - {artist}**]({link})\n\n{convert(progress_ms)} ━━⬤──── {convert(duration_ms)}\n\n:calendar_spiral: <t:{int(datetime.now().timestamp())}:f>', color=0x5EE922)
                    embed.set_thumbnail(url=thumbnail)
                    webhook.add_embed(embed)
                    webhook.execute()
                    sleep(4)
                else: # notif already sent.
                    sleep(4)
            except:
                pass
        elif r.status_code == 401: # no functionnal token provided
            HEADERS.update({'Authorization':f'Bearer {refresh_token()}'})
            sleep(4)
        elif r.status_code == 204: # no song playing
            sleep(30)
        else:
            # print(f'Error ({r.status_code})')
            sleep(30)

if __name__ == '__main__':
    main()
