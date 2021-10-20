from questions import questions_length, main_questions


class User:

    def __init__(self, id):
        self.__id = id
        self.__penalty_points = 0
        self.__has_ended_test = False
        self.__answered_questions = dict()
        self.last_asked_q = None

    def __str__(self):
        return "Пользователь с id: {}, \n Ответил на {} вопросов, \n" \
               "имеет {} штрафных баллов, \n закончил тест: {}".format(
                self.__id,
                len(self.__answered_questions),
                self.__penalty_points,
                self.__has_ended_test)

    @property
    def id(self):
        return self.__id

    @property
    def has_ended_test(self):
        return self.__has_ended_test

    @property
    def penalty_points(self):
        return self.__penalty_points

    @property
    def answered_questions(self):
        return self.__answered_questions

    def end_of_test(self):
        if (len(self.__answered_questions) == questions_length
                or (self.__penalty_points == 0
                    and len(self.__answered_questions) > main_questions)):
            self.__has_ended_test = True

    def answer(self, question_id, answer_is_true, answer):
        if (question_id not in self.__answered_questions and
                self.__has_ended_test is False and
                question_id == self.last_asked_q):
            self.__answered_questions[question_id] = answer
            if answer_is_true is False:
                self.__penalty_points += 1
            else:
                if question_id >= main_questions:
                    self.__penalty_points -= 1
        self.end_of_test()