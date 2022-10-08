from urllib.parse import quote, unquote

from pagermaid.listener import listener
from pagermaid.utils import alias_command, attach_log, lang, obtain_message


@listener(
    is_plugin=True,
    outgoing=True,
    command=alias_command("quote"),
    description="encodeURI",
    parameters="<text>",
)
async def encode_url(context):
    try:
        msg = await obtain_message(context)
    except Exception:
        return await context.edit(lang("arg_error"))

    result = quote(msg, safe=":/")

    if len(result) > 4096:
        return await attach_log(result, context.chat_id, "output.txt", context.id)
    await context.edit(result)


@listener(
    is_plugin=True,
    outgoing=True,
    command=alias_command("unquote"),
    description="decodeURI",
    parameters="<text>",
)
async def decode_url(context):
    try:
        msg = await obtain_message(context)
    except Exception:
        return await context.edit(lang("arg_error"))

    result = unquote(msg)

    if len(result) > 4096:
        return await attach_log(result, context.chat_id, "output.txt", context.id)
    await context.edit(result)
