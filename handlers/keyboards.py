from aiogram.types import KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData


class MenuCallBack(CallbackData, prefix="menu"):
    """Класс для создания структуры callback data для меню (фабрика колбэков).

    Attrs:
        level (int): Уровень меню.
        menu_name (str): Имя меню.
        category (Optional[int]): Категория меню. Может быть `None`.
        page (int): Номер страницы. Значение по умолчанию 1.
        product_id (Optional[int]): Идентификатор продукта. Может быть `None`.

    """
    level: int
    menu_name: str
    category: int | None = None
    page: int = 1
    product_id: int | None = None


class CartCallback(CallbackData, prefix="cart"):
    """Класс для создания структуры callback data для корзины (фабрика колбэков).

    Attrs:
        menu_name (str): Имя меню.
        page (int): Номер страницы. Значение по умолчанию 1.
        product_id (Optional[int]): Идентификатор продукта. Может быть `None`.

    """
    menu_name: str
    page: int = 1
    product_id: int | None = None


def get_keyboard(*btns, placeholder: str = None, sizes: tuple[int] = (2,)):
    """Создает клавиатуру.

    Функция создает пользовательскую клавиатуру с переменным количеством кнопок,
    текстом для поля ввода и регулируемым значением кнопок.

    Args:
        *btns (str): Изменяемое количество кнопок, добавляемых в клавиатуру.
        placeholder (str, optional): Текст для поля ввода. По умолчанию None
        sizes (tuple[int], optional): Кортеж, указывающий количество кнопок в строке.
            По умолчанию (2,) - две кнопки в первой строке

    Returns:
        ReplyKeyboardMarkup: Пользовательская клавиатура с кнопками.

    Raises:
        ValueError: Если кнопок нет.
        TypeError: Если кнопка - не строка.

    """

    if not btns:
        raise ValueError("Buttons must exist")
    for button in btns:
        if not isinstance(button, str):
            raise TypeError("Each button must be a string")

    keyboard = ReplyKeyboardBuilder()

    for text in btns:
        keyboard.add(KeyboardButton(text=text))

    return keyboard.adjust(*sizes).as_markup(resize_keyboard=True, input_field_placeholder=placeholder)


def get_callback_btns(*, btns: dict[str, str], sizes: tuple[int] = (2,)):
    """Создает inline-клавиатуру.

    Функция создает inline-клавиатуру с кнопками, каждая из которых будет иметь callback-данные.

    Args:
        btns (dict[str, str]): Словарь, где ключи - текст кнопок, а значения - callback_data.
        sizes (tuple[int], optional): Количество кнопок в каждой строке клавиатуры. По умолчанию - 2 в первой строке.

    Returns:
        InlineKeyboardMarkup: Inline клавиатура с кнопками.

    Raises:
        TypeError: Если принимамый аргумент - не словарь, если название кнопки и ее callback_data - не строчки.
        ValueError: Если принимаемый аргумент пустой.

    """
    if not isinstance(btns, dict):
        raise TypeError("Buttons must be a dictionary")
    if not btns:
        raise ValueError("Buttons dictionary cannot be empty")
    for button, call in btns.items():
        if not isinstance(button, str) and not isinstance(call, str):
            raise TypeError("Both button and callback data must be a string")
        if not isinstance(button, str):
            raise TypeError("Each button must be a string")
        if not isinstance(call, str):
            raise TypeError("Each callback data must be a string")

    keyboard = InlineKeyboardBuilder()

    for text, data in btns.items():
        keyboard.add(InlineKeyboardButton(text=text, callback_data=data))

    return keyboard.adjust(*sizes).as_markup()


def get_user_catalog_btns(*, level: int, categories: list, sizes: tuple[int] = (2,)):
    """Создает inline-клавиатуру.

     Создает inline-клавиатуру с кнопками для каталога товаров.

     Args:
         level (int): Уровень текущего меню. Используется для определения уровня в callback data.
         categories (list): Список объектов категорий товаров.
         sizes (tuple[int], optional): Количество кнопок в ряду. По умолчанию - 2 в первом ряду.

     Returns:
         InlineKeyboardMarkup: Inline клавиатура с кнопками.

     """
    keyboard = InlineKeyboardBuilder()

    for c in categories:
        keyboard.add(InlineKeyboardButton(text=c.name,
                                          callback_data=MenuCallBack(level=level+1, menu_name=c.name,
                                                                     category=c.id).pack()))

    return keyboard.adjust(*sizes).as_markup()


def get_products_btns(*, level: int, category: int, page: int, pagination_btns: dict, product_id: int):
    """Создает inline-клавиатуру.

    Создает inline-клавиатуру с кнопками для отображения продуктов, включая кнопки для покупки и пагинации товаров.

    Args:
        level (int): Уровень текущего меню..
        category (int): Идентификатор категории продуктов.
        page (int): Номер текущей страницы с продуктами.
        pagination_btns (dict): Словарь с кнопками пагинации, где ключи — это текст кнопки,
            а значения — действия пагинации (например, 'next' или 'previous').
        product_id (int): Идентификатор текущего продукта.

    Returns:
        InlineKeyboardMarkup: Inline клавиатура с кнопками.

    """
    keyboard = InlineKeyboardBuilder()
    
    keyboard.add(InlineKeyboardButton(text='Купить 💵',
                                      callback_data=MenuCallBack(level=level, menu_name='add_to_cart',
                                                                 product_id=product_id).pack()))

    row = []
    for text, menu_name in pagination_btns.items():
        if menu_name == "next":
            row.append(InlineKeyboardButton(text=text, callback_data=MenuCallBack(
                                                level=level,
                                                menu_name=menu_name,
                                                category=category,
                                                page=page+1).pack()))

        elif menu_name == "previous":
            row.append(InlineKeyboardButton(text=text, callback_data=MenuCallBack(
                                                level=level,
                                                menu_name=menu_name,
                                                category=category,
                                                page=page-1).pack()))

    return keyboard.row(*row).as_markup()


def get_user_cart(*, page: int | None, pagination_btns: dict | None, product_id: int | None, sizes: tuple[int] = (3,)):
    """Создает inline-клавиатуру.

    Создает inline-клавиатуру для корзины пользователя с кнопками управления товаром и пагинацией.

    Args:
        page (int | None): Номер текущей страницы в корзине.
        pagination_btns (dict | None): Словарь кнопок пагинации,
            где ключ — текст кнопки, значение — действие ('previous' или 'next').
        product_id (int | None): Идентификатор текущего товара для операций (удаление, изменение количества).
        sizes (tuple[int], optional): Количество кнопок в ряду. По умолчанию 3 в первом ряду.

    Returns:
        InlineKeyboardMarkup: Inline клавиатура с кнопками.

    """
    keyboard = InlineKeyboardBuilder()

    keyboard.add(InlineKeyboardButton(
        text='Удалить',
        callback_data=CartCallback(menu_name='delete', product_id=product_id, page=page).pack()))
    keyboard.add(InlineKeyboardButton(
        text='-1',
        callback_data=CartCallback(menu_name='decrement', product_id=product_id, page=page).pack()))
    keyboard.add(InlineKeyboardButton(
        text='+1',
        callback_data=CartCallback(menu_name='increment', product_id=product_id, page=page).pack()))
    keyboard.add(InlineKeyboardButton(
        text='Заказать',
        callback_data=CartCallback(menu_name='order').pack()))

    keyboard.adjust(*sizes)

    row = []
    for text, menu_name in pagination_btns.items():
        if menu_name == "next":
            row.append(InlineKeyboardButton(
                text=text,
                callback_data=CartCallback(menu_name=menu_name, page=page+1).pack()))
        elif menu_name == "previous":
            row.append(InlineKeyboardButton(
                text=text,
                callback_data=CartCallback(menu_name=menu_name, page=page-1).pack()))

    return keyboard.row(*row).as_markup()
