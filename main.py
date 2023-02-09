from pyrogram import Client, filters

import logging
from time import sleep
from configparser import ConfigParser


logging.basicConfig(
    format="[%(levelname)s] %(message)s",
    level=logging.INFO
)

# program body
app = Client("controller")
config = ConfigParser()
config.read("config.ini")
CHANNEL_ID = config.getint('bot', 'channel_id', fallback=0)


# post homework
@app.on_message(filters.command(["homework", "hw"]) & filters.chat(CHANNEL_ID))
def f(_, message):
    message.delete()
    args = message.text.split()
    if len(args) <= 1:
        msg = app.send_message(message.chat.id, "Не введены предметы")
        sleep(2)
        msg.delete()
        return 0

    args = args[1:]  # delete prefix of command

    hw_for_tomorrow = dict()
    for arg in args:
        arg = arg.replace("-", " ")

        b = False
        for leftAdd in ["**", ""]:
            for rightAdd in ["**", ""]:
                findArg = leftAdd + arg + rightAdd
                last_arg = list(app.search_messages(message.chat.id, findArg, limit=1))
                arg = arg.lower()
                if not last_arg:
                    continue
                for msg in last_arg:
                    i = 0
                    text = msg.text or msg.caption
                    while text[i:i+len(arg)].lower() != arg and i < len(text):  # поиск предмета в сообщении
                        i += 1
                    if i == len(text):
                        continue
                    while text[i-1] != '\n' and i > 0:
                        i -= 1
                    start_name = i
                    while text[i] != '\n' and i < len(text):  # переход на следующую строку
                        i += 1
                    if i == len(text):
                        continue
                    end_name = i
                    name = text[start_name:end_name]
                    i += 1
                    start_pos = i
                    while text[i] != '\n' and i < len(text)-1:  # передвижение курсора до конца задания
                        i += 1
                    if text[i] == '\n':
                        i -= 1
                    end_pos = i+1
                    hw = text[start_pos:end_pos]
                    hw_for_tomorrow[name] = hw

                    b = True
                    break
                if b:
                    break
            if b:
                break
        if not b:
            msg = app.send_message(message.chat.id, f"Нет записей про {arg}")
            sleep(2)
            msg.delete()
    res_msg_text = "**Домашнее задание**"
    for name, hw in hw_for_tomorrow.items():
        res_msg_text += f"\n\n**{name}**\n{hw}"
    app.send_message(message.chat.id, res_msg_text)


@app.on_message(filters.command("getId") & filters.me)
def f(_, msg):
    msg.edit(msg.chat.id)


app.run()
