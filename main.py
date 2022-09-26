import telebot
import logging
import sqlite3
import game_bot
import time
import global_path
import requests
logging.basicConfig(level=logging.INFO, filename="loger.log", format='%(name)s:[%(levelname)s]:[%(asctime)s] - %(message)s')
headers = {
    "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
    "Accept":"*/*"
}
string_execute = "INSERT INTO users (id, name) VALUES "
token='5349405097:AAFy-CWrA76-h60JoT3ip0AYn4mglMZ8vTA'
try:
    bot = telebot.TeleBot(token)
    logging.info("Bot successfully start")
except Exception as e:
    logging.critical(f"Bot dont start {e}")



@bot.message_handler(commands=['start'])
def get_info_users(message):
    bot.send_message(message.chat.id, "Обработка...")
    id_sport = 0
    id_events = list()
    id_games = list()
    list_games = list()
    counter = 0  # Перменная для отслеживания первого запроса, после первого запроса она не нужна
    while True:
        # API для получения всех событий: version=0 либо опустить этот параметр
        url_list_all_info = "https://line02w.bk6bba-resources.com/events/list?lang=ru&scopeMarket=1600"
        # Посылаем запрос
        try:
            responce = requests.get(url=url_list_all_info, headers=headers)
            data = responce.json()
        except Exception as e:
            logging.critical(f"main::get_data() error get json from API: {e}")

        for sports in data['sports']:  # Цикл в котором получаем id спорта
            try:
                if sports['name'] == global_path.SPORT_NAME:
                    id_sport = sports['id']
            except Exception as e:
                logging.critical(f"main::get_data() error get id_sport {e}")

        for events in data['sports']:  # Получаем все события, связанные с нашим спортом
            try:
                if events['parentId'] == id_sport:
                    id_events.append(events['id'])
            except Exception as e:  # Если у события нет id, пропускаем т.к. никак отследить его не можем
                continue

        for _id in id_events:  # Среди всех событий выбираем игры, т.к. там попадются команды, спец. ставки и т.д.
            for games in data['events']:
                try:
                    if games['sportId'] == _id and games['level'] == 1:
                        id_games.append(games['id'])
                except Exception as e:  # Если у события не id, пропускаем
                    continue

        for i in id_games:  # Цикл по всем полученным id игр
            try:
                if len(list_games) > 0:  # Если список игр пустой, то создаем объект
                    for check_game in list_games:
                        try:
                            if i == check_game.return_id():  # Проверяем есть ли уже такая игра как объект
                                break  # Если есть, то пропускаем
                        except Exception as e:
                            logging.critical(f"main::get_data() error check id Game {e}")
                    else:  # Если нет такой игры, создаем объект класса Game
                        try:
                            _game = game_bot.GameBot(i, headers)
                            list_games.append(_game)
                        except Exception as e:
                            logging.critical(f"main::get_data() error create and insert Game in list {e}")
                else:
                    try:
                        _game = game_bot.GameBot(i, headers)
                        list_games.append(_game)
                    except Exception as e:
                        logging.critical(f"main::get_data()::else error create and insert Game in list {e}")
            except Exception as e:
                logging.critical(f"main::get_data() error create object Game {e}")
        logging.info(f"Range main list: {len(list_games)}")
        if counter > 0:
            for i in list_games:
                i.update_data()
        for i in list_games:
            if i.get_info() != -1:
                temp_dict = i.get_info()
                tmp_list = temp_dict.split(',')
                logging.info(f"Info for user: {tmp_list}, {temp_dict}, {i.get_favorit()}")
                bot.send_message(message.chat.id, f"В событии {tmp_list[0]}\nФаворит {i.get_favorit()}\nПобедил {tmp_list[1]}")
                list_games.remove(i)
                del i
        counter += 1
        time.sleep(60)


bot.polling(none_stop=True, interval=0)