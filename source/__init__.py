from video_source import VideoSource, BilibiliWork
if __name__ == "__main__":
    from objects import Item

source_type_to_cls_table = {
    "video": VideoSource,
    "bili_video": BilibiliWork
}


def get_source_cls(source_type):
    return source_type_to_cls_table[source_type]