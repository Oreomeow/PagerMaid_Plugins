from pagermaid import log, silent
from pagermaid.listener import listener
from pagermaid.utils import alias_command, lang, obtain_message, pip_install

pip_install("baidusearch")
from baidusearch.baidusearch import search


@listener(
    is_plugin=True,
    outgoing=True,
    command=alias_command("baidu"),
    description=lang("google_des").replace("Google", "Baidu"),
    parameters="<query>",
)
async def baidu(context):
    try:
        query = await obtain_message(context)
    except ValueError:
        return await context.edit(lang("arg_error"))
    query = query.replace(" ", "+")

    if not silent:
        await context.edit(lang("google_processing"))

    results = ""
    for i in search(query):
        try:
            link = i["url"]
            if "http" not in link:
                continue
            title = i["title"][0:30] + "..."
            results += f"\n[{title}]({link}) \n"
        except:
            return await context.edit(
                lang("google_connection_error").replace("google", "baidu")
            )
    await context.edit(f"**Baidu** |`{query}`| 🎙 👣 \n" f"{results}", link_preview=False)
    await log(f'{lang("google_success").replace("Google", "Baidu")} `{query}`')
