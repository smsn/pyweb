from aiohttp import web
import asyncio

import logging
logging.basicConfig(level=logging.INFO)
# LOG_FORMAT = "%(asctime)s - %(message)s"
# logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)
# logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
# logging.basicConfig(level=logging.WARNING, format=LOG_FORMAT)


async def block_test(request):
    await asyncio.sleep(10)
    return web.Response(text="block test!")


async def hello(request):
    return web.Response(text="welcome!")


async def main(loop):
    app = web.Application(loop=loop)
    app.add_routes([web.get('/', hello)])
    app.add_routes([web.get('/t/', block_test)])
    await loop.create_server(app.make_handler(), host='0.0.0.0', port=8080)
    logging.info('server started at http://0.0.0.0:8080 ...')
    # web.run_app(app, host='0.0.0.0', port=8080)

loop = asyncio.get_event_loop()
loop.run_until_complete(main(loop))
loop.run_forever()
