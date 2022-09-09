# -*- coding: utf-8 -*-
import subprocess
from os import listdir, mkdir, remove
from os.path import exists, sep
from re import compile as regex_compile
from sys import executable
from tempfile import TemporaryDirectory

import requests
from pagermaid.listener import listener
from pagermaid.utils import alias_command
from telethon.tl.types import DocumentAttributeVideo

try:
    from you_get.extractors import Bilibili, YouTube
except ModuleNotFoundError:
    subprocess.call(
        [
            executable,
            "-m",
            "pip",
            "install",
            "git+https://github.com/night-raise/you-get",
        ]
    )
    from you_get.extractors import Bilibili, YouTube


@listener(
    outgoing=True,
    command=alias_command("vdl"),
    description="下载 YouTube/bilibili 视频并上传",
    parameters="<url>",
)
async def vdl(context):
    url = context.arguments.strip()
    if url.find("哔哩哔哩") != -1:
        url = "https" + url.split("https")[1]

    reply = await context.get_reply_message()
    reply_id = None
    await context.edit("视频获取中 . . .")
    if reply:
        reply_id = reply.id
    if url is None:
        await context.edit("出错了呜呜呜 ~ 无效的参数。")
        return

    if url.find("https") == -1:
        if url.find("http") == -1:
            url = "https://" + url
        else:
            url = url.replace("http", "https", 1)

    if url.find("https://m.") != -1:
        url = url.replace("https://m.", "https://www.", 1)

    bilibili_pattern = regex_compile(
        r"^(http(s)?://)?((((w){3}\.|m\.)bilibili(\.com))|b23.tv)/.+"
    )
    youtube_pattern = regex_compile(
        r"^(http(s)?://)?((w){3}\.)?youtu(be|.be)?(\.com)?/.+"
    )

    if youtube_pattern.match(url):
        url = url.replace("www.youtube.com/watch?v=", "youtu.be/")
        if not await youtube_dl(url, context, reply_id):
            await context.edit("出错了呜呜呜 ~ 视频下载失败。")
    elif bilibili_pattern.match(url):
        if not await bilibili_dl(url, context, reply_id):
            await context.edit("出错了呜呜呜 ~ 视频下载失败。")
    else:
        await context.edit("出错了呜呜呜 ~ 无效的网址。")


async def youtube_dl(url, context, reply_id):
    await context.edit("链接解析中 . . .")
    # from you_get.common import parse_host
    # from you_get.common import set_proxy
    # set_proxy(parse_host("localhost:7890"))
    downloader = YouTube(url)
    downloader.prepare()
    return await do_download(context, downloader, reply_id)


async def bilibili_dl(url, context, reply_id):
    await context.edit("链接解析中 . . .")
    if url.find("b23.tv") != -1:
        url = requests.get(url).url.split("?")[0]
    else:
        url = url.split("?")[0]
    downloader = Bilibili(url)
    downloader.prepare(playlist=True)
    try:
        if downloader.pn == 1:
            raise AttributeError

        await context.edit("视频下载中 . . .")
        for pi in range(1, downloader.pn + 1):
            downloader.url = f"{url}?p={pi}"
            downloader.prepare(playlist=True)
            await do_download(context, downloader, reply_id, edit_message=False)
        await context.delete()
        return True
    except AttributeError:
        return await do_download(context, downloader, reply_id)


async def do_download(context, downloader, reply_id, edit_message=True):
    edit_message and await context.edit("视频下载中 . . .")
    downloader.extract()
    downloader.dash_streams = dict(
        filter(lambda x: x[1]["size"] <= 157286400, downloader.dash_streams.items())
    )
    if not downloader.dash_streams:
        edit_message and await context.edit("视频都太大了，服务器可能处理不过来呢 . . .")
        return True
    file_ext = set(map(lambda x: x[1]["container"], downloader.dash_streams.items()))
    with TemporaryDirectory() as tmp_dir:
        downloader.download(output_dir=tmp_dir, merge=True)
        files = list(map(lambda x: tmp_dir + sep + x, listdir(tmp_dir)))
        for file in filter(lambda x: x.split(".")[-1] in file_ext, files):
            edit_message and await context.edit("视频上传中 . . .")
            await upload(
                True,
                file,
                context,
                reply_id,
                f"origin: {downloader.url}\n"
                f"{downloader.title} \n"
                f"#{downloader.name} #video #{file.split('.')[-1]}",
            )
            edit_message and await context.delete()
            return True
        else:
            edit_message and await context.edit("视频不见了哎？！")
    return True


async def upload(as_file, filename, context, reply_id, caption, duration=0):
    if not exists("plugins/VideoDLExtra/FastTelethon.py"):
        if not exists("plugins/VideoDLExtra"):
            mkdir("plugins/VideoDLExtra")
        faster = requests.request(
            "GET",
            "https://gist.githubusercontent.com/TNTcraftHIM/ca2e6066ed5892f67947eb2289dd6439/raw"
            "/86244b02c7824a3ca32ce01b2649f5d9badd2e49/FastTelethon.py",
        )
        for _ in range(6):  # 最多尝试6次
            if faster.status_code == 200:
                with open("plugins/VideoDLExtra/FastTelethon.py", "wb") as f:
                    f.write(faster.content)
                    break
    try:
        from VideoDLExtra.FastTelethon import upload_file

        file = await upload_file(context.client, open(filename, "rb"), filename)
    except:
        file = filename
        await context.client.send_message(
            context.chat_id, "(`FastTelethon`支持文件导入失败，上传速度可能受到影响)"
        )
    if as_file is True:
        await context.client.send_file(
            context.chat_id,
            file,
            caption=caption,
            link_preview=False,
            force_document=False,
            attributes=(DocumentAttributeVideo(duration, 0, 0),),
            reply_to=reply_id,
        )
    else:
        await context.client.send_file(
            context.chat_id,
            file,
            caption=caption,
            link_preview=False,
            force_document=False,
            attributes=(DocumentAttributeVideo(duration, 0, 0),),
            reply_to=reply_id,
        )
    remove(filename)
