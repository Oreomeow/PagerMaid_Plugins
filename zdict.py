from pagermaid.listener import listener
from pagermaid.utils import alias_command, attach_log, execute, pip_install

pip_install("zdict")


@listener(
    is_plugin=True,
    outgoing=True,
    command=alias_command("zdict"),
    description="The last online dictionary CLI framework you need.",
    parameters="<word>",
)
async def zdict(context):
    word = context.arguments
    result = await execute(f"zdict {word}")

    if len(result) > 4096:
        return await attach_log(result, context.chat_id, f"{word}.txt", context.id)
    await context.edit(result)
