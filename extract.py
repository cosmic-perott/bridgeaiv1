import yt_dlp

def download_mp3(youtube_url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'audio',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': False,  # set to True to suppress output
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])
