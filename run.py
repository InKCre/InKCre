# env: python3.10
# author: Lanzhijiang
# date: 2023/04/19
# description: 程序启动点

import asyncio, queue
from objects import Item
from processor.video_processor import VideoProcessor


process_queue = queue.Queue()


async def run():
    
    print("------------New Order----------")
    name = input("请输入名称：")
    source_type = input("请输入数据类型：")
    source_addr = input("请输入数据地址：")
    processed_type = input("请输入处理后类型：")

    if processed_type == "video":
        processor = VideoProcessor

    new_item = Item(name, source_addr, source_type, processor)
    process_queue.put(new_item)
    new_item = process_queue.get(new_item)

    new_item.process()


if __name__ == '__main__':

    print("""
        ##########################
                   D.I.C
               数据.信息.创意
              By Lan_zhijiang
         lanzhijiang@foxmail.com
        ##########################
    """)
    asyncio.get_event_loop().run_until_complete(run())