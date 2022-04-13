# Телеграм-бот - менеджер канала с домашним заданием

## Установка и запуск
1. Перейти в директорию в которой будет установлен проект и запустить терминал в ней

2. Скачать проект
   ```
   git clone https://github.com/Olegonik/tg-homework-bot
   ```

3. Перейти в директорию проекта
   ```
   cd tg-homework-bot/
   ```

4. Создать и записать в файл .env
   ```
   CHANNEL_ID=<id канала в котором будет производиться поиск и вывод заданий>
   ```

5. Создать и записать в config.ini данные из [telegram api](https://my.telegram.org/apps)
   ```
   [pyrogram]
   api_hash=
   api_id=
   ```

7. Установить библиотеки из requirements.txt
   ```
   pip install -r requirements.txt
   ```

6. Запустить бота
   ```
   python main.py
   ```

---

## Команды:
- homework || hw - принимает список предметов через пробел. Если в названии содержится несколько слов, можно поставить "-" на место пробела, либо если одно из слов не встречается в других предметах указать только его, регистр не важен.    
	Пример:
	```
	/hw русский-язык математика ОбЩеСтВОзнание
    	```
