from pagermaid import bot
from pagermaid.listener import listener
from pagermaid.utils import alias_command, attach_log, lang


@listener(
    is_plugin=True,
    outgoing=True,
    command=alias_command("parse"),
    description="Parse Mode Test",
    parameters="(<h/m/n/nh/nm>) <message>",
)
async def parse(context):
    reply = await context.get_reply_message()
    mode = context.arguments.replace(" ", "")
    if not reply:
        return await context.edit("Please reply to a message.\n请回复一条消息。")
    if not mode or mode == "h":
        bot.parse_mode = "html"
        edit_mode = None
    elif mode == "m":
        bot.parse_mode = "markdown"
        edit_mode = None
    elif mode == "n":
        bot.parse_mode = None
        edit_mode = None
    elif mode == "nh":
        bot.parse_mode = None
        edit_mode = "html"
    elif mode == "nm":
        bot.parse_mode = None
        edit_mode = "markdown"
    else:
        return await context.edit(lang("arg_error"))

    if len(reply.text) > 4096:
        return await attach_log(reply.text, context.chat_id, "parse.txt", context.id)
    await bot.edit_message(
        context.chat_id, context.id, reply.text, parse_mode=edit_mode
    )
    bot.parse_mode = "markdown"
