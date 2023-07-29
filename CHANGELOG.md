# 3.8.0

## General

- `changelog` has been translated into English.
- Added `logging.error`

## FFmpeg Wrapper

- `ffmpeg_wrapper` module objects renamed according to PEP-8
  (`FFMpeg` to `FFmpeg`)

## Translator

- `translator.get_service_by_name` is now a valid function even if required dependencies are not installed, in which
  case if call it will raise `KeyError`

## YouTube

- dependency `pafy` added to `extra_requires/requires_yt.txt`

# 3.7.0

## General

- **Changed minimum supported Python version from 3.8 to 3.9**

## CLI

- Fixed bug with `logging.getLevelNamesMapping()` in `__main__.py`

# 3.6.0

## General

- Package `logging` used
- Bugfix
- optimization

## Audio Processing

- `sidechain` is now much faster using `ffmpeg`

## FFmpeg Wrapper

- The `ffmpeg-imageio` library is no longer used, instead the `ffmpeg` command is always called

## CLI

- Argument `--sidechain-ffmpeg-params` see [FFmpeg Documentation](https://ffmpeg.org/ffmpeg-all.html#sidechaincompress)
- Separate `--sidechain-level-sc` see `level_sc` higher.
- `-ll` is now program loglevel and ffmpeg loglevel is now `-fll`

# 3.5.2

## Translator

- Now it will not cause an error in the absence of the Internet.

## Subtitles

- Fixed possible .srt format differences (now `.` is allowed instead of `,`)

# 3.5.1

## Subtitles

- Fixed possible problems with different encodings (added `chardet` module)

# 3.5.0

## Voiceover Process

- Added argument `--export-video` (`-ev`): `BooleanOptionalAction` if `False` (`--no-export-video`, `-n-ev`)
  only exports audio

# 3.4.2

- Minor improvements and optimizations.

## Subtitles

- The `TimeLabel` class is no longer a subclass of `Line`

# 3.4.1

- Fixed documentation

# 3.4.0

## General

- Added the ability to apply a watermark to the video (see the `--watermark` argument)

## CLI

- Bugfix
- The `--watermark` argument. The text of the watermark is passed to it.
- Now, when launched from the console, the FastDub mini-banner is shown.

## Voiceover Process

- Bugfix
- Now fitted audio (which starts with '_') is always deleted as it's a temporary file

## FFmpeg Wrapper

- Added class method `FFmpegWrapper.get_video_duration_s`
  which is used in `FFmpegWrapper.get_video_duration_ms`
- The video result includes: dubbed audio, original audio, subtitles, original subtitles (if any)

## Submodules

### Translator

- The latest version of the translators module is now used

# 3.3.0

## General

- Implemented class `GlobalSettings`

## Audio Processing

- The `calc_speed_change_ffmpeg_arg` function for calculating the `-af` ffmpeg argument
  for speed change has been changed.

- Significantly accelerated using a different algorithm.

- Optimized `side_chain` function.

## Voiceover Process

- Audio length trimming and TTS are now combined into one process to increase performance.
- Now a subfolder `_result_working_dir` is created in which separate already fitted subtitle lines are saved, after
  which all parts are glued together with ffmpeg.
  Due to this, memory consumption is significantly reduced.
- `moviepy` is no longer a dependency, ffmpeg output is parsed instead

## FFmpeg Wrapper

- Now all arguments are converted to strings before calling `check_call`

# 3.2.0

## CLI

- Omitted optional `type=str` arguments.
- Changed `BooleanOptionalAction` logic, both `--no-` and `-n-` negation are now available.
- The `--cleanup-audio` argument is now `BooleanOptionalAction` (default `True`), `--cleanup-level` has been removed.
- Argument `--voice-set-anchor` (also `!:` by default).
- `--audio-format` argument for output audio (default `wav`).
- The `--sidechain` argument has been renamed to `--side-chain`.
- Added shorthand to `--traceback` argument - `-tb`.

## Voiceover Process

- Bugfix.
- Optimization of track length fitting (Fitting).

## TTS

- `anchor` argument (see `--voice-set-anchor`).
- Voice change optimization.

## Submodules

### YouTube

- When multi-loading, fully loaded videos are removed from the screen (so as not to take up space in vain).
