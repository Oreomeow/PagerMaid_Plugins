from pagermaid.listener import listener
from pagermaid.utils import alias_command, lang, obtain_message
from requests import post


def translate(type, text, t):
    try:
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh-Hans;q=0.9",
            "Connection": "keep-alive",
            "Content-Length": "51",
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": "yue.micblo.com",
            "Origin": "https://yue.micblo.com",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
        }
        data = {"type": type, "text": text, "t": t}
        res = post(
            url="https://yue.micblo.com/api/v2/translate", headers=headers, data=data
        ).json()
        if res["state"] == 200:
            return res["content"]
    except Exception as e:
        return str(e)


@listener(
    is_plugin=True,
    outgoing=True,
    command=alias_command("yue"),
    description="普通话（简体） -> 广东话",
)
async def yue(context):
    try:
        text = await obtain_message(context)
    except:
        return await context.edit(lang("arg_error"))
    result = translate(0, text, "")
    if len(result) > 4096:
        return await attach_log(result, context.chat_id, "yue.txt", context.id)
    await context.edit(result)


@listener(
    is_plugin=True,
    outgoing=True,
    command=alias_command("zhtw"),
    description="广东话 -> 普通话（繁体）",
)
async def zhtw(context):
    try:
        text = await obtain_message(context)
    except:
        return await context.edit(lang("arg_error"))
    result = translate(1, text, 1)
    if len(result) > 4096:
        return await attach_log(result, context.chat_id, "yue.txt", context.id)
    await context.edit(result)
