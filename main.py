'''from pyrogram import Client, filters
import logging
from time import sleep
from configparser import ConfigParser
import datetime
import requests


english_Tahmina = "тахмины"
english_Elena = "елены"
history = "история"
russian = "русский"
physics = "физика"
geometry = "геометрия"
literature = "литература"
algebra = "алгебра"
geography = "география"
biology = "биология"
chemistry = "химия"
social_study = "обществознание"
informatics_Tatiana = "татьяны"
informatics_Maria = "марии"
informatics_Leo = "льва"
informatics_Anton = "антона"
FoLS = "обж"
subjects_for_day = [[social_study, english_Tahmina, english_Elena, algebra, literature, history],  # понедельник
                    [russian, geometry, biology],  # вторник
                    [algebra, english_Tahmina, english_Elena, geometry, russian, geography, literature],  # среда
                    [algebra, history, social_study],  # четверг
                    [geometry, informatics_Tatiana, literature, chemistry, english_Tahmina, english_Elena]]  # пятница
full_subjects_names = {english_Tahmina: "Английский язык (группа Тахмины)",
                       english_Elena: "Английский язык (группа Елены)",
                       history: "История",
                       russian: "Русский язык",
                       physics: "Физика",
                       geometry: "Геометрия",
                       literature: "Литература",
                       algebra: "Алгебра",
                       geography: "География",
                       biology: "Биология",
                       chemistry: "Химия",
                       social_study: "Обществознание",
                       informatics_Tatiana: "Информатика (группа Татьяны)",
                       informatics_Maria: "Информатика (группа Марии)",
                       informatics_Leo: "Информатика (группа Льва)",
                       informatics_Anton: "Информатика (группа Антона)",
                       FoLS: "ОБЖ"}
work_day_start_time = ["8:00", "8:50", "9:50", "10:50", "11:50"]
work_day_finish_time = ["8:40", "9:30", "10:30", "11:30", "12:30", "13:20", "14:10", "15:10"]
next_day = ["на вторник", "на среду", "на четверг", "на пятницу", "на понедельник"]

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
    today = get_week_day()
    args = message.text.split()
    args = args[1:]
    subjects = input_handle((subjects_for_day[(today + 1) % 5]), args)
    hw_for_tomorrow = dict()

    for arg in subjects:
        # поиск сообщений с упоминанием предмета
        messages_with_subject = []
        for left_add in ["**", ""]:
            for right_add in ["**", ""]:
                find_arg = left_add + arg + right_add
                messages_with_subject = list(app.search_messages(CHANNEL_ID, find_arg, limit=10)) + messages_with_subject


        # поиск домашнего задания в сообщении
        hw_find = False
        j = 0
        while not hw_find:
            msg = messages_with_subject[j]
            j += 1
            # проверка на то, что сообщение - текст (не фото, не документ)
            if msg.text == None:
                continue
            # проверка на то, что сообщение - дз
            if "Домашние задания" not in msg.text:
                continue
            # поиск предмета в сообщении
            i = 0
            while msg.text[i:i + len(arg)].lower() != arg and i < len(msg.text):
                i += 1
            if i == len(msg.text):
                continue
            # поиск начала заглавия домашнего задания
            while msg.text[i - 1] != '\n' and i > 0:
                i -= 1
            start_name = i
            # поиск конца заглавия домашнего задания
            while msg.text[i] != '\n' and i < len(msg.text):
                i += 1
            if i == len(msg.text):
                continue
            end_name = i
            name = msg.text[start_name:end_name]
            # начало текста домашнего задания
            i += 1
            start_pos = i
            # поиск конца текста домашнего задания
            while i < len(msg.text) - 1 and (msg.text[i] != '\n' or msg.text[i + 1] != '\n'):
                i += 1
            if msg.text[i] == '\n':
                i -= 1
            end_pos = i + 1

            hw = msg.text[start_pos:end_pos]
            hw_for_tomorrow[name] = hw
            hw_find = True

        if not hw_find:
            send_error_message(f"Нет записей про {arg}")

    res_msg_text = f"**Домашние задания {next_day[today]} ({get_next_day()})**"
    for name, hw in hw_for_tomorrow.items():
        res_msg_text += f"\n\n**{name}**\n{hw}"
    app.send_message(message.chat.id, res_msg_text)


@app.on_message(filters.command("getId") & filters.me)
def f(_, mesage):
    mesage.edit(mesage.chat.id)


@app.on_message(filters.command("sh") & filters.chat(CHANNEL_ID))
def f(_, message):
    today = get_week_day()
    label = f"**Расписание {next_day[today]} ({get_next_day()})**\nC "

    if message.text == None:
        message_text = message.caption
    else:
        message.delete()
        message_text = message.text

    if len(message_text) > 3:
        label += work_day_start_time[int(message_text[-2]) - 1] + " до " + work_day_finish_time[int(message_text[-1]) - 1]
    else:
        if today == 3:
            label += work_day_start_time[1] + " до "
        else:
            label += work_day_start_time[0] + " до "
        if today == 2 or today == 3:
            label += work_day_finish_time[7]
        else:
            label += work_day_finish_time[6]

    if message.text == None:
        message.edit(label)
    else:
        app.send_photo(CHANNEL_ID, "pensive_cat.jpg", label)


@app.on_message(filters.command("rasp") & filters.chat(CHANNEL_ID))
def f(_, message):
    date = get_next_day()
    today = get_week_day()
    req = requests.get("https://diary130.ru/api/schedule", params={"class":"10Д", "date":date}).json()
    msg = f"**Расписание {next_day[today]} ({date})**\n"
    if req["ok"]:
        for i in req["schedule"]:
            msg += "   ".join(i) + "\n"
    else:
        msg = req["error"]
    message.edit(msg)



@app.on_message(filters.command("dz") & filters.chat(CHANNEL_ID))
def f(_, message):
    message.delete()
    args = message.text.split()
    args = args[1:]
    today = get_week_day()
    subjects = input_handle(subjects_for_day[today], args)

    pattern = f"**Домашние задания ({datetime.date.today()})**"
    for i in subjects:
        if i in full_subjects_names:
            pattern += "\n\n**" + full_subjects_names[i] + "**\n."
        else:
            send_error_message("Предмета " + i + " не существует")
    app.send_message(CHANNEL_ID, pattern)


def get_week_day():
    today = datetime.date.weekday(datetime.datetime.today())
    if today > 4:
        today = 4
    return today


def get_next_day():
    today = get_week_day()
    if today == 4:
        day = 3
    else:
        day = 1
    return str(datetime.datetime.now() + datetime.timedelta(days=day)).split()[0]



def send_error_message(text):
    mesage = app.send_message(CHANNEL_ID, text)
    sleep(3)
    mesage.delete()


def input_handle(subjects, args):
    handle_subjects = subjects.copy()
    for i in args:
        if i[0] == "-":
            if i[1:] in subjects:
                handle_subjects.remove(i[1:])
            else:
                send_error_message("Предмета " + i[1:] + " нет")
        elif i not in handle_subjects:
            handle_subjects.append(i)
        else:
            send_error_message("Предмет " + i + " и так есть в этот день")
    return handle_subjects


app.run()'''







from pyrogram import Client, filters
import logging
from time import sleep
from configparser import ConfigParser
import datetime
import requests

english_Tahmina = "тахмины"
english_Elena = "елены"
history = "история"
russian = "русский"
physics = "физика"
geometry = "геометрия"
literature = "литература"
algebra = "алгебра"
geography = "география"
biology = "биология"
chemistry = "химия"
social_study = "обществознание"
informatics_Tatiana = "татьяны"
informatics_Maria = "марии"
informatics_Leo = "льва"
informatics_Anton = "антона"
FoLS = "обж"
subjects_for_day = [[social_study, english_Tahmina, english_Elena, algebra, literature, history],  # понедельник
                    [russian, geometry, biology],  # вторник
                    [algebra, english_Tahmina, english_Elena, geometry, russian, geography, literature],  # среда
                    [algebra, history, social_study],  # четверг
                    [geometry, informatics_Tatiana, literature, chemistry, english_Tahmina, english_Elena]]  # пятница
full_subjects_names = {english_Tahmina: "Английский язык (группа Тахмины)",
                       english_Elena: "Английский язык (группа Елены)",
                       history: "История",
                       russian: "Русский язык",
                       physics: "Физика",
                       geometry: "Геометрия",
                       literature: "Литература",
                       algebra: "Алгебра",
                       geography: "География",
                       biology: "Биология",
                       chemistry: "Химия",
                       social_study: "Обществознание",
                       informatics_Tatiana: "Информатика (группа Татьяны)",
                       informatics_Maria: "Информатика (группа Марии)",
                       informatics_Leo: "Информатика (группа Льва)",
                       informatics_Anton: "Информатика (группа Антона)",
                       FoLS: "ОБЖ"}
work_day_start_time = ["8:00", "8:50", "9:50", "10:50", "11:50"]
work_day_finish_time = ["8:40", "9:30", "10:30", "11:30", "12:30", "13:20", "14:10", "15:10"]
next_day = ["на вторник", "на среду", "на четверг", "на пятницу", "на понедельник"]

logging.basicConfig(
    format="[%(levelname)s] %(message)s",
    level=logging.INFO
)

# program body

config = ConfigParser()
config.read("config.ini")
CHANNEL_ID = config.getint('bot', 'channel_id', fallback=0)
app = Client(
    "controller",
    api_id=config.get("pyrogram", "api_id"),
    api_hash=config.get("pyrogram", "api_hash"))


# post homework
@app.on_message(filters.command(["homework", "hw"]) & filters.chat(CHANNEL_ID))
async def f(_, message):
    await message.delete()
    today = get_week_day()
    args = message.text.split()
    args = args[1:]
    subjects = await input_handle((subjects_for_day[(today + 1) % 5]), args)
    hw_for_tomorrow = dict()

    for arg in subjects:
        # поиск сообщений с упоминанием предмета
        messages_with_subject = []
        for left_add in ["**", ""]:
            for right_add in ["**", ""]:
                find_arg = left_add + arg + right_add
                async for mes in app.search_messages(CHANNEL_ID, find_arg, limit=10):
                    messages_with_subject.append(mes)

        # поиск домашнего задания в сообщении
        hw_find = False
        j = 0
        while not hw_find:
            msg = messages_with_subject[j]
            j += 1
            # проверка на то, что сообщение - текст (не фото, не документ)
            if msg.text == None:
                continue
            # проверка на то, что сообщение - дз
            if "Домашние задания" not in msg.text:
                continue
            # поиск предмета в сообщении
            i = 0
            while msg.text[i:i + len(arg)].lower() != arg and i < len(msg.text):
                i += 1
            if i == len(msg.text):
                continue
            # поиск начала заглавия домашнего задания
            while msg.text[i - 1] != '\n' and i > 0:
                i -= 1
            start_name = i
            # поиск конца заглавия домашнего задания
            while msg.text[i] != '\n' and i < len(msg.text):
                i += 1
            if i == len(msg.text):
                continue
            end_name = i
            name = msg.text[start_name:end_name]
            # начало текста домашнего задания
            i += 1
            start_pos = i
            # поиск конца текста домашнего задания
            while i < len(msg.text) - 1 and (msg.text[i] != '\n' or msg.text[i + 1] != '\n'):
                i += 1
            if msg.text[i] == '\n':
                i -= 1
            end_pos = i + 1

            hw = msg.text[start_pos:end_pos]
            hw_for_tomorrow[name] = hw
            hw_find = True

        if not hw_find:
            await send_error_message(f"Нет записей про {arg}")

    res_msg_text = f"**Домашние задания {next_day[today]} ({get_next_day()})**"
    for name, hw in hw_for_tomorrow.items():
        res_msg_text += f"\n\n**{name}**\n{hw}"
    await app.send_message(message.chat.id, res_msg_text)


@app.on_message(filters.command("getId") & filters.me)
async def f(_, mesage):
    await mesage.edit(mesage.chat.id)


@app.on_message(filters.command("sh") & filters.chat(CHANNEL_ID))
async def f(_, message):
    today = get_week_day()
    label = f"**Расписание {next_day[today]} ({get_next_day()})**\nC "

    if message.text == None:
        message_text = message.caption
    else:
        await message.delete()
        message_text = message.text

    if len(message_text) > 3:
        label += work_day_start_time[int(message_text[-2]) - 1] + " до " + work_day_finish_time[
            int(message_text[-1]) - 1]
    else:
        if today == 3:
            label += work_day_start_time[1] + " до "
        else:
            label += work_day_start_time[0] + " до "
        if today == 2 or today == 3:
            label += work_day_finish_time[7]
        else:
            label += work_day_finish_time[6]

    if message.text == None:
        await message.edit(label)
    else:
        await app.send_photo(CHANNEL_ID, "pensive_cat.jpg", label)


@app.on_message(filters.command("rasp") & filters.chat(CHANNEL_ID))
async def f(_, message):
    date = get_next_day()
    today = get_week_day()
    req = requests.get("https://diary130.ru/api/schedule", params={"class": "10Д", "date": date}).json()
    msg = f"**Расписание {next_day[today]} ({date})**\n"
    if req["ok"]:
        for i in req["schedule"]:
            msg += "   ".join(i) + "\n"
    else:
        msg = req["error"]
    await message.edit(msg)


@app.on_message(filters.command("dz") & filters.chat(CHANNEL_ID))
async def f(_, message):
    await message.delete()
    args = message.text.split()
    args = args[1:]
    today = get_week_day()
    subjects = await input_handle(subjects_for_day[today], args)

    pattern = f"**Домашние задания ({datetime.date.today()})**"
    for i in subjects:
        if i in full_subjects_names:
            pattern += "\n\n**" + full_subjects_names[i] + "**\n."
        else:
            await send_error_message("Предмета " + i + " не существует")
    await app.send_message(CHANNEL_ID, pattern)


def get_week_day():
    today = datetime.date.weekday(datetime.datetime.today())
    if today > 4:
        today = 4
    return today


def get_next_day():
    today = datetime.date.weekday(datetime.datetime.today())
    if today == 4 or today == 5 or today == 6:
        day = 7 - today
    else:
        day = 1
    return str(datetime.datetime.now() + datetime.timedelta(days=day)).split()[0]


async def send_error_message(text):
    mesage = await app.send_message(CHANNEL_ID, text)
    sleep(3)
    await mesage.delete()


async def input_handle(subjects, args):
    handle_subjects = subjects.copy()
    for i in args:
        if i[0] == "-":
            if i[1:] in subjects:
                handle_subjects.remove(i[1:])
            else:
                await send_error_message("Предмета " + i[1:] + " нет")
        elif i not in handle_subjects:
            handle_subjects.append(i)
        else:
            await send_error_message("Предмет " + i + " и так есть в этот день")
    return handle_subjects


app.run()
