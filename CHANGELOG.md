---

# 02.12.2022

## CLI

- Опущены необязательные `type=str` аргументы
- Изменена логика `BooleanOptionalAction`, теперь доступно как `--no-` так и `-n-` отрицание
- Аргумент `--cleanup-audio` теперь `BooleanOptionalAction` (по умолчанию `True`), `--cleanup-level` удалён
- Аргумент `--voice-set-anchor` (по умолчанию так же `!:`)
- Аргумент `--audio-format` для выходного аудио (по умолчанию `wav`)
- Аргумент `--sidechain` переименован в `--side-chain`
- Добавлено сокращение аргументу `--traceback` - `-tb`

## Voiceover Process

- Bugfix
- Оптимизация подгона длительности дорожек (Fitting-а)

## TTS

- `anchor` аргумент (см. `--voice-set-anchor`)
- Оптимизация смены голосов

## Submodules

### YouTube

- При multi-загрузке полностью загруженные видео удаляются с экрана (чтоб не занимать зря место)
