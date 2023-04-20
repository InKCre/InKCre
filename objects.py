# env: python3.10
# author: Lanzhijiang
# date: 2023/04/19
# description: 数据对象等...

import json
from source import get_source_cls

settings = json.load(open("./data/settings.json", "r", encoding="utf-8"))["item"]


class Item:

    def __init__(self, name, source, processor, processed_addr=None) -> None:
        
        self.name = name
        self.source = source
        self.processor = processor
        if processed_addr is None:
            processed_addr = settings["defaultProcessedAddr"]
        self.processed_addr = processed_addr

        self._temp_path = "%s/%s/%s/" % (settings["tempBasePath"], source.source_type, name)

        self._status = "wait"

    @staticmethod
    def create_from_raw_info(name, source_addr, source_type, processed_type, processed_path=None):
        source = get_source_cls(source_type)(source_addr)
        return Item()

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

    def process(self):

        """
        开始处理
        """
