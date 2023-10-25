import enum


class Command(enum.StrEnum):
    start = "start"


class Text:
    add_city = "Добавить новый город"
    choose_city = "Выбрать другой город"
    now = "Сейчас"
    one_day = "На 1 день"
    three_days = "На 3 дня"
    seven_days = "На 7 дней"
    fourteen_days = "На 14 дней"
    delete = "Очистить историю поиска🗑 \n(оставлю 4 последних города)"
    next = "Далее"


class MessageType(enum.StrEnum):
    text = "text"
    any = "any"
