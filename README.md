Package for voice over subtitles:

* with the ability to embed in video,
* audio ducking,
* dynamic voice changer for a single track. _Add **"!: voice name"** at the beginning of the subtitle line. (Applies to
  all
  subsequent ones)_

> pip install -U [PyFastDub](https://pypi.org/project/PyFastDub/)

> python -m FastDub --help

# CLI

```
usage: FastDub [-h] -i INPUT [-vf VIDEO_FORMAT] [-sf SUBTITLES_FORMAT] [-En EXCLUDE [EXCLUDE ...]] [-Eu EXCLUDE_UNDERSCORE]
               [--ducking | --no-ducking] [--min-silence-len MIN_SILENCE_LEN] [--silence-thresh SILENCE_THRESH]
               [--gain-during-overlay GAIN_DURING_OVERLAY]
               [-v {...}]
               [-a ALIGN] [-ll LOGLEVEL] [-y] [-rf CLEANUP_LEVEL] [-rc]

FastDub is a tool for dubbing videos by subtitle files.

options:
  -h, --help            show this help message and exit
  -rc, --remove-cache   Remove all cache files

Input:
  -i INPUT, --input INPUT
                        Input file or directory.
  -vf VIDEO_FORMAT, --video-format VIDEO_FORMAT
                        Video format (default .mp4).
  -sf SUBTITLES_FORMAT, --subtitles-format SUBTITLES_FORMAT
                        Subtitles format (default .srt).

Audio Ducking:
  -dk, --ducking, --no-ducking
                        Enable audio ducking (default: True)
  -dk-msl MIN_SILENCE_LEN, --min-silence-len MIN_SILENCE_LEN
                        Minimum silence length in ms (default 100)
  -dk-st SILENCE_THRESH, --silence-thresh SILENCE_THRESH
                        Silence threshold in dB
  -dk-gdo GAIN_DURING_OVERLAY, --gain-during-overlay GAIN_DURING_OVERLAY
                        Gain during overlay in dB

Voicer:
  -v {microsoft irina desktop - russian,microsoft zira desktop - english (united states),microsoft david desktop - english (united states),yuriy}, 
--voice {microsoft irina desktop - russian,microsoft zira desktop - english (united states),microsoft david desktop - english (united states),yuriy
}
                        Voice
  -a ALIGN, --align ALIGN
                        Audio fit align
                                1 = right
                                2 = center

Output:
  -ll LOGLEVEL, --loglevel LOGLEVEL
                        FFMpegWrapper loglevel
  -y, --yes             Don't ask for confirmation
  -rf CLEANUP_LEVEL, --cleanup-level CLEANUP_LEVEL
                        Cleanup level (0 = No removing any files
                                > 0 remove audio from video (default)
                                > 1 = remove dubbed audio if video exists)
                                > 2 = reomve dubbed cache files

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
