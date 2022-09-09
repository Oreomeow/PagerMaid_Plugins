import asyncio

from pagermaid.listener import listener
from pagermaid.utils import alias_command, attach_log, execute


async def del_msg(context, t_lim):
    await asyncio.sleep(t_lim)
    try:
        await context.delete()
    except:
        pass


@listener(
    is_plugin=True,
    outgoing=True,
    command=alias_command("wget"),
    description="GNU Wget (or just Wget, formerly Geturl, also written as its package name, wget) is a computer program that retrieves content from web servers. GNU Wget 是一个从网络上自动下载文件的自由工具。",
    parameters="(<options>) <url>",
)
async def wget(context):
    params = context.parameter
    reply = await context.get_reply_message()
    if len(params) < 1:
        if reply:
            params.insert(0, reply.text)
        else:
            await context.edit("Missing parameters.\n参数缺失。")
            return await del_msg(context, 3)
    if len(params) < 2:
        content = await execute(f"wget -qO- {params[0]}")
        if not content:
            return await context.edit(
                f"[URL]({params[0]}) content download and output to stdout failed.\n下载并输出到命令行失败。"
            )
        else:
            if len(content) > 4096:
                await attach_log(content, context.chat_id, f"content.txt", context.id)
            else:
                await context.edit(content)
    else:
        output = await execute(f"wget {' '.join(params)}")
        if len(output) > 4096:
            return await attach_log(output, context.chat_id, f"output.txt", context.id)
        await context.edit(output)
