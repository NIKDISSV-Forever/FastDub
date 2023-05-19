Package for voice over subtitles:

* with the ability to embed in video,
* audio ducking,
* dynamic voice changer for a single track. _Add **--voice-set-anchor** at the beginning of the subtitle line. (Applies
  to
  all
  subsequent ones)_

> pip install -U [FastDub](https://pypi.org/project/FastDub/)

---

# Install for Ubuntu

> sudo apt update -y && sudo apt upgrade -y
>
> sudo apt install python3 python3-pip ffmpeg [espeak](http://espeak.sourceforge.net/data/) libxml2-dev libxslt1-dev
>
> ; libxml for translator functions
>
> sudo python3 -m pip install -U pip setuptools wheel
>
> sudo python3 -m pip install -U [FastDub](https://pypi.org/project/FastDub/)

# Install all dependencies

> pip install FastDub[ALL]  # default

# Youtube support

## Youtube argument group

> pip install FastDub[YT]

### Process all videos from a channel

_To get the channel id if it only has a username, run the JS code in the browser console:_

```javascript
document.querySelector("body>link").href
```

**Then, in the input parameter,
you can pass a link to the channel (with an id, not with a username) or a string of the format "c/CHANNEL_ID"**

_For example:_

> python -m fastdub -i "c/[UCi-5OZ2tYuwMLIcEyOsbdRA](https://www.youtube.com/channel/UCi-5OZ2tYuwMLIcEyOsbdRA)" -yt

## YouTube Search argument group

That the input data was a request to YouTube, they must begin with "?".

_For Example:_

> python -m fastdub -i "?#python" -yt -yts-l 5

## YouTube Upload argument group

> pip install FastDub[YTU]

To download, you need to go to [credentials](https://console.cloud.google.com/apis/credentials) (Create a new project if
needed) > <kbd>+ Create credentials</kbd> > <kbd>OAuth Client ID</kbd> > <kbd>Desktop App</kbd>

After filling in the required fields, <kbd>DOWNLOAD JSON</kbd> format and save to a working folder under the name
_client_secrets.json_

* Specifying the -ytu-ps argument as non-private may result in processing errors, but this was not observed during
  testing.

* Please note that video uploads require a large amount of [quota](https://console.cloud.google.com/iam-admin/quotas) (
  default has 10,000 per day)

# Subtitles translate

### Translate argument group

> pip install FastDub[TR]

# Usage

> python -m fastdub --help

```
usage: fastdub [-h] [-rc {0,1,2}] [-ra | --cleanup-audio | -n-ra | --no-cleanup-audio] [-ev | --export-video | -n-ev | --no-export-video]
               [-l LANGUAGE] [-tc THREADS_COUNT] -i INPUT [-vf VIDEO_FORMAT] [-sf SUBTITLES_FORMAT] [-En EXCLUDE [EXCLUDE ...]]
               [-Eu EXCLUDE_UNDERSCORE] [-sc | --sidechain | -n-sc | --no-sidechain] [-sc-args SIDECHAIN_FFMPEG_PARAMS]
               [-sc-lvl SIDECHAIN_LEVEL_SC]
               [-v {microsoft irina desktop - russian,microsoft zira desktop - english united states),microsoft david desktop - english (united s
tates,aleksandr-hq,arina,artemiy,evgeniy-eng,evgeniy-rus,lyubov,marianna,mikhail,pavel,tatiana,victoria,vitaliy,volodymyr,vsevolod,yuriy}]       
               [-a ALIGN] [-v-set-a VOICE_SET_ANCHOR] [-ll {trace,debug,verbose,info,warning,error,fatal,panic,quiet}]
               [-y | --confirm | -n-y | --no-confirm] [-af AUDIO_FORMAT] [-wm WATERMARK] [-tb | --traceback | -n-tb | --no-traceback] [-yt]      
               [-ak API_KEYS [API_KEYS ...]] [-yts] [-yts-l YOUTUBE_SEARCH_LIMIT] [-yts-rg YOUTUBE_SEARCH_REGION] [-ytu]
               [-ytu-ps {private,public,unlisted}] [-ytu-t] [-tr] [--rewrite-srt | --no-rewrite-srt]
               [-ts {alibaba,apertium,argos,baidu,bing,caiyun,cloudYi,deepl,elia,google,iciba,iflytek,iflyrec,itranslate,judic,languageWire,lingv
anex,niutrans,mglip,modernMt,myMemory,papago,qqFanyi,qqTranSmart,reverso,sogou,sysTran,tilde,translateCom,translateMe,utibet,volcEngine,yandex,ye
ekit,youdao}]

fastdub is a tool for dubbing videos by subtitle files.

options:
  -h, --help            show this help message and exit
  -rc {0,1,2}, --remove-cache {0,1,2}
                        Remove all cache (_cached_texts directory) files
                                0 - No remove cache
                                1 - Delete cache before voice acting
                                2 - Delete cache after voice acting (default)
  -ra, --cleanup-audio, -n-ra, --no-cleanup-audio
                        Remove result audio if video exists (default True) (default: True)
  -ev, --export-video, -n-ev, --no-export-video
  -l LANGUAGE, --language LANGUAGE
                        Subtitles language (ru)
  -tc THREADS_COUNT, --threads-count THREADS_COUNT
                        Process count to download (pass to cpu count, < 2 to disable)
                                *N = N * cpu count

Input:
  -i INPUT, --input INPUT
                        Input directory/YouTube Playlist/Video URL.
  -vf VIDEO_FORMAT, --video-format VIDEO_FORMAT
                        Video format (default: .mp4).
  -sf SUBTITLES_FORMAT, --subtitles-format SUBTITLES_FORMAT
                        Subtitles format (default: .srt).

Input Exclude:
  -En EXCLUDE [EXCLUDE ...], --exclude EXCLUDE [EXCLUDE ...]
                        Exclude <name> (glob)
  -Eu EXCLUDE_UNDERSCORE, --exclude-underscore EXCLUDE_UNDERSCORE
                        Exclude files starts with underscore

Audio Ducking:
  -sc, --sidechain, -n-sc, --no-sidechain
                        Enable audio side chain compress (ducking) (default: True)
  -sc-args SIDECHAIN_FFMPEG_PARAMS, --sidechain-ffmpeg-params SIDECHAIN_FFMPEG_PARAMS
                        sidechain FFMpeg parameters (default '')
  -sc-lvl SIDECHAIN_LEVEL_SC, --sidechain-level-sc SIDECHAIN_LEVEL_SC
                        Set sidechain gain. Range is between 0.015625 and 64. (default 0.8)

Voicer:
  -v {microsoft irina desktop - russian,microsoft zira desktop - english (united states),microsoft david desktop - english (united states),aleksa
ndr-hq,arina,artemiy,evgeniy-eng,evgeniy-rus,lyubov,marianna,mikhail,pavel,tatiana,victoria,vitaliy,volodymyr,vsevolod,yuriy}, --voice {microsoft
 irina desktop - russian,microsoft zira desktop - english (united states),microsoft david desktop - english (united states),aleksandr-hq,arina,ar
temiy,evgeniy-eng,evgeniy-rus,lyubov,marianna,mikhail,pavel,tatiana,victoria,vitaliy,volodymyr,vsevolod,yuriy}
                        SAPI voice for voice acting.
  -a ALIGN, --align ALIGN
                        Audio fit align (divisor)
                                1 = right
                                2 = center (default)
  -v-set-a VOICE_SET_ANCHOR, --voice-set-anchor VOICE_SET_ANCHOR
                        Anchor indicating voice actor change (default "!:")

FFMpeg Output:
  -ll {trace,debug,verbose,info,warning,error,fatal,panic,quiet}, --loglevel {trace,debug,verbose,info,warning,error,fatal,panic,quiet}
                        FFMpegWrapper loglevel
  -y, --confirm, -n-y, --no-confirm
                        Don't ask for confirmation (default: True)
  -af AUDIO_FORMAT, --audio-format AUDIO_FORMAT
                        Out audio files format (default wav)
  -wm WATERMARK, --watermark WATERMARK
                        Add watermark to output video

Terminal Output:
  -tb, --traceback, -n-tb, --no-traceback
                        Show debug traceback (default: False)

YouTube:
  -yt, --youtube
  -ak API_KEYS [API_KEYS ...], --api-keys API_KEYS [API_KEYS ...]
                        Youtube API key/s

YouTube Search:
  -yts, --youtube-search
                        The input data is a query for searching on YouTube. (Adds "?" at the start of input)
  -yts-l YOUTUBE_SEARCH_LIMIT, --youtube-search-limit YOUTUBE_SEARCH_LIMIT
                        Sets limit to the number of results. Defaults to 20.
  -yts-rg YOUTUBE_SEARCH_REGION, --youtube-search-region YOUTUBE_SEARCH_REGION
                        Sets the result region. Defaults to "US".

YouTube Upload:
  -ytu, --youtube-upload
                        yt_upload video to YouTube channel after voice acting.
  -ytu-ps {private,public,unlisted}, --privacy-status {private,public,unlisted}
                        Video privacy status (If not private, errors are possible)
  -ytu-t, --youtube-upload-translate
                        Translate title and description on upload. (+ Arguments from translate argument group)

Translate:
  -tr, --translate      Translate input subtitles files
  --rewrite-srt, --no-rewrite-srt
                        Rewrite input subtitles files.
                        If not, add "_" to the beginning of the original subtitle file. (default: False)
  -ts {alibaba,apertium,argos,baidu,bing,caiyun,cloudYi,deepl,elia,google,iciba,iflytek,iflyrec,itranslate,judic,languageWire,lingvanex,niutrans,
mglip,modernMt,myMemory,papago,qqFanyi,qqTranSmart,reverso,sogou,sysTran,tilde,translateCom,translateMe,utibet,volcEngine,yandex,yeekit,youdao}, 
--translate-service {alibaba,apertium,argos,baidu,bing,caiyun,cloudYi,deepl,elia,google,iciba,iflytek,iflyrec,itranslate,judic,languageWire,lingv
anex,niutrans,mglip,modernMt,myMemory,papago,qqFanyi,qqTranSmart,reverso,sogou,sysTran,tilde,translateCom,translateMe,utibet,volcEngine,yandex,ye
ekit,youdao}
                        Subtitle translation service. (default google)
```

**If the voice set after "!:" is not selected during voiceover, clear the cache with the -rc argument**

## Example

> python -m fastdub -i DirToDub -v "[Yuriy](https://rhvoice.su/downloads/?voice=yuriy&type=sapi)" --no-sidechain -sf vtt
> -vf mkv

All files in the folder will be voices (*.mkv, *.vtt)

Default is mp4 video and srt subtitles.

Then:
_name and name2 will be announced, and the results will be saved to a folder with the appropriate name._

## YT Example

> python -m fastdub **-yt** -i https://youtu.be/DD5UKQggXTc
> -v "[Yuriy](https://rhvoice.su/downloads/?voice=yuriy&type=sapi)"
> -l ru

### YouTube Search Example

> python -m fastdub -yt **-yts** -i "#annoyingorange" -l ru

## Translate Example

> python -m fastdub -i DirToDub -tr **-ts iciba** _-l [ru](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes)_

Default service is Google.

## Other

### The `fastdub.utils` module stores helper functions.

### python -m pydoc -w fastdub

### You can write your issues on [GitHub](https://github.com/NIKDISSV-Forever/fastdub/issues) in English or in Russian.
