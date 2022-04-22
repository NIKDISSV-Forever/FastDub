Package for voice over subtitles:

* with the ability to embed in video,
* audio ducking,
* dynamic voice changer for a single track. _Add **"!: voice name"** at the beginning of the subtitle line. (Applies to
  all
  subsequent ones)_

> pip install -U [PyFastDub](https://pypi.org/project/PyFastDub/)

# Youtube support

> pip install PyFastDub[YT]

# Usage

> python -m FastDub --help

# CLI

```
usage: FastDub [-h] [-rc] [-rf CLEANUP_LEVEL] -i INPUT [-vf VIDEO_FORMAT] [-sf SUBTITLES_FORMAT] [-En EXCLUDE [EXCLUDE ...]]
               [-Eu EXCLUDE_UNDERSCORE] [-sc | --sidechain | --no-sidechain] [-sc-msl MIN_SILENCE_LEN] [-sc-st SILENCE_THRESH]
               [-sc-gdo GAIN_DURING_OVERLAY]
               [-v {microsoft irina desktop - russian,microsoft zira desktop - english united states),microsoft david desktop - english (united sta
tes,yuriy}]
               [-a ALIGN] [-ll LOGLEVEL] [-y | --confirm | --no-confirm] [-yt | --youtube | --no-youtube] [-l LANGUAGE]
               [-ak API_KEYS [API_KEYS ...]] [-pc PROCESS_COUNT]

FastDub is a tool for dubbing videos by subtitle files.

options:
  -h, --help            show this help message and exit
  -rc, --remove-cache   Remove all cache files
  -rf CLEANUP_LEVEL, --cleanup-level CLEANUP_LEVEL
                        Cleanup level   0 = No removing any files
                                > 0 remove audio from video (default)
                                > 1 = remove dubbed audio if video exists
                                > 2 = reomve dubbed cache files

Input:
  -i INPUT, --input INPUT
                        Input directory.
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
                        Gain during overlay in dB

Voicer:
  -v {microsoft irina desktop - russian,microsoft zira desktop - english (united states),microsoft david desktop - english (united states),yuriy}, 
--voice {microsoft irina desktop - russian,microsoft zira desktop - english (united states),microsoft david desktop - english (united states),yuriy
}
                        Voice
  -a ALIGN, --align ALIGN
                        Audio fit align
                                1 = right
                                2 = center (default)

FFMpeg Output:
  -ll LOGLEVEL, --loglevel LOGLEVEL
                        FFMpegWrapper loglevel
  -y, --confirm, --no-confirm
                        Don't ask for confirmation (default: True)

Youtube:
  -yt, --youtube, --no-youtube
  -l LANGUAGE, --language LANGUAGE
                        Subtitles language (ru)
  -ak API_KEYS [API_KEYS ...], --api-keys API_KEYS [API_KEYS ...]
                        Youtube API key/s
  -pc PROCESS_COUNT, --process-count PROCESS_COUNT
                        Process count to download (pass to cpu count, < 2 to disable)

```

**If the voice set after !: is not selected during voiceover, clear the cache with the -rc argument**

## Example

> python -m FastDub -i "DirToDub" -v "[Yuriy](https://rhvoice.su/downloads/?voice=yuriy&type=sapi)" --no-ducking
> --min-silence-len 200

name = "Any name"

DirToDub:

- name.srt
- name.mp4
- name2.srt
- name2.mp4

Then:
_name and name2 will be announced, and the results will be saved to a folder with the appropriate name._
