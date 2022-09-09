from asyncio import TimeoutError, sleep
from io import BytesIO
from math import floor
from os import makedirs, remove
from os.path import exists

from pagermaid import bot, version
from pagermaid.listener import listener
from pagermaid.utils import alias_command, client
from PIL import Image, ImageDraw, ImageFont
from requests import get
from telethon.errors import (
    AuthKeyError,
    FloodWaitError,
    ForbiddenError,
    YouBlockedUserError,
)
from telethon.tl.functions.contacts import UnblockRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import (
    MessageMediaPhoto,
    MessageMediaUnsupported,
    MessageMediaWebPage,
)


def font(path, size):
    return ImageFont.truetype(f"{path}ZhuZiAWan-2.ttc", size=size, encoding="utf-8")


def cut(obj, sec):
    return [obj[i : i + sec] for i in range(0, len(obj), sec)]


def yv_lu_process_image(name, text, photo, path):
    if len(name) > 16:
        name = name[:16] + "..."
    text = cut(text, 17)
    # 用户不存在头像时
    if not photo:
        photo = Image.open(f"{path}p4.png")
        # 对图片写字
        draw = ImageDraw.Draw(photo)
        # 计算使用该字体占据的空间
        # 返回一个 tuple (width, height)
        # 分别代表这行字占据的宽和高
        text_width = font(path, 60).getsize(name[0])
        if name[0].isalpha():
            text_coordinate = (
                int((photo.size[0] - text_width[0]) / 2),
                int((photo.size[1] - text_width[1]) / 2) - 10,
            )
        else:
            text_coordinate = int((photo.size[0] - text_width[0]) / 2), int(
                (photo.size[1] - text_width[1]) / 2
            )
        draw.text(text_coordinate, name[0], (255, 110, 164), font(path, 60))
    else:
        photo = Image.open(f"{path}{photo}")
    # 读取图片
    img1, img2, img3, mask = (
        Image.open(f"{path}p1.png"),
        Image.open(f"{path}p2.png"),
        Image.open(f"{path}p3.png"),
        Image.open(f"{path}mask.png"),
    )
    size1, size2, size3 = img1.size, img2.size, img3.size
    photo_size = photo.size
    mask_size = mask.size
    scale = photo_size[1] / mask_size[1]
    photo = photo.resize(
        (int(photo_size[0] / scale), int(photo_size[1] / scale)), Image.LANCZOS
    )
    mask1 = Image.new("RGBA", mask_size)
    mask1.paste(photo, mask=mask)
    # 创建空图片
    result = Image.new(
        img1.mode, (size1[0], size1[1] + size2[1] * len(text) + size3[1])
    )

    # 读取粘贴位置
    loc1, loc3, loc4 = (
        (0, 0),
        (0, size1[1] + size2[1] * len(text)),
        (6, size1[1] + size2[1] * len(text) - 23),
    )

    # 对图片写字
    draw = ImageDraw.Draw(img1)
    draw.text((60, 10), name, (255, 110, 164), font(path, 18))
    for i in range(len(text)):
        temp = Image.open(f"{path}p2.png")
        draw = ImageDraw.Draw(temp)
        draw.text((60, 0), text[i], (255, 255, 255), font(path, 18))
        result.paste(temp, (0, size1[1] + size2[1] * i))

    # 粘贴图片
    result.paste(img1, loc1)
    result.paste(img3, loc3)
    result.paste(mask1, loc4)

    # 保存图片
    result.save(f"{path}result.png")


async def yv_lu_process_sticker(name, photo, sticker, path):
    # 用户不存在头像时
    if not photo:
        photo = Image.open(f"{path}p4.png")
        # 对图片写字
        draw = ImageDraw.Draw(photo)
        # 计算使用该字体占据的空间
        # 返回一个 tuple (width, height)
        # 分别代表这行字占据的宽和高
        text_width = font(path, 60).getsize(name[0])
        if name[0].isalpha():
            text_coordinate = (
                int((photo.size[0] - text_width[0]) / 2),
                int((photo.size[1] - text_width[1]) / 2) - 10,
            )
        else:
            text_coordinate = int((photo.size[0] - text_width[0]) / 2), int(
                (photo.size[1] - text_width[1]) / 2
            )
        draw.text(text_coordinate, name[0], (255, 110, 164), font(path, 60))
    else:
        photo = Image.open(f"{path}{photo}")
    # 读取图像
    sticker = await resize_image(sticker, 400)
    # 创建空图片
    result = Image.new("RGBA", (512, 400))
    # 处理头像
    mask = Image.open(f"{path}mask1.png")
    photo_size = photo.size
    mask_size = mask.size
    scale = photo_size[1] / mask_size[1]
    photo = photo.resize(
        (int(photo_size[0] / scale), int(photo_size[1] / scale)), Image.LANCZOS
    )
    mask1 = Image.new("RGBA", mask_size)
    mask1.paste(photo, mask=mask)
    # 粘贴图像
    result.paste(mask1, (0, 300))
    result.paste(sticker, (112, 400 - sticker.size[1]))
    # 保存图像
    result.save(f"{path}result.png")


@listener(
    is_plugin=True,
    outgoing=True,
    command=alias_command("fakeyvlu"),
    description="将回复的消息转换成语录",
    parameters="<text>",
)
async def fakeyvlu(context):
    if not context.reply_to_msg_id:
        await context.edit("你需要回复一条消息。")
        return
    if not exists("plugins/fakeyvlu/"):
        makedirs("plugins/fakeyvlu/")
    await context.edit("处理中。。。")
    # 下载资源文件
    for num in range(1, 5):
        if not exists("plugins/fakeyvlu/p" + str(num) + ".png"):
            re = get(
                "https://gitlab.com/Xtao-Labs/PagerMaid_Plugins/-/raw/master/yvlu/p"
                + str(num)
                + ".png"
            )
            with open("plugins/fakeyvlu/p" + str(num) + ".png", "wb") as bg:
                bg.write(re.content)
    if not exists("plugins/fakeyvlu/mask.png"):
        re = get(
            "https://gitlab.com/Xtao-Labs/PagerMaid_Plugins/-/raw/master/yvlu/mask.png"
        )
        with open("plugins/fakeyvlu/mask.png", "wb") as bg:
            bg.write(re.content)
    if not exists("plugins/fakeyvlu/mask1.png"):
        re = get(
            "https://gitlab.com/Xtao-Labs/PagerMaid_Plugins/-/raw/master/yvlu/mask1.png"
        )
        with open("plugins/fakeyvlu/mask1.png", "wb") as bg:
            bg.write(re.content)
    if not exists("plugins/fakeyvlu/ZhuZiAWan-2.ttc"):
        await context.edit("下载字体中。。。")
        re = get(
            "https://gitlab.com/Xtao-Labs/Telegram_PaimonBot/-/raw/master/assets/fonts/ZhuZiAWan-2.ttc"
        )
        with open("plugins/fakeyvlu/ZhuZiAWan-2.ttc", "wb") as bg:
            bg.write(re.content)
    # 获取回复信息
    reply_message = await context.get_reply_message()
    if not reply_message:
        await context.edit("你需要回复一条消息。")
        return
    user_id = reply_message.sender_id
    target_user = await context.client(GetFullUserRequest(user_id))
    # 下载头像
    await bot.download_profile_photo(
        target_user.user.id,
        "plugins/fakeyvlu/" + str(target_user.user.id) + ".jpg",
        download_big=True,
    )
    name = target_user.user.first_name
    if target_user.user.last_name:
        name += f" {target_user.user.last_name}"
    # 判断是否为贴纸
    file_name = None
    if reply_message and reply_message.media:
        if isinstance(reply_message.media, MessageMediaPhoto):
            file_name = "plugins/fakeyvlu/sticker.jpg"
            await bot.download_media(reply_message.photo, file_name)
        elif isinstance(reply_message.media, MessageMediaWebPage):
            return await context.edit("不支持的文件类型。")
        elif isinstance(reply_message.media, MessageMediaUnsupported):
            return await context.edit("不支持的文件类型。")
        elif "image" in reply_message.media.document.mime_type.split("/"):
            file_name = "plugins/fakeyvlu/sticker.jpg"
            await bot.download_file(reply_message.media.document, file_name)
        else:
            await context.edit("不支持的文件类型。")
            return

    text = " ".join(context.parameter)
    if exists("plugins/fakeyvlu/" + str(target_user.user.id) + ".jpg"):
        if len(context.parameter) > 0:
            yv_lu_process_image(
                name, text, f"{target_user.user.id}.jpg", "plugins/fakeyvlu/"
            )
        elif file_name:
            await yv_lu_process_sticker(name, None, file_name, "plugins/fakeyvlu/")
            remove(file_name)
        else:
            yv_lu_process_image(
                name,
                reply_message.message,
                f"{target_user.user.id}.jpg",
                "plugins/fakeyvlu/",
            )
        remove("plugins/fakeyvlu/" + str(target_user.user.id) + ".jpg")
    else:
        if len(context.parameter) == 1:
            yv_lu_process_image(name, text, None, "plugins/fakeyvlu/")
        elif file_name:
            await yv_lu_process_sticker(name, None, file_name, "plugins/fakeyvlu/")
            remove(file_name)
        else:
            yv_lu_process_image(name, reply_message.message, None, "plugins/fakeyvlu/")
    # 转换为贴纸
    image = await resize_image("plugins/fakeyvlu/result.png", 512)
    file = BytesIO()
    file.name = "sticker.webp"
    try:
        image.save(file, "WEBP")
    except KeyError:
        await context.delete()
        return
    file.seek(0)
    await context.client.send_file(
        context.chat_id,
        file,
        force_document=False,
        reply_to=context.message.reply_to_msg_id,
    )
    await context.delete()


@listener(
    is_plugin=True,
    outgoing=True,
    command=alias_command("onesyvlu"),
    description="生成某人的语录",
    parameters="<name> <text>",
)
async def onesyvlu(context):
    if len(context.parameter) != 2:
        await context.edit("参数错误")
        return
    if not exists("plugins/fakeyvlu/"):
        makedirs("plugins/fakeyvlu/")
    await context.edit("处理中。。。")
    # 下载资源文件
    for num in range(1, 5):
        if not exists("plugins/fakeyvlu/p" + str(num) + ".png"):
            re = get(
                "https://gitlab.com/Xtao-Labs/PagerMaid_Plugins/-/raw/master/yvlu/p"
                + str(num)
                + ".png"
            )
            with open("plugins/fakeyvlu/p" + str(num) + ".png", "wb") as bg:
                bg.write(re.content)
    if not exists("plugins/fakeyvlu/mask.png"):
        re = get(
            "https://gitlab.com/Xtao-Labs/PagerMaid_Plugins/-/raw/master/yvlu/mask.png"
        )
        with open("plugins/fakeyvlu/mask.png", "wb") as bg:
            bg.write(re.content)
    if not exists("plugins/fakeyvlu/mask1.png"):
        re = get(
            "https://gitlab.com/Xtao-Labs/PagerMaid_Plugins/-/raw/master/yvlu/mask1.png"
        )
        with open("plugins/fakeyvlu/mask1.png", "wb") as bg:
            bg.write(re.content)
    if not exists("plugins/fakeyvlu/ZhuZiAWan-2.ttc"):
        await context.edit("下载字体中。。。")
        re = get(
            "https://gitlab.com/Xtao-Labs/Telegram_PaimonBot/-/raw/master/assets/fonts/ZhuZiAWan-2.ttc"
        )
        with open("plugins/fakeyvlu/ZhuZiAWan-2.ttc", "wb") as bg:
            bg.write(re.content)

    yv_lu_process_image(
        context.parameter[0], context.parameter[1], None, "plugins/fakeyvlu/"
    )
    # 转换为贴纸
    image = await resize_image("plugins/fakeyvlu/result.png", 512)
    file = BytesIO()
    file.name = "sticker.webp"
    try:
        image.save(file, "WEBP")
    except KeyError:
        await context.delete()
        return
    file.seek(0)
    await context.client.send_file(
        context.chat_id,
        file,
        force_document=False,
        reply_to=context.message.reply_to_msg_id,
    )
    await context.delete()


async def resize_image(photo, num):
    image = Image.open(photo)
    maxsize = (num, num)
    if (image.width and image.height) < num:
        size1 = image.width
        size2 = image.height
        if image.width > image.height:
            scale = num / size1
            size1new = num
            size2new = size2 * scale
        else:
            scale = num / size2
            size1new = size1 * scale
            size2new = num
        size1new = floor(size1new)
        size2new = floor(size2new)
        size_new = (size1new, size2new)
        image = image.resize(size_new)
    else:
        image.thumbnail(maxsize)

    return image
