from pagermaid import bot
from pagermaid.listener import listener
from pagermaid.utils import alias_command, lang


@listener(
    is_plugin=True,
    outgoing=True,
    command=alias_command("v2p"),
    description="Docking self-built V2Pbot. 对接自建 V2P 机器人。",
    parameters="<cmd>",
)
async def v2p(context):
    cmd = context.arguments
    if not cmd:
        return await context.edit(lang("arg_error"))
    async with bot.conversation("V2Phelper_bot") as conversation:
        await conversation.send_message(cmd)
        chat_response = await conversation.get_response()
        await bot.send_read_acknowledge(conversation.chat_id)
        v2p_text = chat_response.text
    await context.edit(v2p_text, parse_mode="html")
