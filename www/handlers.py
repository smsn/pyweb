from web_frame import get, post


@get('/')
async def hello(request):
    # name = request.match_info.get('name', "Anonymous")
    return "Welcome !"


@get(r'/user{tail:.*}')
async def test(request):
    return (403, "test666")
