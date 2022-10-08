from pagermaid.listener import listener
from pagermaid.utils import alias_command, obtain_message, pip_install

pip_install("baiduspider")
from baiduspider import BaiduSpider


@listener(
    is_plugin=True,
    outgoing=True,
    command=alias_command("baike"),
    description="查询百度百科词条",
    parameters="<词组>",
)
async def baike(context):
    await context.edit("获取中 . . .")
    try:
        message = await obtain_message(context)
    except ValueError:
        return await context.edit("出错了呜呜呜 ~ 无效的参数。")

    try:
        results = BaiduSpider().search_baike(message).plain
    except Exception:
        return await context.edit("出错了呜呜呜 ~ 无法访问到百度百科。")
    if results:
        result = results[0]
        title = result["title"].replace("_百度百科", "")
        url = result["url"]
        des = result["des"]
        upd_date = result["upd_date"]
        others = ""
        if len(results) > 1:
            others = "其他词条："
            for i in results[1:]:
                others += f'[{i["title"].replace(" - 百度百科", "")}](https://baike.baidu.com{i["url"].replace("https://baike.baidu.comhttps://baike.baidu.com","")})\t'
        message = f"词条： [{title}]({url})\n\n{des}\n\n此词条最后修订于{upd_date}\n\n{others}"
    else:
        message = "没有匹配到相关词条"
    await context.edit(message)
