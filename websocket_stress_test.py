import asyncio
import argparse
import ssl
import sys
import traceback
from multiprocessing import Process

try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except:
    pass

import websockets

parser = argparse.ArgumentParser(description='websocket压测')
parser.add_argument('--host', required=True, help='websocket的url信息')
parser.add_argument('-t', '--timeout', help='websocket的超时时间', default=30, type=int)
parser.add_argument('-p', '--process_num', help='创建的进程数', default=4, type=int)
parser.add_argument('-n', '--numbers', help='每个进程并发的个数', default=100, type=int)
args = parser.parse_args()
print(args)

ssl_context = ssl.SSLContext()
ssl_context.verify_mode = ssl.CERT_NONE


async def hello():
    try:
        async with websockets.connect(args.host, ssl=ssl_context, timeout=args.timeout) as websocket:
            while True:
                await websocket.send("Hello world!")
                response = await websocket.recv()
                print(response)
                await asyncio.sleep(1.0)
    except websockets.exceptions.InvalidStatusCode as e:
        if e.status_code == 502:
            sys.exit(-1)
        raise
    except Exception as e:
        await asyncio.sleep(1.0)
        await hello()


async def amain(numbers):
    tasks = set()
    for i in range(numbers):
        task = asyncio.create_task(hello())
        tasks.add(task)
    await asyncio.gather(*tasks)


def main(numbers):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(amain(numbers))


def multiprocesses_coroutine(process_num, numbers):
    processes = []
    for index in range(process_num):
        processes.append(Process(target=main, args=(numbers,)))

    for index in range(process_num):
        processes[index].start()

    for index in range(process_num):
        processes[index].join()


if __name__ == '__main__':
    multiprocesses_coroutine(process_num=args.process_num, numbers=args.numbers)
