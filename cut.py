import contextlib
import re
import subprocess
import time
from os import remove

from pagermaid import bot
from pagermaid.listener import listener
from pagermaid.utils import alias_command, obtain_message, pip_install

pip_install("selenium")
pip_install("webdriver_manager")
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


def check_chrome():
    if subprocess.call(["which", "google-chrome"]):
        subprocess.call(
            [
                "wget -N https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && apt install -y -f ./google-chrome-stable_current_amd64.deb && rm google-chrome-stable_current_amd64.deb",
            ],
            shell=True,
        )
        return subprocess.call(["which", "google-chrome"])


def get_screenshot(url, file_path, fullscreen=False):
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-notifications")
    options.add_argument("--headless")
    options.add_argument("--hide-scrollbars")
    options.add_argument("--no-sandbox")
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    driver.get(url)
    with contextlib.suppress(Exception):
        driver.find_element(
            By.XPATH, '//button[@class="Button Modal-closeButton Button--plain"]'
        ).click()
    if not fullscreen:
        width = "1920"
        height = "1080"
    else:
        width = driver.execute_script(
            "return Math.max(document.body.scrollWidth, document.body.offsetWidth, document.documentElement.clientWidth, document.documentElement.scrollWidth, document.documentElement.offsetWidth);"
        )
        height = driver.execute_script(
            "return Math.max(document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight);"
        )
    driver.set_window_size(width, height)
    time.sleep(5)
    driver.get_screenshot_as_file(file_path)
    driver.close()


@listener(
    is_plugin=True,
    outgoing=True,
    command=alias_command("cut"),
    description="Web Page Screenshot ????????????",
    parameters="<url>",
)
async def cut(context):
    await context.edit("Processing . . .")
    if check_chrome():
        return await context.edit(
            "Package google-chrome-stable failed to install automatically, please install google-chrome browser by yourself.\n????????? google-chrome-stable ???????????????????????????????????? google-chrome ????????????"
        )
    message = await obtain_message(context)
    url_regex = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
    url = re.findall(url_regex, message)
    if url:
        url = url[0].rstrip(")")
    else:
        return await context.edit(
            "The message does not contain a link, please check.\n???????????????????????????????????????"
        )
    file_path = f'data/{time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))}.png'
    get_screenshot(url, file_path)
    await context.edit(f"[Web]({url}) preview below\n??????????????????")
    await bot.send_file(context.chat_id, file_path)
    remove(file_path)


@listener(
    is_plugin=True,
    outgoing=True,
    command=alias_command("cut_"),
    description="Web Page Screenshot & Save ?????????????????????",
    parameters="<url>",
)
async def cut_(context):
    await context.edit("Processing . . .")
    if check_chrome():
        return await context.edit(
            "Package google-chrome-stable failed to install automatically, please install google-chrome browser by yourself.\n????????? google-chrome-stable ???????????????????????????????????? google-chrome ????????????"
        )
    message = await obtain_message(context)
    url_regex = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
    url = re.findall(url_regex, message)
    if url:
        url = url[0].rstrip(")")
    else:
        return await context.edit(
            "The message does not contain a link, please check.\n???????????????????????????????????????"
        )
    file_path = f'data/{time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))}.png'
    get_screenshot(url, file_path)
    await context.edit(f"[Web]({url}) preview below\n??????????????????")
    await bot.send_file(context.chat_id, file_path)


@listener(
    is_plugin=True,
    outgoing=True,
    command=alias_command("cuta"),
    description="Web Page Full Screenshot ??????????????????",
    parameters="<url>",
)
async def cut_fullscreen(context):
    await context.edit("Processing . . .")
    if check_chrome():
        return await context.edit(
            "Package google-chrome-stable failed to install automatically, please install google-chrome browser by yourself.\n????????? google-chrome-stable ???????????????????????????????????? google-chrome ????????????"
        )
    message = await obtain_message(context)
    url_regex = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
    url = re.findall(url_regex, message)
    if url:
        url = url[0].rstrip(")")
    else:
        return await context.edit(
            "The message does not contain a link, please check.\n???????????????????????????????????????"
        )
    file_path = f'data/{time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))}.png'
    get_screenshot(url, file_path, True)
    await context.edit(f"[Web]({url}) preview below\n??????????????????")
    await bot.send_file(context.chat_id, file_path, force_document=True)
    remove(file_path)


@listener(
    is_plugin=True,
    outgoing=True,
    command=alias_command("cuta_"),
    description="Web Page Full Screenshot & Save ???????????????????????????",
    parameters="<url>",
)
async def cut_fullscreen_(context):
    await context.edit("Processing . . .")
    if check_chrome():
        return await context.edit(
            "Package google-chrome-stable failed to install automatically, please install google-chrome browser by yourself.\n????????? google-chrome-stable ???????????????????????????????????? google-chrome ????????????"
        )
    message = await obtain_message(context)
    url_regex = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
    url = re.findall(url_regex, message)
    if url:
        url = url[0].rstrip(")")
    else:
        return await context.edit(
            "The message does not contain a link, please check.\n???????????????????????????????????????"
        )
    file_path = f'data/{time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))}.png'
    get_screenshot(url, file_path, True)
    await context.edit(f"[Web]({url}) preview below\n??????????????????")
    await bot.send_file(context.chat_id, file_path, force_document=True)
