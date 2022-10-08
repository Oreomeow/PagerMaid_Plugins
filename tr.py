from pagermaid.listener import listener
from pagermaid.utils import alias_command, attach_log, lang
from requests import post

DES = """Request the self-built DeepL API interface to get translations.  
请求自建的 DeepL API 接口实现翻译。  

**Language Supported:**  
```
• DE: German      德语  
• EN: English     英语  
• ES: Spanish     西班牙语  
• FR: French      法语  
• IT: Italian     意大利语  
• JA: Japanese    日语  
• NL: Dutch       荷兰语  
• PL: Polish      波兰语  
• PT: Portuguese  葡萄牙语  
• RU: Russian     俄语  
• ZH: Chinese     中文  
• BG: Bulgarian   保加利亚语  
• CS: Czech       捷克语  
• DA: Danish      丹麦语  
• EL: Greek       希腊语  
• ET: Estonian    爱沙尼亚语  
• FI: Finnish     芬兰语  
• HU: Hungarian   匈牙利语  
• LT: Lithuanian  立陶宛语  
• LV: Latvian     拉脱维亚语  
• RO: Romanian    罗马尼亚语  
• SK: Slovak      斯洛伐克语  
• SL: Slovenian   斯洛文尼亚语  
• SV: Swedish     瑞典语  
```"""


def translate(target_lang, text):
    try:
        headers = {
            "Content-Type": "application/json",
        }
        json = {
            "text": "".join(
                [l + "\n" if l != "\n" else l for l in text.splitlines(True)]
            ),
            "source_lang": "auto",
            "target_lang": target_lang,
        }
        res = post(
            url="Place your own DeepL api interface here",
            headers=headers,
            json=json,
            timeout=20,
        ).json()
        if res["code"] == 200:
            return "".join(
                [l if l != "" else l + "\n" for l in res["data"].splitlines()]
            )
        else:
            return res["msg"]
    except Exception as e:
        return str(e)


@listener(
    is_plugin=True,
    outgoing=True,
    command=alias_command("tr"),
    description=DES,
    parameters="<target_lang> <text>",
)
async def tr(context):
    reply = await context.get_reply_message()
    if params := context.parameter:
        if reply:
            target_lang = params[0].replace(" ", "").upper()
            text = reply.text
        elif len(params) > 1:
            target_lang = params[0].upper()
            text = "".join(params[1:])
        else:
            return await context.edit(lang("arg_error"))
    result = translate(target_lang, text)

    if len(result) > 4096:
        return await attach_log(result, context.chat_id, "tr.txt", context.id)
    await context.edit(result)


@listener(
    is_plugin=True,
    outgoing=True,
    command=alias_command("en"),
    description="DeepL API translate: auto -> EN",
    parameters="<text>",
)
async def en(context):
    reply = await context.get_reply_message()
    text = context.arguments
    if text:
        pass
    elif reply:
        text = reply.text
    else:
        return await context.edit(lang("arg_error"))
    result = translate("EN", text)

    if len(result) > 4096:
        return await attach_log(result, context.chat_id, "en.txt", context.id)
    await context.edit(result)


@listener(
    is_plugin=True,
    outgoing=True,
    command=alias_command("zh"),
    description="DeepL API translate: auto -> ZH",
    parameters="<text>",
)
async def zh(context):
    reply = await context.get_reply_message()
    text = context.arguments
    if text:
        pass
    elif reply:
        text = reply.text
    else:
        return await context.edit(lang("arg_error"))
    result = translate("ZH", text)

    if len(result) > 4096:
        return await attach_log(result, context.chat_id, "zh.txt", context.id)
    await context.edit(result)
