from magic_google import MagicGoogle
from pagermaid import log, silent
from pagermaid.listener import config, listener
from pagermaid.utils import alias_command, lang, obtain_message


@listener(
    is_plugin=True,
    outgoing=True,
    command=alias_command("gg"),
    description=lang("google_des"),
    parameters="<query>",
)
async def googleplus(context):
    """Searches Google for a string."""
    PROXIES = [
        {
            "http": "socks5://woiden_oreo:woiden@sg-socks5.woiden.net:8080",
            "https": "socks5://woiden_oreo:woiden@sg-socks5.woiden.net:8080",
        }
    ]
    mg = MagicGoogle()
    try:
        query = await obtain_message(context)
    except ValueError:
        return await context.edit(lang("arg_error"))
    query = query.replace(" ", "+")

    if not silent:
        await context.edit(lang("google_processing"))

    results = ""
    for i in mg.search(query=query, num=int(config["result_length"])):
        try:
            title = i["text"][:30] + "..."
            link = i["url"]
            results += f"\n[{title}]({link}) \n"
        except Exception:
            return await context.edit(lang("google_connection_error"))
    await context.edit(
        f"**Google** |`{query}`| 🎙 🔍 \n" f"{results}", link_preview=False
    )
    await log(f'{lang("google_success")} `{query}`')
