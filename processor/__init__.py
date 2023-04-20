from video_processor import VideoProcessor

processed_type_to_processor_cls_table = {
    "video": VideoProcessor
}


def get_processor(processed_type):
    return processed_type_to_processor_cls_table[processed_type]
