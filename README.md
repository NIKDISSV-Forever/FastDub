Package for voice over subtitles:

* with the ability to embed in video,
* audio ducking,
* dynamic voice changer for a single track. _Add **"!: voice name"** at the beginning of the subtitle line. (Applies to
  all
  subsequent ones)_

> pip install -U [PyFastDub](https://pypi.org/project/PyFastDub/)

# Install all dependencies

> pip install PyFastDub[ALL]

# Youtube support

## Youtube argument group

> pip install PyFastDub[YT]

### Process all videos from a channel

_To get the channel id if it only has a username, run the JS code in the browser console:_

```javascript
document.querySelector("body>link").href
```

**Then, in the input parameter,
you can pass a link to the channel (with an id, not with a username) or a string of the format "c/CHANNEL_ID"**

_For example:_

> python -m FastDub -i "c/[UCi-5OZ2tYuwMLIcEyOsbdRA](https://www.youtube.com/channel/UCi-5OZ2tYuwMLIcEyOsbdRA)" -yt

## YouTube Search argument group

> pip install PyFastDub[YTS]

That the input data was a request to YouTube, they must begin with "?".

_For Example:_

> python -m FastDub -i "?#python" -yt -yts-l 5

## YouTube Upload argument group

> pip install PyFastDub[YTU]

To download, you need to go to [credentials](https://console.cloud.google.com/apis/credentials) (Create a new project if
needed) > <kbd>+ Create credentials</kbd> > <kbd>OAuth Client ID</kbd> > <kbd>Desktop App</kbd>

After filling in the required fields, <kbd>DOWNLOAD JSON</kbd> format and save to a working folder under the name
_client_secrets.json_

* Specifying the -ytu-ps argument as non-private may result in processing errors, but this was not observed during
  testing.

* Please note that video uploads require a large amount of quota (default has 10,000 per day)

# Subtitles translate

### Translate subtitles argument group

> pip install PyFastDub[TR]

# Usage

> python -m FastDub --help

```
usage: FastDub [-h] [-rc {0,1,2}] [-rf CLEANUP_LEVEL] [-l LANGUAGE] [-tc THREADS_COUNT] [-i INPUT] [-vf VIDEO_FORMAT] [-sf SUBTITLES_FORMAT]
               [-En EXCLUDE [EXCLUDE ...]] [-Eu EXCLUDE_UNDERSCORE] [-sc | --sidechain | --no-sidechain] [-sc-msl MIN_SILENCE_LEN] [-sc-st SILENCE_THRESH]
               [-sc-gdo GAIN_DURING_OVERLAY]
               [-v {microsoft irina desktop - russian,microsoft zira desktop - english united states),microsoft david desktop - english (united states,aleksandr-hq,
arina,artemiy,evgeniy-eng,evgeniy-rus,lyubov,marianna,mikhail,pavel,tatiana,victoria,vitaliy,volodymyr,yuriy}]
               [-a ALIGN] [-ll {trace,debug,verbose,info,warning,error,fatal,panic,quiet}] [-y | --confirm | --no-confirm] [-yt] [-ak API_KEYS [API_KEYS ...]]      
               [-yts] [-yts-l YOUTUBE_SEARCH_LIMIT] [-yts-rg YOUTUBE_SEARCH_REGION] [-tr] [--rewrite-srt | --no-rewrite-srt]
               [-ts {alibaba,argos,baidu,bing,caiyun,deepl,google,iciba,iflytek,itranslate,papago,reverso,sogou,tencent,translateCom,utibet,yandex,youdao}]

FastDub is a tool for dubbing videos by subtitle files.

options:
  -h, --help            show this help message and exit
  -rc {0,1,2}, --remove-cache {0,1,2}
                        Remove all cache (_cached_texts directory) files
                                0 - No remove cache
                                1 - Delete cache before voice acting
                                2 - Delete cache after voice acting (default)
  -rf CLEANUP_LEVEL, --cleanup-level CLEANUP_LEVEL
                        Cleanup level   0 = No removing any files
                                > 0 remove audio from video (default)
                                > 1 = remove dubbed audio if video exists
                                > 2 = reomve dubbed cache files
  -l LANGUAGE, --language LANGUAGE
                        Subtitles language (ru)
  -tc THREADS_COUNT, --threads-count THREADS_COUNT
                        Process count to download (pass to cpu count, < 2 to disable)
                                *N = N * cpu count

Input:
  -i INPUT, --input INPUT
                        Input directory/YouTube Playlist/Video URL.
  -vf VIDEO_FORMAT, --video-format VIDEO_FORMAT
                        Video format (default .mp4).
  -sf SUBTITLES_FORMAT, --subtitles-format SUBTITLES_FORMAT
                        Subtitles format (default .srt).

Audio Ducking:
  -sc, --sidechain, --no-sidechain
                        Enable audio side chain compress (ducking) (default: True)
  -sc-msl MIN_SILENCE_LEN, --min-silence-len MIN_SILENCE_LEN, --attack MIN_SILENCE_LEN
                        Minimum silence length in ms (default 100)
  -sc-st SILENCE_THRESH, --silence-thresh SILENCE_THRESH
                        Silence threshold in dB
  -sc-gdo GAIN_DURING_OVERLAY, --gain-during-overlay GAIN_DURING_OVERLAY
                        Gain during overlay in dB (-11)

Voicer:
  -v {microsoft irina desktop - russian,microsoft zira desktop - english (united states),microsoft david desktop - english (united states),aleksandr-hq,arina,artemi
y,evgeniy-eng,evgeniy-rus,lyubov,marianna,mikhail,pavel,tatiana,victoria,vitaliy,volodymyr,yuriy}, --voice {microsoft irina desktop - russian,microsoft zira desktop
 - english (united states),microsoft david desktop - english (united states),aleksandr-hq,arina,artemiy,evgeniy-eng,evgeniy-rus,lyubov,marianna,mikhail,pavel,tatian
a,victoria,vitaliy,volodymyr,yuriy}
                        SAPI voice for voice acting.
  -a ALIGN, --align ALIGN
                        Audio fit align
                                1 = right
                                2 = center (default)

FFMpeg Output:
  -ll {trace,debug,verbose,info,warning,error,fatal,panic,quiet}, --loglevel {trace,debug,verbose,info,warning,error,fatal,panic,quiet}
                        FFMpegWrapper loglevel
  -y, --confirm, --no-confirm
                        Don't ask for confirmation (default: True)

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

Translate subtitles:
  -tr, --translate      Translate input subtitles files
  --rewrite-srt, --no-rewrite-srt
                        Rewrite input subtitles files.
                        If not, add "_" to the beginning of the original subtitle file. (default: False)
  -ts {alibaba,argos,baidu,bing,caiyun,deepl,google,iciba,iflytek,itranslate,papago,reverso,sogou,tencent,translateCom,utibet,yandex,youdao}, --translate-service {a
libaba,argos,baidu,bing,caiyun,deepl,google,iciba,iflytek,itranslate,papago,reverso,sogou,tencent,translateCom,utibet,yandex,youdao}
                        Subtitle translation service. (default google)
```

**If the voice set after !: is not selected during voiceover, clear the cache with the -rc argument**

## Example

> python -m FastDub DirToDub -v "[Yuriy](https://rhvoice.su/downloads/?voice=yuriy&type=sapi)" --no-ducking -vf mkv

name is any name.

DirToDub:

- name.srt
- name.mkv
- name2.srt
- name2.mkv
- andit.srt
- andit.mkv

Then:
_name and name2 will be announced, and the results will be saved to a folder with the appropriate name._

## YT Example

> python -m FastDub https://youtu.be/DD5UKQggXTc **-yt**
> -v "[Yuriy](https://rhvoice.su/downloads/?voice=yuriy&type=sapi)"
> -l ru

## Translate Example

> python -m FastDub DirToDub -tr -ts iciba -l ru

### python -m pydoc -w FastDub

### You can write your issues on [GitHub](https://github.com/NIKDISSV-Forever/FastDub/) in English or in Russian.
