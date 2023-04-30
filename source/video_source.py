# env: python3.10 lxml ffmpeg
# author: Lanzhijiang
# date: 2023/04/05
# description: 
#   主要通过AI的能力来处理、提取视频中的信息，并整合为富文本从而节省时间
#   设计：获取某个视频列表(稍后再看、收藏夹...)，然后爬取下载->处理->输出为md总结
#   输入：分析对象

from bilibili_api import video, Credential
from bilibili_api import settings as bilibiapi_settings
# import bilibili_api.utils.network as network
import httpx, re, requests
# from ffmpeg.asyncio import FFmpeg
# from ffmpeg import Progress
import asyncio, os, json
from tqdm import tqdm
from source_base import Source

# if __name__ == "__main__":
#     from objects import Item

# settings
# settings = json.load(open("../data/settings.json", "r"), encoding="utf-8")["videoSource"]
settings = {
        "baseTempPath": "./processing/video/",
        "language": "zh-Hans"
}

# CONSTANT

# bilibili_api setting
bilibiapi_settings.timeout = 5.0
# settings.geetest_auto_open = False


class VideoSource(Source):

    VIDEO_QUALITY = 80
    AUDIO_QUALITY = None 

    def __init__(self, video_addr=None, item = None) -> None:
        
        Source.__init__(self, "video", item)
        self.video_addr = video_addr
        self.video_title = None

        self.video_fp = None
        self.audio_fp = None

        self.is_subtitle_available = False

    @classmethod
    def select_ideal_streams(cls, dash):

        """
        选出理想音频视频流
        :return Tuple[List[VideoStreamDownloadURL | AudioStreamDownloadURL], None]
        """
        video_dash = dash["video"]
        audio_dash = dash["audio"]

        # select video
        for one in video_dash:
            if one["id"] == cls.VIDEO_QUALITY:
                print("选择视频流：%s %s %s %s" % ("%sp" % one["height"], one["bandwidth"], one["codecs"], one["mimeType"]))
                video_steam_download_url = one["baseUrl"]
                vid_format = one["mimeType"][-3:]
                break

        # select audio
        if cls.AUDIO_QUALITY is None:
            audio_one = audio_dash[-1]
        else:
            for one in audio_dash:
                if one["bandwidth"] == cls.AUDIO_QUALITY:
                    audio_one = one
                    break
        print("选择音频流：%s %s %s" % ("%s" % one["bandwidth"], one["codecs"], one["mimeType"]))
        audio_steam_download_url = audio_one["baseUrl"]

        return (video_steam_download_url, audio_steam_download_url), vid_format

class BilibiliWork(VideoSource, video.Video):

    ''' b站稿件源类 '''

    BASE_URL = "https://www.bilibili.com/video/"
    SESSDATA = "2f53b70f%2C1696164775%2C098f8%2A42"
    BILI_JCT = "3853f557ccee4247cef1412be9b15ffa"
    BUVID3 = "508400C7-2B40-A1A3-E6D1-013148F896F962620infoc"
    credential = Credential(sessdata=SESSDATA, bili_jct=BILI_JCT, buvid3=BUVID3)

    HEADERS = {
        "origin": "https://www.bilibili.com",
        "referer": None,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.62",
    }
    
    def __init__(self, video_addr=None, video_id=None, item=None) -> None:
        
        VideoSource.__init__(self, video_addr, item)
        self.video_addr, self.video_id, self.video_type = self._get_video_source_info_from_addr(video_addr, video_id)

        self._download_content = self.download_video_and_audio
        # self._download_metadata = self.download_metadata

        self.pages = None
        self.tags: list = None

    @property
    async def title(self):
        if self.video_title is None:
            self.video_title = await self.get_info()["title"]
        return self.video_title

    def _get_video_source_info_from_addr(self, video_addr=None, video_id=None):

        """
        从视频源地址中提取视频源信息
        """
        if video_addr is not None:
            video_id = re.findall("https:\/\/www.bilibili.com\/video\/(.*?)\/", video_addr)[0]
        else:
            video_addr = self.BASE_URL + video_id
        if video_id is None or video_addr is None:
            raise ValueError("video_addr or video_id should be filled")
        
        if "BV" in video_id:
            video_id_type = "bv"
            video.Video.__init__(self, bvid=video_id, credential=self.credential)
        else:
            video_id_type = "av"
            video.Video.__init__(self, aid=video_id, credential=self.credential)

        return video_addr, video_id, video_id_type
    
    @staticmethod
    def _format_title(v_title: str):
        return v_title.replace(" ", "_")

    async def download_video_and_audio(self):
        
        """
        获取视频数据
            获取音频流(mp3)与视频流(mp4)以及字幕文件(如果有)
        """
        v_info = await self.get_info()
        v_title = self._format_title(v_info["title"])
        self.video_title = v_title
        if self.work_temp_path is None:
            self.work_temp_path = "%s/%s/" % (self.temp_path, self.video_title)
        
        out_temp_video_fp = self.temp_path + "%s_video.m4s" % v_title
        out_temp_audio_fp = self.temp_path + "%s_audio.m4s" % v_title
        out_video_fp = self.temp_path + v_title + "_video.mp4"
        out_audio_fp = self.temp_path + v_title + "_audio.mp3"

        download_data = await self.get_download_url(0)
        streams, vid_format = self.select_ideal_streams(download_data["dash"])
        if vid_format == "flv":
            out_av_fp = self.temp_path + "%s_temp.flv" % v_title
            await self.download_stream_data(streams[0], out_av_fp, "FLV 音视频流 %s" % v_title)
            os.system(f"ffmpeg -i %s %s_video.mp4" % (out_av_fp, out_video_fp))
            os.system(f"ffmpeg -i %s %s_audio.mp3" % (out_av_fp, out_audio_fp))
            os.remove(out_av_fp)
        else:
            await self.download_stream_data(streams[0], out_temp_video_fp, "MP4 视频流 %s" % v_title)
            await self.download_stream_data(streams[1], out_temp_audio_fp, "MP4 音频流 %s" % v_title)
            os.system(f"ffmpeg -i %s %s_video.mp4" % (out_temp_video_fp, out_video_fp))
            os.system(f"ffmpeg -i %s -ac 1 -ar 16000 %s_audio.mp3" % (out_temp_audio_fp, out_audio_fp))
            os.remove(out_temp_video_fp); os.remove(out_temp_audio_fp)

        self.video_fp = out_video_fp
        self.audio_fp = out_audio_fp

        return out_temp_video_fp, out_temp_audio_fp

    async def download_stream_data(self, stram_url, out_fp, info):
        
        """
        获取流数据并保存
        """
        self.HEADERS["referer"] = self.video_addr[:-1]
        
        async with httpx.AsyncClient(headers=self.HEADERS) as session:
        # with requests.session() as session:
            res = await session.get(url=stram_url, cookies=self.credential.get_cookies())
            length = res.headers.get('content-length')

            progress_bar = tqdm(total=int(length))
            progress_bar.set_description("正在下载 [%s]" % info)
            with open(out_fp, 'wb') as f:
                for chunk in res.iter_bytes(1024):
                    if not chunk:
                        break
                    
                    f.write(chunk)
                    progress_bar.update(1024)

    async def _get_subtitle(self, pid=0) -> list:
        subtitles = self.get_subtitle(self.get_cid(pid))["subtitles"]
        if subtitles:
            for subtitle in subtitles:
                if subtitle["lan"] == settings["language"]:
                    subtitle_json = requests.get("https://%s" % subtitle["subtitle_url"]).content
                    self.is_subtitle_available = True
        else:
            subtitle_json = []
            self.is_subtitle_available = False
        
        json.dump(subtitle_json, open("%s/subtitle.json" % self.temp_path))
        return subtitle_json

    async def _get_tags(self, pid=0) -> list:
        return self.get_tags(self.get_cid(pid))

    async def download_metadata(self, fields: list = None):
        
        """
        下载元数据
            包括部分TAG、字幕、分P信息等
        """
        _fields = [
                ("subtitle", self._get_subtitle), 
                # ("tags", self._get_tags),
                ("pages", self.get_pages)
            ]
        if fields is not None:
            _fields.extend(fields)

        result = {}
        for field in _fields:
            result[field[0]] = field[1](self)

        self.metadata["subtitle"] = result["subtitle"]
        self.metadata["pages"] = result["pages"]

        return result
    

# async def entrance(video_addr):
#     vid = BilibiliWork(video_addr)
#     print(await vid.get_tags(await vid.get_cid(2)))


# if __name__ == "__main__":
#     asyncio.get_event_loop().run_until_complete(entrance("https://www.bilibili.com/video/BV14M4y117MB/"))

