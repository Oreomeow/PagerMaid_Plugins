import re
from urllib.parse import quote

import requests
from pagermaid.listener import listener
from pagermaid.utils import alias_command, pip_install

pip_install("bs4")
from bs4 import BeautifulSoup


def get_html_text(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36 Edg/99.0.1150.39",
        "Content-type": "text/html; charset=utf-8",
    }
    return requests.get(url, headers=headers).text


def get_cmds():
    html_text = get_html_text("https://wangchujiang.com/linux-command/hot.html")
    soup = BeautifulSoup(html_text, "html.parser")
    return [
        f'> [{x.text}](https://wangchujiang.com/linux-command/{x.a["href"]})'
        for x in soup("li")
    ]


def get_laws():
    html_text = get_html_text("https://lawbook.cf/")
    soup = BeautifulSoup(html_text, "html.parser")
    return [
        f'· [{x["href"].split("/")[1].rstrip(".html")}](https://lawbook.cf/{quote(x["href"])})'
        for x in soup("a", {"href": re.compile("^((?!0-README).)*html$")})
    ]


def get_regs():
    html_text = get_html_text(
        "https://github.com/Oreomeow/Law-Book2/blob/main/src/SUMMARY.md"
    )
    soup = BeautifulSoup(html_text, "html.parser")
    return [
        f'* [{x.text}]({x["href"].replace("/Oreomeow/Law-Book2/blob/main/src/","https://oreomeow.github.io/Law-Book2/").replace("md","html")})'
        for x in soup("a", {"href": re.compile("^((?!README).)*md$")})
    ]


@listener(
    is_plugin=True,
    outgoing=True,
    command=alias_command("cmd"),
    description="Linux 命令大全",
    parameters="<keyword>",
)
async def cmd(context):
    keyword = context.arguments
    url = f"https://wangchujiang.com/linux-command/c/{keyword}.html"
    code = requests.get(url).status_code
    if code == 200:
        await context.edit(f"[{keyword}]({url})", link_preview=True)
    else:
        cmds = get_cmds()
        sugs = filter(lambda x: keyword in x, cmds)
        sugs_text = "\n".join(sugs)
        await context.edit(f"**`{keyword}` 相关命令如下：**\n{sugs_text}")


@listener(
    is_plugin=True,
    outgoing=True,
    command=alias_command("law"),
    description="中国常用法律查询手册 | Law-Book",
    parameters="<keyword>",
)
async def law(context):
    keyword = context.arguments
    laws = get_laws()
    sugs = filter(lambda x: keyword in x, laws)
    sugs_text = "\n".join(sugs)
    await context.edit(f"**`{keyword}` 相关法律如下：**\n{sugs_text}")


@listener(
    is_plugin=True,
    outgoing=True,
    command=alias_command("reg"),
    description="司法解释、法规等 | Law-Book2",
    parameters="<keyword>",
)
async def reg(context):
    keyword = context.arguments
    regs = get_regs()
    sugs = filter(lambda x: keyword in x, regs)
    sugs_text = "\n".join(sugs)
    await context.edit(f"**`{keyword}` 相关法规如下：**\n{sugs_text}")
