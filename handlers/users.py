from aiogram import F, types, Router
from aiogram.filters import CommandStart
from sqlalchemy.ext.asyncio import AsyncSession


from handlers.keyboards import MenuCallBack, get_keyboard, CartCallback
from handlers.menu import get_menu_content, carts, add_to_cart

router = Router()


@router.message(CommandStart())
async def start_cmd(message: types.Message):
    """Обработчик команды start.

    Этот обработчик вызывается, когда пользователь отправляет команду /start. Бот отвечает
    сообщением с клавиатурой.

    Args:
        message (types.Message): Сообщение, полученное от пользователя.

    Returns:
        None: Функция ничего не возвращает.

    """
    user_kb = get_keyboard(
        "Товары",
        "Корзина",
        "О магазине",
    )
    text = "Здравствуйте, добро пожаловать в магазин картин художницы Виктории Петровой"
    await message.answer(text=text, reply_markup=user_kb)


@router.message(F.text == "Товары")
async def items(message: types.Message, session: AsyncSession):
    """Обработчик сообщения "Товары".

    Этот обработчик вызывается, когда пользователь нажимает на кнопку "Товары". Бот отвечает
    изображением с inline-клавиатурой для выбора категории товаров.

    Args:
        message (types.Message): Сообщение, полученное от пользователя.
        session (AsyncSession): Асинхронная сессия для взаимодействия с базой данных.

    Returns:
        None: Функция ничего не возвращает.

    """
    media, kb = await get_menu_content(session, level=0, menu_name="catalog")
    await message.answer_photo(photo=media.media, caption=media.caption, reply_markup=kb)


@router.message(F.text == "Корзина")
async def cart(message: types.Message, session: AsyncSession):
    """Обработчик сообщения "Корзина".

    Этот обработчик вызывается, когда пользователь нажимает на кнопку "Корзина". Бот отвечает
    изображением товара с inline-клавиатурой с кнопками управления товаром и пагинацией, если товары есть в корзине.
    Если нет, выводит сообщение "В вашей корзине ничего нет".

    Args:
        message (types.Message): Сообщение, полученное от пользователя.
        session (AsyncSession): Асинхронная сессия для взаимодействия с базой данных.

    Returns:
        None: Функция ничего не возвращает.

    """
    user_id = message.from_user.id
    media, kb = await carts(session, user_id)

    if not media and not kb:
        await message.answer("В вашей корзине ничего нет")
        return

    await message.answer_photo(photo=media.media, caption=media.caption, reply_markup=kb)


@router.message(F.text == "О магазине")
async def about(message: types.Message):
    """Обработчик сообщения "O магазине".

    Этот обработчик вызывается, когда пользователь нажимает на кнопку "О магазине". Бот отвечает
    сообщением с информацией о магазине.

    Args:
        message (types.Message): Сообщение, полученное от пользователя.

    Returns:
        None: Функция ничего не возвращает.

    """
    text = "В этом онлайн-магазине я продаю свои картины 🎨\n "\
           "Варианты оплаты: 💸\n 1. Картой онлайн \n Варианты доставки: ✈️ \n 1. Почтой \n 2. Курьером"
    await message.answer(text=text)


@router.callback_query(MenuCallBack.filter())
async def user_menu(callback: types.CallbackQuery, callback_data: MenuCallBack, session: AsyncSession):
    """Обрабатывает callback-запросы для основного меню пользователя, выполняет соответствующие действия.

    В зависимости от значения `menu_name` в `callback_data`, функция либо добавляет товар в корзину,
    либо обновляет контент меню (медиа и кнопки) на основе уровня, категории, страницы.

    Args:
        callback (types.CallbackQuery): Объект callback-запроса, содержащий информацию о запросе.
        callback_data (MenuCallBack): Данные callback, содержащие информацию о текущем состоянии меню.
        session (AsyncSession): Асинхронная сессиия для взаимодействия с базой данных.

    Returns:
        None: Функция ничего не возвращает.

    """
    if callback_data.menu_name == "add_to_cart":
        await add_to_cart(callback, callback_data, session)
        return

    media, reply_markup = await get_menu_content(
        session,
        level=callback_data.level,
        menu_name=callback_data.menu_name,
        category=callback_data.category,
        page=callback_data.page,
    )

    await callback.message.edit_media(media=media, reply_markup=reply_markup)
    await callback.answer()


@router.callback_query(CartCallback.filter())
async def user_cart(callback: types.CallbackQuery, callback_data: CartCallback, session: AsyncSession):
    """Обрабатывает callback-запросы для корзины пользователя, выполняет соответствующие действия.

    В зависимости от значения `menu_name` в `callback_data` функция
    обновляет контент корзины(медиа и кнопки) на основе страницы, id пользователя и товара.

    Args:
        callback (types.CallbackQuery): Объект callback-запроса, содержащий информацию о запросе.
        callback_data (MenuCallBack): Данные callback, содержащие информацию о текущем состоянии корзины.
        session (AsyncSession): Асинхронная сессиия для взаимодействия с базой данных.

    Returns:
        None: Функция ничего не возвращает.

    """
    media, reply_markup = await carts(
        session,
        menu_name=callback_data.menu_name,
        page=callback_data.page,
        user_id=callback.from_user.id,
        product_id=callback_data.product_id,
    )
    if media and not reply_markup:
        await callback.answer("Товар закончился")
        return

    if not media and not reply_markup:
        await callback.message.delete()
        await callback.message.answer("В вашей корзине ничего нет!")
        return

    await callback.message.edit_media(media=media, reply_markup=reply_markup)
    await callback.answer()
