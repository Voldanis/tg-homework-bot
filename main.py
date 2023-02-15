from pyrogram import Client, filters
import logging
from time import sleep
from configparser import ConfigParser
import calendar
import datetime


english_Tahmina = "тахмины"
english_Julia = "юлии"
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
informatics = "информатика"
russian_OGE = "огэ"
mrgz = "методология"
subjects_for_day = [[english_Tahmina, english_Julia, history, russian, physics, geometry, literature],
                    [geometry, geography, biology, algebra, physics],
                    [chemistry, literature, geometry, geography, english_Tahmina, english_Julia, social_study, russian],
                    [algebra, chemistry],
                    [mrgz, biology, english_Tahmina, english_Julia, physics, literature, history]]
full_subjects_names = {english_Tahmina: "Английский язык (группа Тахмины)",
                       english_Julia: "Английский язык (группа Юлии)",
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
                       informatics: "Информатика (группа Льва)",
                       russian_OGE: "Русский язык подготовка к ОГЭ",
                       mrgz: "Методология решения геометрических задач"}
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
CHANNEL_ID = config.getint('bot', 'channel_id', fallback=0) # -1001633320063 -- тест_группа -1001632804461 -- дз_группа


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

        b = False
        for leftAdd in ["**", ""]:
            for rightAdd in ["**", ""]:
                findArg = leftAdd + arg + rightAdd
                last_arg = list(app.search_messages(CHANNEL_ID, findArg, limit=10))
                arg = arg.lower()
                if not last_arg:
                    continue
                for msg in last_arg:
                    if msg.text == None:
                        continue
                    i = 0
                    while msg.text[i:i+len(arg)].lower() != arg and i < len(msg.text):  # поиск предмета в сообщении
                        i += 1
                    if i == len(msg.text):
                        continue
                    while msg.text[i-1] != '\n' and i > 0:
                        i -= 1
                    start_name = i
                    while msg.text[i] != '\n' and i < len(msg.text):  # переход на следующую строку
                        i += 1
                    if i == len(msg.text):
                        continue
                    end_name = i
                    name = msg.text[start_name:end_name]
                    i += 1
                    start_pos = i
                    while i < len(msg.text)-1 and (msg.text[i] != '\n' or msg.text[i + 1] != '\n'):  # передвижение курсора до конца задания
                        i += 1
                    if msg.text[i] == '\n':
                        i -= 1
                    end_pos = i+1
                    hw = msg.text[start_pos:end_pos]
                    hw_for_tomorrow[name] = hw

                    b = True
                    break
                if b:
                    break
            if b:
                break
        if not b:
            send_error_message(f"Нет записей про {arg}")

    res_msg_text = "**Домашние занания " + next_day[today] + "**"
    for name, hw in hw_for_tomorrow.items():
        res_msg_text += f"\n\n**{name}**\n{hw}"
    app.send_message(message.chat.id, res_msg_text)


@app.on_message(filters.command("getId") & filters.me)
def f(_, mesage):
    mesage.edit(mesage.chat.id)


@app.on_message(filters.command("sh") & filters.chat(CHANNEL_ID))
def f(_, message):
    today = get_week_day()
    label = "**Домашние занания " + next_day[today] + "**\nC "

    if message.text == None:
        message_text = message.caption
    else:
        message.delete()
        message_text = message.text

    if len(message_text) > 3:
        label += work_day_start_time[int(message_text[-2]) - 1] + " до " + work_day_finish_time[int(message_text[-1]) - 1]
    else:
        label += work_day_start_time[0] + " до "
        if today == 2:
            label += work_day_finish_time[5]
        else:
            label += work_day_finish_time[6]

    if message.text == None:
        message.edit(label)
    else:
        app.send_photo(CHANNEL_ID, "pensive_cat.jpg", label)



@app.on_message(filters.command("dz") & filters.chat(CHANNEL_ID))
def f(_, message):
    message.delete()
    args = message.text.split()
    args = args[1:]
    today = get_week_day()
    subjects = input_handle(subjects_for_day[today], args)

    pattern = "**Домашние задания**"
    for i in subjects:
        if i in full_subjects_names:
            pattern += "\n\n**" + full_subjects_names[i] + "**\n."
        else:
            send_error_message("Предмета " + i + " не существует")
    app.send_message(CHANNEL_ID, pattern)


def get_week_day():
    y, m, d = map(int, str(datetime.date.today()).split("-"))
    today = calendar.weekday(y, m, d)
    if today > 4:
        today = 4
    return today


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
                send_error_message("Предмета " + i[1:] + " сегодня нет")
        elif i not in handle_subjects:
            handle_subjects.append(i)
        else:
            send_error_message("Предмет " + i + " и так есть в этот день")
    return handle_subjects


app.run()

