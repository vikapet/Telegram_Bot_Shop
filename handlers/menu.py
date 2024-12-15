from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import InputMediaPhoto
from aiogram import types

from database.requests import (
    orm_add_to_cart,
    orm_delete_from_cart,
    orm_get_banner,
    orm_get_categories,
    orm_get_products,
    orm_get_product,
    orm_get_user_carts,
    orm_reduce_product_in_cart,
    orm_add_user,
)
from handlers.keyboards import get_user_catalog_btns, get_products_btns, get_user_cart, MenuCallBack
from paginator.pag import Paginator
from handlers.admin import format_price


def multiplication(quantity, price):
    """Функция для умножения цены товара на его количество.

    Args:
        quantity (int): Количество товара.
        price (float): Цена товара.

    Returns:
        float: Возвращает результат умножения.

    Raises:
        TypeError: Если количество - не целое число.
        ValueError: Если количество или цена отрицательные.

    Examples:
        >>> quantity = 2
        >>> price = 1000.00
        >>> multiplication(quantity, price)
        2000.00

    """
    if not isinstance(quantity, int):
        raise TypeError("Quantity must be an integer")
    if price < 0 and quantity < 0:
        raise ValueError("Both price and quantity cannot be negative")
    if price < 0:
        raise ValueError("Price cannot be negative")
    if quantity < 0:
        raise ValueError("Quantity cannot be negative")
    return quantity * price


async def get_menu_content(
    session: AsyncSession,
    level: int,
    menu_name: str,
    category: int | None = None,
    page: int | None = None,
):
    """Получает содержимое меню в зависимости от уровня навигации и других параметров.

    Args:
        session (AsyncSession): Асинхронная сессия для работы с базой данных.
        level (int): Уровень меню (0 - каталог, 1 - товары).
        menu_name (str): Имя меню.
        category (Optional[int]): Идентификатор категории продуктов.
        page (Optional[int]): Номер страницы для пагинации.

    Returns:
        Tuple: (media, reply_markup) - Содержимое меню (медиа и клавиатура).

    """
    if level == 0:
        return await catalog(session, level, menu_name)
    elif level == 1:
        return await products(session, level, category, page)


def pages(paginator: Paginator):
    """Создает кнопки пагинации на основе состояния пагинатора.

    Эта функция создает и возвращает словарь с кнопками пагинации, которые позволяют пользователю
    переходить к предыдущей или следующей странице в зависимости от состояния пагинатора.

    Args:
        paginator (Paginator): Объект пагинатора, который содержит информацию о текущей странице.

    Returns:
        dict: Словарь с кнопками пагинации. Ключи — текст кнопок, значения — действия ('previous' или 'next').

    """
    btns = dict()
    if paginator.has_previous():
        btns["◀ Пред."] = "previous"

    if paginator.has_next():
        btns["След. ▶"] = "next"

    return btns


async def catalog(session, level, menu_name):
    """Получает содержимое для отображения каталога, включая баннер, описание и кнопки для категорий.

    Эта функция извлекает баннер для заданного меню, а также список категорий товаров из базы данных.
    Возвращает медиа-объект для баннера и клавиатуру с кнопками для категорий.

    Args:
        session (AsyncSession): Асинхронная сессия для работы с базой данных.
        level (int): Уровень текущего меню.
        menu_name (str): Название страницы, для которой нужно получить баннер.

    Returns:
        tuple: Кортеж из двух элементов:
            - `InputMediaPhoto`: Объект для отображения баннера с изображением и описанием.
            - `InlineKeyboardMarkup`: Inline клавиатура с кнопками для категорий товаров.

    """
    banner = await orm_get_banner(session, menu_name)
    image = InputMediaPhoto(media=banner.image, caption=banner.description)

    categories = await orm_get_categories(session)
    kbds = get_user_catalog_btns(level=level, categories=categories)

    return image, kbds


async def products(session, level, category, page):
    """Получает информацию о продукте в заданной категории и странице.

     Эта функция извлекает список продуктов для заданной категории, использует пагинацию для
     отображения текущего продукта и создает клавиатуру с кнопками для перехода между страницами.

     Args:
         session (AsyncSession): Асинхронная сессия для работы с базой данных.
         level (int): Уровень текущего меню, используемый для настройки кнопок.
         category (int): Идентификатор категории продуктов.
         page (int): Номер текущей страницы продуктов.

     Returns:
         tuple: Кортеж из двух элементов:
             - `InputMediaPhoto`: Объект для отображения информации о продукте, включая изображение и описание.
             - `InlineKeyboardMarkup`: Клавиатура с кнопками для пагинации и добавления товара в корзину.

    """
    items = await orm_get_products(session, category_id=category)

    paginator = Paginator(items, page=page)
    product = paginator.get_item()

    image = InputMediaPhoto(
        media=product.image,
        caption=(
            f"{product.name}\n{product.description}\n"
            f"В наличии: {product.quantity} шт\n"
            f"Стоимость: {format_price(float(product.price))}\n"
            f"Товар {paginator.page} из {paginator.pages}"
        ))

    pagination_btns = pages(paginator)

    kbds = get_products_btns(
        level=level,
        category=category,
        page=page,
        pagination_btns=pagination_btns,
        product_id=product.id,
    )

    return image, kbds


async def add_to_cart(callback: types.CallbackQuery, callback_data: MenuCallBack, session: AsyncSession):
    """Добавляет товар в корзину для пользователя, если товар в наличии.

      Эта функция добавляет информацию о пользователе в базу данных, если его еще не существует,
      добавляет выбранный товар в корзину пользователя, отправляет ответ пользователю,
      сообщая, был ли товар успешно добавлен в корзину или товар закончился.

      Args:
          callback (types.CallbackQuery): Объект callback-запроса от пользователя,
              который содержит информацию о запросе.
          callback_data (MenuCallBack): Данные callback, включая идентификатор продукта.
          session (AsyncSession): Асинхронная сессия для работы с базой данных.

      Returns:
          None: Функция ничего не возвращает.

      """
    user = callback.from_user
    await orm_add_user(session, user_id=user.id, first_name=user.first_name, last_name=user.last_name)
    cart = await orm_add_to_cart(session, user_id=user.id, product_id=callback_data.product_id)

    if cart:
        await callback.answer("Товар добавлен в корзину.")
    else:
        await callback.answer("Товар закончился.")


async def carts(
        session: AsyncSession,
        user_id: int,
        menu_name: str | None = None,
        page: int = 1,
        product_id: int | None = None,
):
    """Обрабатывает действия пользователя с корзиной и возвращает обновленный контент корзины.

    Функция выполняет операции с корзиной пользователя, включая:
    - Увеличение количества товара (increment).
    - Уменьшение количества товара (decrement).
    - Удаление товара (delete).
    - Отображение корзины с учетом действий.

    Args:
        session (AsyncSession): Асинхронная сессия для работы с базой данных.
        menu_name (str): Действие, которое нужно выполнить ('increment', 'decrement', 'delete').
        page (int): Номер текущей страницы в корзине.
        user_id (int): Идентификатор пользователя.
        product_id (int | None): Идентификатор товара для действия.

    Returns:
        tuple[InputMediaPhoto, InlineKeyboardMarkup]:
            - `InputMediaPhoto`: Обновленное изображение с описанием состояния корзины.
            - `InlineKeyboardMarkup`: Клавиатура с кнопками управления корзиной.

    """
    if menu_name == "increment":
        product = await orm_get_product(session, product_id)
        if product and product.quantity > 0:
            await orm_add_to_cart(session, user_id, product_id)
        else:
            return True, False
    elif menu_name == "delete":
        await orm_delete_from_cart(session, user_id, product_id)
        if page > 1:
            page -= 1
    elif menu_name == "decrement":
        is_cart = await orm_reduce_product_in_cart(session, user_id, product_id)
        if page > 1 and not is_cart:
            page -= 1

    baskets = await orm_get_user_carts(session, user_id)

    if not baskets:
        return False, False

    else:
        paginator = Paginator(baskets, page=page)
        cart = paginator.get_item()

        cart_price = format_price(float(multiplication(cart.quantity, cart.product.price)))
        total_price = format_price(float((sum(multiplication(cart.quantity, cart.product.price) for cart in baskets))))
        image = InputMediaPhoto(
            media=cart.product.image,
            caption=(
                f"{cart.product.name}\n"
                f" {format_price(float(cart.product.price))} руб x {cart.quantity} = {cart_price} руб\n"
                f"В наличии: {cart.product.quantity} шт\nТовар {paginator.page} из {paginator.pages} в корзине\n"
                f"Общая стоимость товаров в корзине: {total_price} руб"
            ))

        pagination_btns = pages(paginator)

        kbds = get_user_cart(
            page=page,
            pagination_btns=pagination_btns,
            product_id=cart.product_id,
        )

        return image, kbds
