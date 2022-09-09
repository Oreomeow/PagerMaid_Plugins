import asyncio
import re

from pagermaid.listener import listener
from pagermaid.utils import alias_command, attach_log, execute, pip_install

pip_install("pipgh")
pip_install("qypi")
pip_install("pip_search")


async def del_msg(context, t_lim):
    await asyncio.sleep(t_lim)
    try:
        await context.delete()
    except:
        pass


@listener(
    is_plugin=True,
    outgoing=True,
    command=alias_command("pypi"),
    description="Python Libraries Query. Python 库查询。\nTotal 3 modes: query in GitHub, query in Pypi & return JSON, query globally in Pypi & return table (default). \n共三种模式：在 GitHub 查询、在 Pypi 查询并返回 JSON、在 Pypi 全局查询并返回表格（默认）。",
    parameters="(gh/i/s) <query>",
)
async def pypi(context):
    params = context.parameter
    if len(params) == 0:
        await context.edit("参数缺失。\nMissing parameters.")
        return await del_msg(context, 3)
    if len(params) == 1:
        params.append(params[0])
        params[0] = "s"
    if len(params) > 1:
        if params[0] == "gh":
            query = " ".join(params[1:])
            output = await execute(f"pipgh search {query}")
            repo_regex = r"(([0-9a-zA-Z](?:-(?=[0-9a-zA-Z])|[0-9a-zA-Z]){0,38}(?<=[0-9a-zA-Z]))/[0-9a-zA-Z._-]+)"
            output = re.sub(repo_regex, r"[\1](https://github.com/\1)", output)
            if len(output) > 4096:
                await attach_log(
                    output,
                    context.chat_id,
                    f"{query.replace(' ', '+')}.txt",
                    context.id,
                )
            else:
                await context.edit(output)
        elif params[0] == "i":
            query = " ".join(params[1:])
            output = await execute(f"qypi info {query}")
            if len(output) > 4096:
                await attach_log(
                    output,
                    context.chat_id,
                    f"{query.replace(' ', '+')}.txt",
                    context.id,
                )
            else:
                await context.edit(output)
        elif params[0] == "s":
            query = " ".join(params[1:])
            output = await execute(f"pip_search {query}")
            if len(output) > 4096:
                await attach_log(
                    output,
                    context.chat_id,
                    f"{query.replace(' ', '+')}.txt",
                    context.id,
                )
            else:
                await context.edit(output)
        else:
            query = " ".join(params)
            output = await execute(f"pip_search {query}")
            if len(output) > 4096:
                return await attach_log(
                    output,
                    context.chat_id,
                    f"{query.replace(' ', '+')}.txt",
                    context.id,
                )
            await context.edit(output)
