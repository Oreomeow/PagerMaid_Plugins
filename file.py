import asyncio
import contextlib
from io import BytesIO
from os import chmod, remove, rename, stat
from os.path import isdir, isfile

from pagermaid import bot
from pagermaid.listener import listener
from pagermaid.utils import alias_command, execute


async def del_msg(context, t_lim):
    await asyncio.sleep(t_lim)
    with contextlib.suppress(Exception):
        await context.delete()


@listener(
    is_plugin=True,
    outgoing=True,
    command=alias_command("file"),
    description="Find files from the server based on the keyword and upload the file or output paths to telegram or reply to a message with a file to download the file from telegram to the specified path on the server.\n根据关键词从服务器查找文件并上传文件或输出路径到 telegram 或回复带有文件的消息从 telegram 下载文件到服务器指定路径。",
    parameters="<keyword> or <filepath> (in reply)",
)
async def file(context):
    params = context.parameter
    if len(params) < 1:
        await context.edit("Missing parameters.\n参数缺失。")
        return await del_msg(context, 3)
    elif len(params) < 2:
        message = await context.get_reply_message()
        if message:
            if message.media:
                _file = BytesIO()
                try:
                    await bot.download_file(message.media.document, _file)
                except AttributeError:
                    return await context.edit(
                        "Unable to download this type of file.\n无法下载此类型的文件。"
                    )
                if isdir(params[0]):
                    params[0] = params[0].rstrip("/") + "/" + str(message.file.name)
                    await context.edit(
                        f"This is the directory that will be automatically patched with the filename as the full path.\n此为目录，将被自动补上文件名作为完整路径。\n{params[0]}"
                    )
                if isfile(params[0]):
                    with contextlib.suppress(FileNotFoundError):
                        remove(f"{params[0]}.bak")
                    rename(params[0], f"{params[0]}.bak")
                    await context.edit(
                        f"This path already has files, so the original files are backed up.\n此路径已存在文件，已将原文件备份至 {params[0]}.bak。"
                    )
                with open(params[0], "wb") as f:
                    f.write(_file.getvalue())
                    chmod(params[0], 0o0744)
                    permission = oct(stat(params[0]).st_mode)[-3:]
                await context.edit(
                    f"Saved successfully.\n保存成功，保存路径(path) {params[0]}，权限(permisson) {permission}。"
                )
            else:
                await context.edit(
                    "The message replied to doesn't contain a file.\n所回复消息中不包含文件。"
                )
                return await del_msg(context, 3)
        else:
            keyword = params[0]
            file_path = await execute(f'"*{keyword}*" -print | head -1')
            if not isfile(file_path):
                return await context.edit(
                    f"Wrong keyword or file doesn't exist.\n{keyword} 关键词有误或文件不存在。"
                )
            chat_id = context.chat_id
            await context.edit(f"Uploading . . .\n正在上传 `{file_path}` 文件。")
            await bot.send_file(chat_id, file_path, force_document=True)
            await context.edit("Upload complete.\n上传完毕。")
            await del_msg(context, 3)
    elif len(params) < 3:
        keyword = params[0]
        n = params[1]
        file_path = await execute(
            f'n={n};find / -path "/proc" -prune -o -type f -name "*{keyword}*" -print | head -$n'
        )
        await context.edit(f"**Found files below**\n**找到的文件如下**：\n```{file_path}```")
    else:
        await context.edit("Unknown Command.\n未知命令。")
        return await del_msg(context, 3)


@listener(
    is_plugin=True,
    outgoing=True,
    command=alias_command("wfind"),
    description="Find server files by filename or the keyword & wildcards and upload the file or output paths to telegram.\n根据文件名或关键词和通配符查找服务器文件并上传文件或输出路径到 telegram",
    parameters="<(wildcard)keyword(wildcard)>",
)
async def wfind(context):
    params = context.parameter
    if len(params) < 1:
        await context.edit("Missing parameters.\n参数缺失。")
        return await del_msg(context, 3)
    elif len(params) < 2:
        content = params[0]
        file_path = await execute(
            f'find / -path "/proc" -prune -o -type f -name "{content}" -print | head -1'
        )
        if not isfile(file_path):
            return await context.edit(
                f"Wrong keyword or file doesn't exist.\n{content} 关键词有误或文件不存在。"
            )
        chat_id = context.chat_id
        await context.edit(f"Uploading . . .\n正在上传 `{file_path}` 文件。")
        await bot.send_file(chat_id, file_path, force_document=True)
        await context.edit("Upload complete.\n上传完毕。")
        await del_msg(context, 3)
    elif len(params) < 3:
        content = params[0]
        n = params[1]
        file_path = await execute(
            f'n={n};find / -path "/proc" -prune -o -type f -name "{content}" -print | head -$n'
        )
        await context.edit(f"**Found files below**\n**找到的文件如下**：\n```{file_path}```")
    else:
        await context.edit("Unknown Command.\n未知命令。")
        return await del_msg(context, 3)
