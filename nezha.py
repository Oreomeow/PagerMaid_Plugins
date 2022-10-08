import asyncio

import contextlib
from pagermaid import bot
from pagermaid.listener import listener
from pagermaid.utils import alias_command, lang, obtain_message


async def del_msg(context, t_lim):
    await asyncio.sleep(t_lim)
    with contextlib.suppress(Exception):
        await context.delete()


@listener(
    is_plugin=True,
    outgoing=True,
    command=alias_command("nz"),
    description=f'Nezha Panel Query. 哪吒面板查询。\n1. Send `/seturl <url>` to @NezhaM_bot to bind your panel. \n给 @NezhaM_bot 发送 `/seturl <url>` 绑定你的面板。\nUsage: `-{alias_command("nz")}`\n2. No binding. 不绑定使用。\nUsage: `-{alias_command("nz")} <url>`',
    parameters="(<url>)",
)
async def nz(context):
    await context.edit("Processing . . .")
    try:
        message = await obtain_message(context)
        cmd = f"/checknezha {message}"
    except ValueError:
        cmd = "/nz"
    async with bot.conversation("NezhaM_bot") as conversation:
        await conversation.send_message(cmd)
        chat_response = await conversation.get_response()
        await bot.send_read_acknowledge(conversation.chat_id)
        nz_text = chat_response.text
    await context.edit(nz_text)
    await del_msg(context, 30)


@listener(
    is_plugin=True,
    outgoing=True,
    command=alias_command("nezha"),
    description=f"Nezha Panel Detailed Quiry. 哪吒面板详细查询。\nNeed to send `/add <url> <token>` to @nezhaChecker_bot to bind your panel first.\n需先给 @nezhaChecker_bot 发送 `/add <url> <token>` 绑定你的面板。",
    parameters="(<id>/s <keyword>)",
)
async def nezha(context):
    await context.edit("Processing . . .")
    params = context.parameter
    if len(params) == 0:
        await context.edit(
            "No query ID entered, general information returned.\n未输入查询 ID，返回整体信息。"
        )
        cmd = "/all"
    elif len(params) == 1:
        cmd = f"/id {params[0]}"
    elif params[0] == "s":
        await context.edit(
            "Start keyword (case-sensitive) lookup mode.\n启动关键词（大小写敏感）查找模式。"
        )
        cmd = f'/search {" ".join(params[1:])}'
    else:
        await context.edit(lang("arg_error"))
        return await del_msg(context, 3)
    async with bot.conversation("nezhaChecker_bot") as conversation:
        await conversation.send_message(cmd)
        chat_response = (
            await conversation.get_response()
            if len(params) < 2
            else await conversation.get_edit()
        )
        await bot.send_read_acknowledge(conversation.chat_id)
        nezha_text = chat_response.text
    await context.edit(nezha_text, parse_mode="html")
    await del_msg(context, 30)
