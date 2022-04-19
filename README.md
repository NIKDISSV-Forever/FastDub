Package for voice over subtitles:

* with the ability to embed in video,
* audio ducking,
* dynamic voice changer for a single track. _Add **"!: voice name"** at the beginning of the subtitle line. (Applies to all
  subsequent ones)_

> pip install [PyFastDub](https://pypi.org/project/PyFastDub/)

> python -m FastDub --help

# CLI

```
Input:
  -i INPUT, --input INPUT
                        Input file or directory.
  -vf VIDEO_FORMAT, --video-format VIDEO_FORMAT
                        Video format (default .mp4).
  -sf SUBTITLES_FORMAT, --subtitles-format SUBTITLES_FORMAT
                        Subtitles format (default .srt).

Audio Ducking:
  --ducking, --no-ducking
                        Enable audio ducking (default: True)
  --min-silence-len MIN_SILENCE_LEN
                        Minimum silence length in ms (default 100)
  --silence-thresh SILENCE_THRESH
                        Silence threshold in dB
  --gain-during-overlay GAIN_DURING_OVERLAY
                        Gain during overlay in dB

Voicer:
  -v {...}, 
--voice {...}
                        Voice
  -a ALIGN, --align ALIGN
                        Audio fit align
                                1 = right (default)
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

## Example

> python -m FastDub -i "DirToDub" -v "[Yuriy](https://rhvoice.su/downloads/?voice=yuriy&type=sapi)" --ducking
> --min-silence-len 200

name = "Any name"

DirToDub:

- name.srt
- name.mp4
- name2.srt
- name2.mp4

Then:
_name and name2 will be announced, and the results will be saved to a folder with the appropriate name._