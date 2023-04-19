# env: python3.7 lxml ffmpeg
# author: Lanzhijiang
# date: 2023/04/05
# description: 
#   主要通过AI的能力来处理、提取视频中的信息，并整合为富文本从而节省时间
#   设计：获取某个视频列表(稍后再看、收藏夹...)，然后爬取下载->处理->输出为md总结
#   输入：分析对象

from bilibili_api import video, Credential
from bilibili_api import settings as bilibiapi_settings
import bilibili_api.utils.network as network
import httpx, re, requests
from ffmpeg.asyncio import FFmpeg
from ffmpeg import Progress
import asyncio, os, json
from tqdm import tqdm 

# settings
BASE_FILE_PATH = json.load("./data/settings.json")["videoProcessor"]["filePath"]

# CONSTANT
BASE_VID_URL = "https://www.bilibili.com/video/"
HEADERS = {
    "origin": "https://www.bilibili.com",
    "referer": None,
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.62",
}

VIDEO_QUALITY = 80
AUDIO_QUALITY = None

# bilibili_identity
SESSDATA = "2f53b70f%2C1696164775%2C098f8%2A42"
BILI_JCT = "3853f557ccee4247cef1412be9b15ffa"
BUVID3 = "508400C7-2B40-A1A3-E6D1-013148F896F962620infoc"
credential = Credential(sessdata=SESSDATA, bili_jct=BILI_JCT, buvid3=BUVID3)

# bilibili_api setting
bilibiapi_settings.timeout = 5.0
# settings.geetest_auto_open = False


class Video(video.Video):

    def __init__(self, vid_url=None, vid=None) -> None:
        
        self.vid = vid
        self.vid_url = vid_url
        if self.vid_url is not None:
            self.vid = re.findall("https:\/\/www.bilibili.com\/video\/(.*?)\/", vid_url)[0]
        else:
            self.vid_url = BASE_VID_URL + vid
        if self.vid is None or self.vid_url is None:
            raise ValueError("vid_url or vid should be filled")
        
        if "BV" in self.vid:
            self.vid_type = "bv"
            video.Video.__init__(self, bvid=self.vid, credential=credential)
        else:
            self.vid_type = "av"
            video.Video.__init__(self, aid=self.vid, credential=credential)

        self.vid_url = vid_url

    @staticmethod
    def select_ideal_streams(download_data):

        """
        选出理想音频视频流
        :return Tuple[List[VideoStreamDownloadURL | AudioStreamDownloadURL], None]
        """
        dash = download_data["dash"]
        video_dash = dash["video"]
        audio_dash = dash["audio"]

        # select video
        for one in video_dash:
            if one["id"] == VIDEO_QUALITY:
                print("选择视频流：%s %s %s %s" % ("%sp" % one["height"], one["bandwidth"], one["codecs"], one["mimeType"]))
                video_steam_download_url = one["baseUrl"]
                vid_format = one["mimeType"][-3:]
                break

        # select audio
        if AUDIO_QUALITY is None:
            audio_one = audio_dash[-1]
        else:
            for one in audio_dash:
                if one["bandwidth"] == AUDIO_QUALITY:
                    audio_one = one
                    break
        print("选择音频流：%s %s %s" % ("%s" % one["bandwidth"], one["codecs"], one["mimeType"]))
        audio_steam_download_url = audio_one["baseUrl"]

        return (video_steam_download_url, audio_steam_download_url), vid_format
    
    @staticmethod
    def _process_title(v_title):
        return v_title.replace(" ", "_")

    async def fetch_video_data(self):
        
        """
        获取视频数据
            获取音频流(mp3)与视频流(mp4)以及字幕文件(如果有)
        """
        v_info = await self.get_info()
        v_title = self._process_title(v_info["title"])
        

        download_data = await self.get_download_url(0)
        streams, vid_format = self.select_ideal_streams(download_data)
        if vid_format == "flv":
            out_temp_fp = BASE_FILE_PATH + "%s_temp.flv" % v_title
            await self.download_stream_data(streams[0], out_temp_fp, "FLV 音视频流 %s" % v_title)
            to_video = FFmpeg().option("an").input(out_temp_fp).output("%s_video.mp4" % v_title, {"codec": "copy"})
            to_audio = FFmpeg().option("vn").input(out_temp_fp).output("%s_audio.mp3" % v_title, {"codec": "copy"})
        else:
            out_vid_fp = BASE_FILE_PATH + "%s_video.m4s" % v_title
            out_aud_fp = BASE_FILE_PATH + "%s_audio.m4s" % v_title
            await self.download_stream_data(streams[0], out_vid_fp, "MP4 视频流 %s" % v_title)
            await self.download_stream_data(streams[1], out_aud_fp, "MP4 音频流 %s" % v_title)
            os.system(f"ffmpeg -i %s %s_video.mp4" % (out_vid_fp, BASE_FILE_PATH+v_title))
            os.system(f"ffmpeg -i %s %s_audio.mp3" % (out_aud_fp, BASE_FILE_PATH+v_title))

        return out_vid_fp.replace("ms4", "mp4"), out_aud_fp.replace("ms4", "mp3"), 

    async def download_stream_data(self, stram_url, out_fp, info):
        
        """
        获取流数据并保存
        """
        HEADERS["referer"] = self.vid_url[:-1]
        
        async with httpx.AsyncClient(headers=HEADERS) as session:
        # with requests.session() as session:
            res = await session.get(url=stram_url, cookies=credential.get_cookies())
            length = res.headers.get('content-length')

            progress_bar = tqdm(total=int(length))
            progress_bar.set_description("正在下载 [%s]" % info)
            with open(out_fp, 'wb') as f:
                for chunk in res.iter_bytes(1024):
                    if not chunk:
                        break
                    
                    f.write(chunk)
                    progress_bar.update(1024)


async def enterance():
    
    v = Video("https://www.bilibili.com/video/BV1Hk4y1q7Rz/")
    await v.fetch_video_data()


def asr(title, audio_fp):

    
    

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(enterance())
