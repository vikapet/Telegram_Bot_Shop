import pytest
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup

from paginator.pag import Paginator
from handlers.admin import format_price
from handlers.keyboards import get_callback_btns, get_keyboard
from handlers.menu import multiplication


def test_paginator_positive():
    """Позитивные тесты пагинатора"""
    items = [1, 2, 3, 4, 5, 6]
    item = [1]

    paginator = Paginator(items, page=1)
    assert paginator.pages == 6
    assert paginator.get_item() == 1
    assert paginator.has_next() == 2
    assert paginator.has_previous() is False

    paginator = Paginator(items, page=6)
    assert paginator.get_item() == 6
    assert paginator.has_next() is False
    assert paginator.has_previous() == 5

    paginator = Paginator(item, page=1)
    assert paginator.pages == 1
    assert paginator.get_item() == 1
    assert paginator.has_next() is False
    assert paginator.has_previous() is False


def test_paginator_negative():
    """Негативные тесты пагинатора"""
    items = [1, 2, 3]

    with pytest.raises(ValueError, match="Array cannot be empty"):
        Paginator([], page=1)

    with pytest.raises(ValueError, match="Page must be greater than 0"):
        Paginator(items, page=-1)

    with pytest.raises(IndexError, match="This page doesn't exist"):
        Paginator(items, page=5)


def test_price_formatting_positive():
    """Позитивные тесты форматирования цены"""

    assert format_price(1000) == " 1 000.00 ₽"

    assert format_price(1234.56) == " 1 234.56 ₽"

    assert format_price(0) == " 0.00 ₽"

    assert format_price(1000000) == " 1 000 000.00 ₽"


def test_price_formatting_negative():
    """Негативные тесты форматирования цены"""

    with pytest.raises(ValueError, match="Price cannot be negative"):
        format_price(-100)

    with pytest.raises(TypeError, match="Price must be a number"):
        format_price("100")

    with pytest.raises(TypeError, match="Price must be a number"):
        format_price(None)


def test_reply_keyboard_markup_positive():
    """Позитивные тесты создания обычной клавиатуры"""

    keyboard = get_keyboard("Кнопка 1", "Кнопка 2", "Кнопка 3", "Кнопка 4", sizes=(2, 1, 1))

    assert isinstance(keyboard, ReplyKeyboardMarkup)

    assert len(keyboard.keyboard) == 3

    assert keyboard.keyboard[0][0].text == "Кнопка 1"

    assert keyboard.keyboard[1][0].text == "Кнопка 3"

    assert keyboard.keyboard[2][0].text == "Кнопка 4"


def test_reply_keyboard_markup_negative():
    """Негативные тесты создания обычной клавиатуры"""

    with pytest.raises(ValueError, match="Buttons must exist"):
        get_keyboard()

    with pytest.raises(TypeError, match="Each button must be a string"):
        get_keyboard("Кнопка 1", 2)

    with pytest.raises(TypeError, match="Each button must be a string"):
        get_keyboard(None)


def test_inline_keyboard_markup_positive():
    """Позитивные тесты создания инлайн клавиатуры"""

    buttons = {"Кнопка 1": "Колбэк 1", "Кнопка 2": "Колбэк 2", "Кнопка 3": "Колбэк 3", "Кнопка 4": "Колбэк 4"}

    inline_keyboard = get_callback_btns(btns=buttons, sizes=(2, 1, 1))

    assert isinstance(inline_keyboard, InlineKeyboardMarkup)

    assert len(inline_keyboard.inline_keyboard) == 3

    assert inline_keyboard.inline_keyboard[0][0].text == "Кнопка 1"

    assert inline_keyboard.inline_keyboard[0][0].callback_data == "Колбэк 1"

    assert inline_keyboard.inline_keyboard[0][1].text == "Кнопка 2"

    assert inline_keyboard.inline_keyboard[2][0].callback_data == "Колбэк 4"


def test_inline_keyboard_markup_negative():
    """Негативные тесты создания инлайн клавиатуры"""

    with pytest.raises(TypeError, match="Buttons must be a dictionary"):
        get_callback_btns(btns=["Кнопка 1"])

    with pytest.raises(TypeError, match="Buttons must be a dictionary"):
        get_callback_btns(btns="Строка")

    with pytest.raises(ValueError, match="Buttons dictionary cannot be empty"):
        get_callback_btns(btns={})

    with pytest.raises(TypeError, match="Both button and callback data must be a string"):
        get_callback_btns(btns={"Кнопка 1": "Колбэк 1", 2: 2})

    with pytest.raises(TypeError, match="Each button must be a string"):
        get_callback_btns(btns={"Кнопка 1": "Колбэк 1", 2: "Колбэк 2"})

    with pytest.raises(TypeError, match="Each callback data must be a string"):
        get_callback_btns(btns={"Кнопка 1": "Колбэк 1", "Кнопка 1": None})

    with pytest.raises(TypeError, match="Both button and callback data must be a string"):
        get_callback_btns(btns={"Кнопка 1": "Колбэк 1", 2: 2})

    with pytest.raises(TypeError, match="Buttons must be a dictionary"):
        get_callback_btns(btns=None)


def test_multiplication_positive():
    """Позитивные тесты умножения"""

    assert multiplication(2, 1000.00) == 2000.00

    assert multiplication(3, 1234.56) == 3703.68

    assert multiplication(0, 10000) == 0

    assert multiplication(200, 1000000) == 200000000

    assert multiplication(5, 3333.4567) == 16667.2835


def test_multiplication_negative():
    """Негативные тесты умножения"""

    with pytest.raises(ValueError, match="Price cannot be negative"):
        multiplication(100, -1)

    with pytest.raises(ValueError, match="Quantity cannot be negative"):
        multiplication(-2, 10000)

    with pytest.raises(ValueError, match="Both price and quantity cannot be negative"):
        multiplication(-100, -1)

    with pytest.raises(TypeError, match="Quantity must be an integer"):
        multiplication("100", 100)

    with pytest.raises(TypeError, match="Quantity must be an integer"):
        multiplication(None, 2000)
