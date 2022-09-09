from os.path import isdir, isfile

from pagermaid.listener import listener
from pagermaid.utils import alias_command, attach_log, execute


@listener(
    is_plugin=True,
    outgoing=True,
    command=alias_command("view"),
    description="Use ls (-alrt) or cat (-n) to view a directory or file. 使用 ls (-alrt) 或 cat (-n) 查看目录或文件",
    parameters="(<path>)",
)
async def view(context):
    params = context.parameter
    if len(params) < 1:
        output = await execute("ls")
        await context.edit(f"```{output}```")
    elif len(params) < 2:
        path = params[0]
        if isfile(path):
            content = await execute(f"cat -n {path}")
            if len(content) > 4096:
                return await attach_log(
                    content, context.chat_id, f"{path}.txt", context.id
                )
            await context.edit(f"```{content}```")
        elif isdir(path):
            output = await execute(f"ls -ahlrt {path}")
            if len(output) > 4096:
                return await attach_log(
                    output, context.chat_id, f"{path}.txt", context.id
                )
            await context.edit(f"```{output}```")
        else:
            await context.edit(
                f"`{path}` is neither a file nor a directory! Exit!\n`{path}` 既不是文件，也不是目录！退出！"
            )
    else:
        await context.edit("Not supported multiple parameters.\n不支持多个参数。")
