from pyrogram import Client
from pyrogram import filters

import logging
from time import sleep
from dotenv import load_dotenv
from os import getenv


logging.basicConfig(
        format="[%(levelname)s] %(message)s",
        level=logging.INFO
)

# get .env constants
load_dotenv()

CHANNEL_ID = int(getenv("CHANNEL_ID"))

# program body
app = Client("controller")
moderators = [1210453612, 1096006718, 1138946626]

# post homework
@app.on_message(filters.command(["homework", "hw"]) & (filters.user(moderators) | filters.chat(CHANNEL_ID)))
def f(_, message):
    message.delete()
    args = message.text.split()
    if len(args) <= 1:
        msg = app.send_message(message.chat.id, "Не введены предметы")
        sleep(1)
        msg.delete()
        return 0

    args = args[1:]  # delete prefix of command

    hw_for_tomorrow = dict()
    for arg in args:
        for s in range(len(arg)):
            if arg[s] == "-":
                arg = arg[:s] + " " + arg[s+1:]
                
        b = False
        for leftAdd in ["**", ""]:
            for rightAdd in ["**", ""]:
                findArg = leftAdd + arg + rightAdd
                last_arg = list(app.search_messages(CHANNEL_ID, findArg, limit=1))
                arg = arg.lower()
                if not last_arg:
                    continue
                for msg in last_arg:
                    i = 0
                    while msg.text[i:i+len(arg)].lower() != arg:  # поиск предмета в сообщении
                        i += 1
                    while msg.text[i-1] != '\n' and i > 0:
                        i -= 1
                    start_name = i
                    while msg.text[i] != '\n':  # переход на следующую строку
                        i += 1
                    end_name = i
                    name = msg.text[start_name:end_name]
                    i += 1
                    start_pos = i
                    while msg.text[i] != '\n' and i < len(msg.text)-1:  # передвижение курсора до конца задания
                        i += 1
                    if msg.text[i] == '\n':
                        i -= 1
                    end_pos = i+1
                    hw = msg.text[start_pos:end_pos]
                    hw_for_tomorrow[name] = hw

                    b = True
                if b:
                    break
            if b:
                break
        if not b:
            msg = app.send_message(message.chat.id, f"Нет записей про {arg}")
            sleep(1)
            msg.delete()
    res_msg_text = "**Домашнее задание**"
    for name, hw in hw_for_tomorrow.items():
        res_msg_text += f"\n\n**{name}**\n{hw}"
    app.send_message(CHANNEL_ID, res_msg_text)


app.run()
