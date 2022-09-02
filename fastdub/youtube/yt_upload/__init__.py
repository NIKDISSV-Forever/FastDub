try:
    from fastdub.youtube.yt_upload import uploader
    from fastdub.youtube.yt_upload.upload_video import VALID_PRIVACY_STATUSES
except ImportError:
    SUPPORTED = False
else:
    SUPPORTED = True
