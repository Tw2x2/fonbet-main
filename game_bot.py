import requests
import global_path
import logging


class GameBot():
    _event_name = ""        #Имя события
    _data = ""              #json из api, в нем все события из fonbet
    _new_info = False       #Если первый сет завершился, то эта перменная будет true
    _id_game = 0            #ID самой игры
    _headers = dict()       #Для request запроса параметры
    _team1_name = ""        #Имя первой команды
    _team2_name = ""        #Имя второй команды
    _tracking = False       #Если есть фаворит, отслеживаем игру
    _coefficient_team_1 = 0 #Коэф на первую команду
    _coefficient_team_2 = 0 #Коэф на второую команду
    _winner = -1            #Победитель: если первая команда, то 0; если вторая, то 1
    _favorit = 0            #Кто фаворит
    _set_event_id = 0

    def __init__(self,id_game,headers):
        #Конструктор в котором перадается id игры и заголовки
        #После запускается функция в которой получаем json со всеми событиями на fonbet
        self._id_game = id_game
        self._headers = headers
        logging.basicConfig(level=logging.CRITICAL, filename="loger.log", format='%(name)s:[%(levelname)s]:[%(asctime)s] - %(message)s')
        logging.info(f"GameBot::__init__:{id_game} Create game object")
        self.get_data()

    def __del__(self):
        logging.info(f"GameBot::__del__:{self._id_game} delete game")

    def update_data(self):
        url_info_games = "https://line05w.bk6bba-resources.com/events/event?lang=ru&eventId=(1)&scopeMarket=1600&version=0"
        responce_game_info = requests.get(url=url_info_games.replace('(1)', str(self._id_game)), headers=self._headers)
        try:
            self._data = responce_game_info.json()
        except Exception as e:
            logging.critical("Error get json package from api!")
        temp_set = 0
        for event in self._data['events']:
            if len(event['name']) == 7 and self._tracking:
                # Проверяем сет
                _string = event['name']
                temp_info = _string.split()
                temp_set = int(temp_info[0].split('-')[0])
                logging.info(f"GameBot::update_data:{self._id_game} Set is {temp_set}")
                if temp_set > 1 and temp_set < 4 and self._tracking == True:
                    logging.info(
                        f"GameBot::update_data:{self._id_game} for event set is {temp_set}, event is tracking")
                    for score in self._data['eventMiscs']:
                        if score['id'] == self._id_game:
                            if (int(score['score1']) == 1  and int(score['score2']) == 0) or (int(score['score1']) == 0  and int(score['score2']) == 1):
                                logging.info(
                                    f"GameBot::update_data:{self._id_game} for event: check winner...")
                                self._winner = 0 if score['score1'] > score['score2'] else 1
                                self._new_info = True
                                logging.info(
                                    f"GameBot::update_data:{self._id_game} for event: wineer {self._winner + 1}, new info {self._new_info}")
                                break
                            elif int(score['score1']) != 0 or int(score['score2']) != 0:
                                logging.info(
                                    f"GameBot::update_data:{self._id_game} play one more set, delete event")
                                self.__del__()
                            logging.info(f"GameBot::update_data:{self._id_game}: {score['score1']}-{score['score2']}")
                elif temp_set == 1:
                    continue
            elif not self._tracking:
                logging.info(
                    f"GameBot::update_data:{self._id_game} delete event")
                self.__del__()

    def return_id(self):
        return self._id_game

    def get_info(self):
        if self._new_info:
            if self._favorit == 1 and self._winner == 1:
                st = f"{self._event_name},{self._team2_name}"
                return st
            elif self._favorit == 2 and self._winner == 0:
                st = f"{self._event_name},{self._team1_name}"
                return st
            else:
                logging.info(f"GameBot::get_info:{self._id_game} favorit is win: tracking {self._tracking}")
                return -1
        else:
            return -1

    def get_favorit(self):
        if self._favorit == 1:
            return self._team1_name
        else:
            return self._team2_name

    def get_data(self):
        logging.info(f"GameBot::get_data:{self._id_game} call")
        #Получаем все события
        url_info_games = "https://line05w.bk6bba-resources.com/events/event?lang=ru&eventId=(1)&scopeMarket=1600&version=0"
        responce_game_info = requests.get(url=url_info_games.replace('(1)', str(self._id_game)), headers=self._headers)
        #Если что-то не так, то в log надо будет смотреть
        try:
            self._data = responce_game_info.json()
            logging.info(f"GameBot::get_data:{self._id_game} successfully get data from API")
        except Exception as e:
            logging.critical("Error get json package from api!")
        #Если нет имен команд, скипаем
        if not self.check_events():
            return False
        #Вся инфа по событию
        self.get_info_event()

    def get_info_event(self):
        logging.info(f"GameBot::get_info_event:{self._id_game} call")
        #Временно сохраняем id спорта
        _temp_value_sport_id = 0
        #Ищем наше событие в списке (ищем игру среди говна ненужного)
        for event in self._data['events']:
            try:
                #Вытаскиваем всю нужную инфу
                if event['id'] == self._id_game and (not event['name']):
                    self._team1_name = event['team1']
                    self._team2_name = event['team2']
                    _temp_value_sport_id = event['sportId']
                    logging.info(f"GameBot::get_info_event:{self._id_game} Successfully get info: team1_name: {self._team1_name}, team2_name: {self._team2_name}")
                else:
                    if not event['name']:
                        continue
                    elif len(event['name']) == 7:
                        logging.info(f"GameBot::get_info_event:{self._id_game} Check set: param name in json {event['name']}")
                        #Проверяем сет
                        _string = event['name']
                        temp_info = _string.split()
                        temp_set = int(temp_info[0].split('-')[0])
                        logging.info(f"GameBot::get_info_event:{self._id_game} Set is {temp_set}")
                        if temp_set == 1:
                            self.is_nedeed_tracking()
                            if self._tracking:
                                self._set_event_id = event["id"]
                                logging.info(f"GameBot::get_info_event:{self._id_game} Set is {temp_set}, start tracking event")
                            else:
                                logging.info(f"GameBot::get_info_event:{self._id_game} game not tracking, delete game")
                                self.__del__()
                        elif temp_set > 1 and temp_set < 4 and self._tracking == True:
                            logging.info(
                                f"GameBot::get_info_event:{self._id_game} for event: set is {temp_set}, event is tracking")
                            for score in self._data['eventMiscs']:
                                if score['id'] == self._id_game:
                                    if (int(score['score1']) == 1  and int(score['score2']) == 0) or (int(score['score1']) == 0  and int(score['score2']) == 1):
                                        logging.info(
                                            f"GameBot::get_info_event:{self._id_game} for event: check winner...")
                                        self._winner = 0 if score['score1'] > score['score2'] else 1
                                        self._new_info = True
                                        logging.info(
                                            f"GameBot::get_info_event:{self._id_game} for event: wineer {self._winner+1}, new info {self._new_info}")
                                    elif int(score['score1']) != 0  or int(score['score2']) != 0:
                                        logging.info(
                                            f"GameBot::get_info_event:{self._id_game} play one more set, delete event")
                                        self.__del__()
                        else:
                            logging.info(f"GameBot::get_info_event:{self._id_game} the event is not suitable for tracking, delete event")
                            self.__del__()
            except Exception as e:
                continue
        for item in self._data['sports']:
            #Получаем имя события
            if item['id'] == _temp_value_sport_id:
                self._event_name = item['name']
                logging.info(f"GameBot::get_info_event:{self._id_game} event data received successfully: event:{self._event_name}, team_1:{self._team1_name}, team_2:{self._team2_name}")


    def is_nedeed_tracking(self):
        logging.info(f"GameBot::is_nedeed_tracking:{self._id_game} check")
        #Проверка на фаворита
        for info in self._data['customFactors']:
            #В json нужные коэфиценты находятся в словаре customFactors
            #В подславоре e под номерами 921 и 923, номера сохранены в файле global_path
            #Чтобы было проще поменять в случае чего
            if info['e'] == self._id_game:
                for coef in info['factors']:
                    try:
                        if coef['f'] == global_path.PARAM_FRST_TEAM:
                            self._coefficient_team_1 = coef['v']
                            logging.info(
                                f"GameBot::is_nedeed_tracking:{self._id_game} for event get coef for {self._team1_name} - {self._coefficient_team_1}")
                        elif coef['f'] == global_path.PARAM_SCND_TEAM:
                            self._coefficient_team_2 = coef['v']
                            logging.info(
                                f"GameBot::is_nedeed_tracking:{self._id_game} for event get coef for {self._team2_name} - {self._coefficient_team_2}")
                    except Exception as e:
                        continue
        if self._coefficient_team_1 != 0 or self._coefficient_team_2 != 0:
            self._tracking = (abs(self._coefficient_team_1 - self._coefficient_team_2)) > 0.49
            if self._coefficient_team_1 > self._coefficient_team_2:
                self._favorit = 2
                logging.info(
                    f"GameBot::is_nedeed_tracking:{self._id_game} for event favorit is {self._team2_name}")
            else:
                self._favorit = 1
                logging.info(
                    f"GameBot::is_nedeed_tracking:{self._id_game} for event favorit is {self._team1_name}")

    def check_events(self):
        logging.info(f"GameBot::check_event:{self._id_game} Check event")
        #Если в событии есть id команд, то в этом собитии лежат имена команд и id игры
        for event in self._data['events']:
            if event['team1Id'] == 0 or event['team2Id'] == 0:
                logging.info(f"GameBot::check_event:{self._id_game} Event not game")
                return False
            else:
                logging.info(f"GameBot::check_event:{self._id_game} Event is a game")
                return True
        return False

    def set_winner(self, temp_set_id):
        #Выясняем кто победил
        for eventMiscs in self._data['eventMiscs']:
            try:
                if self._set != 0:
                    if (eventMiscs['id'] == temp_set_id) and (eventMiscs['score1'] != 0 or eventMiscs['score2']):
                        self._winner = 0 if eventMiscs['score1'] > eventMiscs['score2'] else 1
                        self._new_info = True
                        logging.info(
                            f"GameBot::set_winner:{self._id_game} in event winner team_{self._winner+1}")
            except Exception as e:
                continue

