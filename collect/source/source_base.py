from video_source import VideoSource, BiliWork
if __name__ == "__main__":
    from objects import DataItem


source_type_to_cls_table = {
    "video": VideoSource,
    "bili_video": BiliWork
}


def get_source_cls(source_type):
    return source_type_to_cls_table[source_type]


class Source:
    def __init__(self, source_id, source_name, source_type) -> None:
        
        self.source_type = source_type
        self.source_id = source_id
        self.source_name = source_name

    def save_source(self):

        pass

    async def download_item_content(self, item_id, *args, **kwargs):

        """
        下载内容
        """
        pass

    async def download_metadata(self, item_id, *args, **kwargs):

        """
        下载元数据
        """
        pass

    async def get_items_list(self, page=None, start_and_end: list = None, num=None):

        """
        获取数据条目列表
        """
        pass
