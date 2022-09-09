from pagermaid.listener import listener
from pagermaid.utils import alias_command, attach_log, execute, pip_install

pip_install("bypy")


@listener(
    is_plugin=True,
    outgoing=True,
    command=alias_command("bypy"),
    description=f'Python client for Baidu Yun (Personal Cloud Storage) 百度云/百度网盘 Python 客户端。\nTip: `-{alias_command("bypy")} help`',
    parameters="<workflow>",
)
async def bypy(context):
    workflow = context.arguments
    result = await execute(f"bypy {workflow}")

    if len(result) > 4096:
        return await attach_log(result, context.chat_id, f"{workflow}.txt", context.id)
    await context.edit(result)
