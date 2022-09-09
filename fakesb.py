from struct import error as StructError

from pagermaid import user_id as self_user_id
from pagermaid.listener import listener
from pagermaid.utils import alias_command, lang
from telethon.errors.rpcerrorlist import (
    ChatAdminRequiredError,
    UserAdminInvalidError,
)
from telethon.tl.functions.channels import DeleteUserHistoryRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import (
    MessageEntityCode,
    MessageEntityMentionName,
    MessageEntityPhone,
    PeerChannel,
)


def mention_user(user):
    try:
        first_name = user.first_name.replace("\u2060", "")
    except AttributeError:
        first_name = "×"
    return f"[{first_name}](tg://user?id={user.id})"


def mention_group(chat):
    try:
        if chat.username:
            if chat.username:
                text = f"[{chat.title}](https://t.me/{chat.username})"
            else:
                text = f"`{chat.title}`"
        else:
            text = f"`{chat.title}`"
    except AttributeError:
        text = f"`{chat.title}`"
    return text


@listener(
    is_plugin=True,
    outgoing=True,
    command=alias_command("fakesb"),
    description=lang("sb_des"),
    parameters="<reply|id|username>",
)
async def fakesb(context):
    if context.reply_to_msg_id:
        reply_message = await context.get_reply_message()
        if reply_message:
            try:
                user = reply_message.from_id
            except AttributeError:
                await context.edit(lang("arg_error"))
                return
        else:
            await context.edit(lang("arg_error"))
            return
        if isinstance(user, PeerChannel):
            # 封禁频道
            try:
                user = await context.client.get_input_entity(reply_message.sender.id)
            except ChatAdminRequiredError:
                return await context.edit(lang("sb_no_per"))
            return await context.edit(lang("sb_channel"))
        elif not user:
            return await context.edit(lang("arg_error"))
        target_user = await context.client(GetFullUserRequest(user))
    else:
        if len(context.parameter) == 1:
            user = context.parameter[0].strip("`")
            if user.isnumeric():
                user = int(user)
                if user < 0:
                    return await context.edit(lang("arg_error"))
        else:
            return await context.edit(lang("arg_error"))
        if context.message.entities is not None:
            if isinstance(context.message.entities[0], MessageEntityMentionName):
                user = context.message.entities[0].user_id
            elif isinstance(context.message.entities[0], MessageEntityPhone):
                user = int(context.parameter[0])
            elif isinstance(context.message.entities[0], MessageEntityCode):
                pass
            else:
                return await context.edit(f"{lang('error_prefix')}{lang('arg_error')}")
        try:
            user_object = await context.client.get_entity(user)
            target_user = await context.client(GetFullUserRequest(user_object.id))
        except (TypeError, ValueError, OverflowError, StructError) as exception:
            if str(exception).startswith("Cannot find any entity corresponding to"):
                await context.edit(f"{lang('error_prefix')}{lang('profile_e_no')}")
                return
            if str(exception).startswith("No user has"):
                await context.edit(f"{lang('error_prefix')}{lang('profile_e_nou')}")
                return
            if str(exception).startswith(
                "Could not find the input entity for"
            ) or isinstance(exception, StructError):
                await context.edit(f"{lang('error_prefix')}{lang('profile_e_nof')}")
                return
            if isinstance(exception, OverflowError):
                await context.edit(f"{lang('error_prefix')}{lang('profile_e_long')}")
                return
            raise exception
    chat = await context.get_chat()
    if len(context.parameter) == 0:
        try:
            await context.client(
                DeleteUserHistoryRequest(channel=chat, user_id=target_user)
            )
        except UserAdminInvalidError:
            pass
        except ChatAdminRequiredError:
            pass
    if target_user.user.id == self_user_id:
        await context.edit(lang("arg_error"))
        return
    if len(context.parameter) == 0:
        text = (
            f'{lang("sb_per")} 114514 {lang("sb_in")} {mention_user(target_user.user)}'
        )
    elif context.parameter[0] == 0:
        text = f'{lang("sb_no")} {mention_user(target_user.user)}'
    else:
        text = f'{lang("sb_per")} {context.parameter[0]} {lang("sb_in")} {mention_user(target_user.user)}'
    await context.edit(text)
