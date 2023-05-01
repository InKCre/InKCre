from collect.pre_processor.video_pre_processor import VideoProcessor

source_type_to_pre_processor_cls_table = {
    "video": VideoProcessor
}


def get_pre_processor_cls(source_type):
    return source_type_to_pre_processor_cls_table[source_type]


def add_new_table_item(source_type, pre_processor_path):

    __import__("handler.handler_manager", fromlist=["HandlerManager"]).HandlerManager
