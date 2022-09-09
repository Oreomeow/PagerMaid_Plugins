from pagermaid.listener import listener
from pagermaid.utils import alias_command, attach_log, execute


@listener(
    is_plugin=True,
    outgoing=True,
    command=alias_command("route"),
    description="BestTrace 回程路由追踪",
    parameters="<ip>",
)
async def route(context):
    reply = await context.get_reply_message()
    ip = context.arguments
    if ip:
        pass
    elif reply:
        ip = reply.text
    result = await execute(
        f"mkdir -p plugins/iptool && cd plugins/iptool && wget -q https://raw.githubusercontent.com/fscarmen/tools/main/return_pure.sh -O route.sh && bash route.sh {ip}"
    )
    if len(result) > 4096:
        return await attach_log(result, context.chat_id, f"{ip}.txt", context.id)
    await context.edit(result)


@listener(
    is_plugin=True,
    outgoing=True,
    command=alias_command("port"),
    description="ping.pe 查看 IP 端口是否被墙",
    parameters="<IPv4:PORT> or <[IPv6]:PORT>",
)
async def port(context):
    reply = await context.get_reply_message()
    ipport = context.arguments
    if ipport:
        pass
    elif reply:
        ipport = reply.text
    result = await execute(
        f"mkdir -p plugins/iptool && cd plugins/iptool && wget -q https://raw.githubusercontent.com/fscarmen/tools/main/port_pure.sh -O port.sh && bash port.sh {ipport}"
    )
    if len(result) > 4096:
        return await attach_log(result, context.chat_id, f"{ip}.txt", context.id)
    await context.edit(result)
