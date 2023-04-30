# env: python3.10 pytorch+cu1.7 
# author: Lanzhijiang
# date: 2023/04/19
# description: 
#   处理视频信息，并作总结
#   1. 通过whisper对视频音频转文字，并且分句
#   2. 语意理解以分类视频

import json
import whisper

settings = json.load(open("./data/settings.json", "r"), encoding="utf-8")

class VideoProcessor:

    BASE_OUPUT_PATH = "./"

    @classmethod
    def audio_to_text(cls, audio_fp, model_id="small"):

        """
        语音转文字
        """
        model = whisper.load_model(model_id)
        result = model.transcribe(audio_fp)["segments"]
        return result
        
    @classmethod
    def video_to_text(cls, video_fp):
        
        """
        视频转文字
            不同于语音，采用OCR技术
        """

    @classmethod
    def speech_split(cls, audio_fp):

        """
        语音分段

        """

    @classmethod
    def process(cls, item):

        if not item.source.is_subtitle_available:
            self.audio_to_text