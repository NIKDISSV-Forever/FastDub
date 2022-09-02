from pathlib import Path
from pprint import pp
from typing import Callable
from fastdub.youtube.yt_upload.upload_video import upload
from fastdub.youtube import pafy
from fastdub.youtube.downloader import with_api_key


class Uploader:
    def __init__(self,
                 privacy_status: str = 'private',
                 translate: bool = False, translate_service: Callable = None, ):
        self.translate = (
            (lambda line, lang: translate_service(line, to_language=lang))
            if translate else (lambda line, _: line))
        self.privacy = privacy_status

    def upload(self, base_dir: Path):
        names = {fn: (fn.parent.name.removesuffix('_result').removeprefix('_'), fn.stem) for fn in
                 base_dir.glob('_*_result/*.mp4')}
        for fp, (name, lang) in names.items():
            def translate(text: str) -> str:
                return self.translate(text, lang)

            title = f'{name} - {lang}'
            description = category = keywords = None
            ytdl = None
            try:
                ytdl = with_api_key(lambda: pafy.new(name))
            except (OSError, ValueError):
                pass
            if ytdl:
                title = ytdl.title
                description = ytdl.description
                keywords = ytdl.keywords
            command = ('--file', str(fp), '--title', translate(title),
                       '--privacy-status', self.privacy, '--noauth_local_webserver')
            if description:
                command += ('--description', translate(description),)
            if category:
                command += ('--category', category)
            if keywords:
                command += ('--keywords', ','.join(translate(kw) for kw in keywords))
            pp(command)
            upload(command)
