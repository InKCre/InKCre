# env: python3.10
# author: Lanzhijiang
# date: 2023/04/19
# description: 数据对象等...

import json
from source import get_source_cls, Source
from processor import get_processor_cls

settings = json.load(open("./data/settings.json", "r", encoding="utf-8"))["item"]


class Item:

    def __init__(self, name, source: Source, processor, processed_addr=None) -> None:
        
        self.name = name
        self.source = source
        self.processor = processor

        self._temp_path = "%s/%s/%s/" % (settings["tempBasePath"], source.source_type, name)

        self._status = "wait"

    @staticmethod
    def create_from_raw_info(name, source_addr, source_type, processed_type, processed_addr=None):
        if processed_addr is None:
            processed_addr = settings["defaultProcessedAddr"]
        source = get_source_cls(source_type)(source_addr)
        processor = get_processor_cls(processed_type)(processed_addr)
        return Item(name, source, processor, processed_addr)

    @property
    def status(self):
        return self._status
    
    @property
    def temp_base_path(self):
        return self._temp_path
    
    def set_inqueue(self):

        self._status = "inqueue"

    def set_done(self):
        self._status = "done"

    async def process(self):

        """
        开始处理
        """
        # 获取源数据
        await self.source.download_content()
        await self.source.download_metadata()

        # 开始处理
        await self.processor.process(self)