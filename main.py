from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from datetime import datetime
from user import User

import vk_api
import data
import random
import json
import questions


# Сериализация (вообще функция не нужна - записал чтобы запомнить метод)
def serialize_user(obj):
    return json.dumps(obj)


# Десериализация (аналогично сериализации)
def deserialize_user(json_file):
    return json.load(json_file)


def send_file():
    pass


def update_file():
    pass


def get_file():
    pass


# Создание клавиатуры
def create_keyboard(received):
    """return: соответствующая запросу клавиатура"""
    keyboard = VkKeyboard(one_time=True)

    if received == 'профиль':
        keyboard.add_button('Профиль',
                            color=VkKeyboardColor.PRIMARY)

    elif received in range(0, questions.questions_length):
        answers = get_answers(received)
        for answer in answers:
            keyboard.add_button(answer, color=VkKeyboardColor.PRIMARY)

    else:
        return keyboard.get_empty_keyboard()

    keyboard = keyboard.get_keyboard()
    return keyboard


# Отправка сообщения
def send_message(vk_session, id, message=None, attachment=None,
                 keyboard=None):
    """отправить сообщение"""
    vk_session.method('messages.send',
                      {'user_id': id, 'message': message,
                       'random_id': random.randint(-2147483648, +2147483648),
                       'attachment': attachment, 'keyboard': keyboard})


# Получить id пользователя в списке users по его vk_id
def get_user_id(user_id, users):
    """return id объекта в users, где users[id] == user_id,  иначе None"""
    id = 0
    for user in users:
        if user.id == user_id:
            return id
        id += 1
    return None


# Получение ответов на вопрос по его id
def get_answers(question_id):
    """return: кортеж ответов на вопрос с id == qustion_id"""
    return tuple(questions.questions[question_id][2:])


# Вычисление id вопроса, на который был получен ответ
def is_answer_to(mes):
    """return: id вопроса, если mes является ответом, иначе None"""
    count = 0
    for item in questions.questions:
        for answer in item[2:]:
            if mes == answer:
                return count
        count += 1
    return None


# Вычисление, является ли ответ верным
def answer_is_true(question_id, answer):
    """return: true, если answer - правильный ответ на вопрос с id ==
     question_id"""
    if questions.questions[question_id][questions.questions[
            question_id][1]] == answer:
        return True
    return False


# Вычисление id следующего вопроса
def next_question(user):
    """return: id следующего вопроса, если вопросы остались, иначе None"""
    if user.last_asked_q is not None and user.has_ended_test is False:
        return user.last_asked_q + 1
    elif user.has_ended_test is False:
        return 0
    return None


def main():
    # Загрузка данных
    users = list()

    # Авторизация
    vk_session = vk_api.VkApi(token=data.token)
    longpoll = VkLongPoll(vk_session)
    vk = vk_session.get_api()

    # Чат-бот
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and \
                event.from_user is True and event.from_me is False:

            # Отладочная информация
            print('Message received: ' + str(datetime.strftime(datetime.now(),
                                                               "%H:%M:%S")))
            print('Text: ' + str(event.text))
            print(event.user_id, end='\n\n')

            # Обработка пользователя и ответ
            uid = get_user_id(event.user_id, users)

            # Если сообщ. от старого пользователя, который не закончил тест
            if uid is not None and users[uid].has_ended_test is False:

                # Если сообщение - запрос вывести информацию о профиле
                if event.text.lower() == 'профиль':
                    send_message(vk_session, event.user_id,
                                 message=users[uid].__str__(),
                                 keyboard=create_keyboard(''))
                    send_message(vk_session, event.user_id,
                                 message=(questions.questions[users[
                                              uid].last_asked_q][0]),
                                 keyboard=create_keyboard(
                                     users[uid].last_asked_q))

                # Если сообщение - ответ на вопрос или спам
                else:

                    # id вопроса, если сообщение - ответ
                    qid = is_answer_to(event.text)

                    # Если сообщение - ответ
                    if qid is not None:
                        # Обрабатываем ответ
                        send_message(vk_session, event.user_id,
                                     message=answer_is_true(qid, event.text),
                                     keyboard=create_keyboard(''))
                        users[uid].answer(qid,
                                          answer_is_true(qid, event.text),
                                          event.text)

                        # Задаем следующий вопрос
                        next_qid = next_question(users[uid])
                        # Если вопросы остались
                        if next_qid is not None:
                            send_message(vk_session, event.user_id,
                                         message=questions.questions[
                                             next_qid][0],
                                         keyboard=create_keyboard(next_qid))
                            users[uid].last_asked_q = next_qid
                        # Если вопросов не осталось
                        else:
                            send_message(vk_session, event.user_id,
                                         message=questions.end,
                                         keyboard=create_keyboard('профиль'))

                    # Если сообщение - спам
                    elif users[uid].last_asked_q is not None:
                        send_message(vk_session, event.user_id,
                                     message=('Я не понял Вас, поэтому пов'
                                             'торяю вопрос: \n' +
                                              questions.questions[users[
                                                  uid].last_asked_q][0]),
                                     keyboard=create_keyboard(
                                         users[uid].last_asked_q))

            # Если сообщение от старого пользователя, который закончил тест
            elif uid is not None and users[uid].has_ended_test is True:
                if event.text.lower() == 'профиль':
                    send_message(vk_session, event.user_id,
                                 message=users[uid].__str__(),
                                 keyboard=create_keyboard('профиль'))
                else:
                    send_message(vk_session, event.user_id,
                                 message='вы уже завершили тест',
                                 keyboard=create_keyboard('профиль'))

            # Если сообщение от нового пользователя
            else:
                # Если сообщение - кодовая фраза
                if event.text.lower() == 'психология - это не наука!':
                    users.append(User(event.user_id))
                    send_message(vk_session, event.user_id,
                                 message=questions.start,
                                 keyboard=create_keyboard(''))
                    send_message(vk_session, event.user_id,
                                 message=questions.questions[0][0],
                                 keyboard=create_keyboard(0))
                    users[get_user_id(event.user_id, users)].last_asked_q = 0

                # Если сообщение - спам
                else:
                    send_message(vk_session, event.user_id,
                                 message='*молчание*',
                                 keyboard=create_keyboard(''))


main()