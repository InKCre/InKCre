

class Source:
    def __init__(self, source_type, item = None) -> None:
        
        self.source_type = source_type
        self.item = item
        if self.item is None:
            self.item_name = None
            self.temp_path = None
        else:    
            self.item_name = self.item.name
            self.temp_path = self.item.temp_base_path

        self._download_content = None
        self._download_metadata = None

        self.metadata = {}

    async def download_content(self, *args, **kwargs):

        self._download_content(self, *args, **kwargs)

    async def download_metadata(self, *args, **kwargs):

        self._download_metadata(self, *args, **kwargs)
