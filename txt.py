import asyncio
from os import remove
from os.path import splitext

from pagermaid import bot
from pagermaid.listener import listener
from pagermaid.utils import alias_command


async def del_msg(context, t_lim):
    await asyncio.sleep(t_lim)
    try:
        await context.delete()
    except:
        pass


@listener(
    is_plugin=True,
    outgoing=True,
    command=alias_command("txt"),
    description="Convert a file to an Android-friendly txt file. 转换某文件为 Android 友好型 txt 文件。",
)
async def txt(context):
    message = await context.get_reply_message()
    if message:
        if message.file:
            file_path = f"data/{splitext(message.file.name)[0]}.txt"
            try:
                await bot.download_media(message, file_path)
            except AttributeError:
                return await context.edit(
                    "Unable to download this type of file.\n无法下载此类型的文件。"
                )
        else:
            await context.edit(
                "The message replied to doesn't contain a file.\n所回复消息中不包含文件。"
            )
            return await del_msg(context, 3)
        await bot.send_file(context.chat_id, file_path, force_document=True)
        await context.edit("Conversion complete.\n转换完毕。")
        await del_msg(context, 3)
        remove(file_path)
