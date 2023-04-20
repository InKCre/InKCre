from video_source import VideoSource, BilibiliWork
if __name__ == "__main__":
    from objects import Item

source_type_to_cls_table = {
    "video": VideoSource,
    "bili_video": BilibiliWork
}


def get_source_cls(source_type):
    return source_type_to_cls_table[source_type]


class Source:

    def __init__(self, source_type, item: Item = None) -> None:
        
        self.source_type = source_type
        self.item = item
        if self.item is None:
            self.item_name = None
            self.temp_path = None
        else:    
            self.item_name = self.item.name
            self.temp_path = self.item.temp_base_path

        self._download_content = None
        # self._download_metadata = None

    async def download_content(self, *args, **kwargs):

        self._download_content(self, *args, **kwargs)

    # async def download_metadata(self, *args, **kwargs):

    #     self._download_metadata(self, *args, **kwargs)
