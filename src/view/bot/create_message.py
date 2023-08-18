from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup


class MessageBot:
    @staticmethod
    def create_start_message(
        message_chat_id: int, markup: ReplyKeyboardMarkup, bot: TeleBot
    ) -> None:
        bot.send_message(
            chat_id=message_chat_id,
            text="Привет, дорогой друг! "
            "Я чат-бот, который расскажет тебе, какая погода за окном. "
            "Снизу ты видишь кнопки с городами, которые ты раньше добавлял. "
            "Выбери, какой для тебя на данный момент город актуален. "
            "Если ты первый раз, то нажимай на кнопку добавить город",
            reply_markup=markup,
        )

    @staticmethod
    def create_message_with_input_new_city(message_chat_id: int, bot: TeleBot) -> None:
        bot.send_message(chat_id=message_chat_id, text="Введите название города")

    @staticmethod
    def create_message_with_preferred_city(
        message_chat_id: int, city_name: str, markup: ReplyKeyboardMarkup, bot: TeleBot
    ) -> None:
        bot.send_message(
            chat_id=message_chat_id,
            text=(
                f"Вы выбрали город {city_name.title()}. "
                f"Выберите, за какое время хотите получить прогноз"
            ),
            reply_markup=markup,
        )

    @staticmethod
    def create_message_wrong_city(
        message_chat_id: int, markup: ReplyKeyboardMarkup, bot: TeleBot
    ) -> None:
        bot.send_message(
            chat_id=message_chat_id,
            text="Извините, такого города не существует. " "Проверьте, правильно ли вы написали.",
            reply_markup=markup,
        )

    @staticmethod
    def create_message_choose_another_city(
        message_chat_id: int, markup: ReplyKeyboardMarkup, bot: TeleBot
    ) -> None:
        bot.send_message(
            chat_id=message_chat_id,
            text="Выберите интересующий город или добавьте новый",
            reply_markup=markup,
        )

    @staticmethod
    def create_message_with_incomprehension(
        message_chat_id: int, markup: ReplyKeyboardMarkup, bot: TeleBot
    ) -> None:
        bot.send_message(
            chat_id=message_chat_id,
            text="Извините, я вас не поминаю. Пожалуйста, следуйте кнопкам на клавиатуре",
            reply_markup=markup,
        )
