from pyrogram import Client, filters
import logging
from time import sleep
from configparser import ConfigParser
import calendar
import datetime


english_Tahmina = "анг1"
english_Julia = "анг2"
history = "ист"
russian = "рус"
physics = "физ"
geometry = "геом"
literature = "лит"
algebra = "алг"
geography = "геог"
biology = "био"
chemistry = "хим"
social_study = "общ"
informatics = "инф"
russian_OGE = "огэ"
mrgz = "мргз"
next_day = ["на вторник", "на среду", "на четверг", "на пятницу", "на понедельник", "на понедельник", "на понедельник"]
work_day_start_time = ["8:00", "8:50", "9:50", "10:50", "11:50"]
work_day_finish_time = ["8:40", "9:30", "10:30", "11:30", "12:30", "13:20", "14:10", "15:10"]

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
                    while msg.text[i] != '\n' and i < len(msg.text)-1:  # передвижение курсора до конца задания
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


@app.on_message(filters.command("sh"))
def f(_, message):
    today = get_week_day()
    label = "**Домашние занания " + next_day[today] + "**\nC "

    if len(message.caption) > 3:
        label += work_day_start_time[int(message.caption[-2]) - 1] + " до " + work_day_finish_time[int(message.caption[-1]) - 1]
    else:
        label += work_day_start_time[0] + " до "
        if today == 2:
            label += work_day_finish_time[5]
        else:
            label += work_day_finish_time[6]
    message.edit(label)



@app.on_message(filters.command("dz"))
def f(_, message):
    args = message.text.split()
    args = args[1:]
    message.edit(generate_pattern(get_week_day(), args))


def get_week_day():
    y, m, d = map(int, str(datetime.date.today()).split("-"))
    return calendar.weekday(y, m, d)


def generate_pattern(week_day, args):
    if week_day == 0:
        subjects = [english_Tahmina, english_Julia, history, russian, physics, geometry, literature]
    elif week_day == 1:
        subjects = [geometry, geography, biology, algebra, physics]
    elif week_day == 2:
        subjects = [chemistry, literature, geometry, geography, english_Tahmina, english_Julia, social_study, russian]
    elif week_day == 3:
        subjects = [algebra, chemistry]
    else:
        subjects = [mrgz, biology, english_Tahmina, english_Julia, physics, literature, history]

    for i in args:
        if i[0] == "-":
            subjects.remove(i[1:])
        else:
            subjects.append(i)

    pattern = "**Домашние задания**\n\n"
    for i in subjects:
        pattern += "**"
        if i == english_Tahmina:
            pattern += "Английский язык (группа Тахмины)"
        elif i == english_Julia:
            pattern += "Английский язык (группа Юлии)"
        elif i == history:
            pattern += "История"
        elif i == russian:
            pattern += "Русский язык"
        elif i == physics:
            pattern += "Физика"
        elif i == geometry:
            pattern += "Геометрия"
        elif i == literature:
            pattern += "Литература"
        elif i == algebra:
            pattern += "Алгебра"
        elif i == geography:
            pattern += "География"
        elif i == biology:
            pattern += "Биология"
        elif i == chemistry:
            pattern += "Химия"
        elif i == social_study:
            pattern += "Обществознание"
        elif i == informatics:
            pattern += "Информатика (группа Льва)"
        elif i == russian_OGE:
            pattern += "Русский язык подготовка к ОГЭ"
        elif i == mrgz:
            pattern += "Методология решения геометрических задач"
        pattern += "**\n.\n\n"
    return pattern


app.run()

