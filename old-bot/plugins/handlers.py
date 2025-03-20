from pyrogram import Client, Filters, InlineQuery, Message, InlineQueryResultArticle, InputTextMessageContent, \
    InlineKeyboardMarkup, InlineKeyboardButton
from lark import Lark, ParseError, UnexpectedInput
from plugins import dice_roller

BOT_USERNAME = "iactabot"


@Client.on_message(Filters.command(["help", f"help@{BOT_USERNAME}", "start", f"start@{BOT_USERNAME}"]))
def info(client: Client, message: Message):
    message.reply("Hi, I'm the Cast an' Roll bot! I can roll any complex combination of any type of dice. You can "
                  "also use the inline mode in any chat, typing @iactabot followed by a __dice formula__\n\n"
                  "/roll - execute a __dice formula__. In can contain any combination of dice groups written in the "
                  "form `3d6` or `d20`, numeric modifiers, operations `+`,`-`,`*`,`/` or parenthesis `()`. For each "
                  "dice group you can also drop a certain number of the lowest rolls, or keep only a certain number "
                  "of the highest rolls. This bot supports this type of roll through the `d` and `k` commands, "
                  "respectively. For example `8d40k3` will keep the 3 highest rolls. The `d` and `k` commands are "
                  "shortcuts for the full `dl` and `kh` commands. If you need to drop the highest dice use `dh` and "
                  "if you need to keep the lowest dice use `kl`")


@Client.on_message(Filters.command(["roll", f"roll@{BOT_USERNAME}"]))
def message_roll(client: Client, message: Message):
    query = ''.join(message.command[1:])
    try:
        result, summary = roll_query(query)
        if len(summary) > 4000:
            summary = "[...too long...]"
        message.reply(f"**{result}**  =  {summary}")
    except (UnexpectedInput, AttributeError):
        message.reply("That's a strange request 🤔")
    except TimeoutError:
        message.reply("Too difficult to calculate 😩")
    except ParseError:
        message.reply("Maybe you need the /help command?")


@Client.on_inline_query()
def inline_roll(client: Client, inline_query: InlineQuery):
    query = ''.join(inline_query.query.split())
    try:
        result, summary = roll_query(query)
        if len(query) + len(summary) > 4000:
            summary = "[...too long...]"
        inline_query.answer([
            InlineQueryResultArticle(
                title="Roll your dice!",
                input_message_content=InputTextMessageContent(
                    f"__{query}:__\n**{result}**  =  {summary}"
                ),
                thumb_url="https://i.imgur.com/tSLPGZC.png",
                description=query,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton(
                            "Re-roll!",
                            switch_inline_query_current_chat=query)]
                    ]
                )
            )
        ], cache_time=0)
    except (UnexpectedInput, ParseError, AttributeError):
        pass


@Client.on_message(Filters.command(["rickroll", f"rickroll@{BOT_USERNAME}"]))
def rickroll(client: Client, message: Message):
    message.reply("http://tinyurl.com/2g9mqh")


def roll_query(query: str):
    syntax_tree = Lark(dice_roller.grammar).parse(query)
    return dice_roller.MyTransformer().transform(syntax_tree)
