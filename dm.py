""" Module to automate message deletion. """
import contextlib
from asyncio import sleep
from os import path, remove
from os.path import exists

from pagermaid import log, redis, redis_status
from pagermaid.listener import listener
from pagermaid.utils import alias_command
from PIL import Image, UnidentifiedImageError


@listener(
    is_plugin=True,
    outgoing=True,
    command=alias_command("dm"),
    description="编辑并删除当前对话您发送的特定数量的消息。限制：基于消息 ID 的 1000 条消息，大于 1000 "
    "条可能会触发删除消息过快限制。入群消息非管理员无法删除。（倒序）当数字足够大时即可实现删除所有消息。",
    parameters="<数量> [文本]",
)
async def dme(context):
    """Deletes specific amount of messages you sent."""
    reply = await context.get_reply_message()
    if reply and reply.photo:
        if exists("plugins/dme.jpg"):
            remove("plugins/dme.jpg")
        target_file = reply.photo
        await context.client.download_media(
            await context.get_reply_message(), file="plugins/dme.jpg"
        )
        await context.edit("替换图片设置完成。")
    elif reply and reply.sticker:
        if exists("plugins/dme.jpg"):
            remove("plugins/dme.jpg")
        await context.client.download_media(
            reply.media.document, file="plugins/dme.webp"
        )
        try:
            im = Image.open("plugins/dme.webp")
        except UnidentifiedImageError:
            return await context.edit("替换图片设置发生错误。")
        im.save("plugins/dme.png", "png")
        remove("plugins/dme.webp")
        target_file = await context.client.upload_file("plugins/dme.png")
        await context.edit("替换图片设置完成。")
    elif path.isfile("plugins/dme.jpg"):
        target_file = await context.client.upload_file("plugins/dme.jpg")
    elif path.isfile("plugins/dme.png"):
        target_file = await context.client.upload_file("plugins/dme.png")
    else:
        target_file = False
        await context.edit("注意：没有图片进行替换。")
    try:
        count = int(context.parameter[0]) + 1
    except (ValueError, IndexError):
        return await context.edit("出错了呜呜呜 ~ 无效的参数。")
    dme_msg = "别搁这防撤回了。。。"
    if len(context.parameter) == 1:
        if redis_status():
            with contextlib.suppress(Exception):
                dme_msg = redis.get("dme_msg").decode()
    elif len(context.parameter) == 2:
        dme_msg = context.parameter[1]
        if not redis_status():
            pass
        elif dme_msg != str(count):
            with contextlib.suppress(Exception):
                redis.set("dme_msg", dme_msg)
    count_buffer = 0
    try:
        async for message in context.client.iter_messages(
            context.chat_id, from_user="me"
        ):
            if count_buffer == count:
                break
            if (
                message.forward
                or message.via_bot
                or message.sticker
                or message.contact
                or message.poll
                or message.game
                or message.geo
            ):
                pass
            elif message.text or message.voice:
                if message.text != dme_msg:
                    with contextlib.suppress(Exception):
                        await message.edit(dme_msg)
            elif (
                message.document
                or message.photo
                or message.file
                or message.audio
                or message.video
                or message.gif
            ):
                if message.text != dme_msg:
                    with contextlib.suppress(Exception):
                        if target_file:
                            await message.edit(dme_msg, file=target_file)
                        else:
                            await message.edit(dme_msg)
            await message.delete()
            count_buffer += 1
    except ValueError:
        with contextlib.suppress(Exception):
            await context.edit("出错了呜呜呜 ~ 无法识别的对话")
        return
    count -= 1
    count_buffer -= 1
    await log(f"批量删除了自行发送的 {count_buffer} / {count} 条消息。")
    try:
        notification = await send_prune_notify(context, count_buffer, count)
    except Exception:
        return
    await sleep(0.5)
    await notification.delete()


async def send_prune_notify(context, count_buffer, count):
    return await context.client.send_message(
        context.chat_id, f"删除了 {str(count_buffer)} / {str(count)} 条消息。"
    )
