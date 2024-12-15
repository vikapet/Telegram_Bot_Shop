from aiogram import F, Router, types
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from filters.admin_fil import IsAdmin
from handlers.keyboards import get_keyboard, get_callback_btns
from database.requests import (
    orm_change_banner_image,
    orm_get_categories,
    orm_add_product,
    orm_delete_product,
    orm_get_info_pages,
    orm_get_product,
    orm_get_products,
    orm_update_product,
)

from sqlalchemy.ext.asyncio import AsyncSession

admin = Router()

admins = [1188100227]
admin.message.filter(IsAdmin(admins))

admin_kb = get_keyboard(
        "Добавить товар",
        "Ассортимент",
        "Добавить/изменить баннер",
        placeholder="Выберите действие",
    )


class Banner(StatesGroup):
    """Класс состояний для добавления баннера.

    Этот класс используется для управления состояниями во время процесса добавления баннера.
    Содержит только одно состояние `image`, которое представляет этап загрузки изображения.

    Attrs:
        image (State): Состояние для загрузки изображения баннера.

    """
    image = State()


class AddProduct(StatesGroup):
    """Класс состояний для добавления товаров

    Этот класс описывает состояния, через которые проходит процесс добавления нового товара.
    Каждое состояние соответствует шагу, который необходимо пройти пользователю для ввода информации
    о продукте (название, описание, цена и т. д.).

    Attrs:
        name (State): Состояние для ввода названия товара.
        description (State): Состояние для ввода описания товара.
        category (State): Состояние для выбора категории товара.
        price (State): Состояние для ввода цены товара.
        quantity (State): Состояние для ввода количества товара.
        image (State): Состояние для загрузки изображения товара.

        product_for_change (Optional[Product]): Переменная для хранения объекта продукта, который изменяется.
        texts (dict): Словарь, содержащий тексты подсказок для каждого состояния,
            которые будут отправляться пользователю.

    """
    name = State()
    description = State()
    category = State()
    price = State()
    quantity = State()
    image = State()

    product_for_change = None

    texts = {
        'AddProduct:name': 'Введите название заново:',
        'AddProduct:description': 'Введите описание заново:',
        'AddProduct:category': 'Выберите категорию заново',
        'AddProduct:price': 'Введите стоимость заново:',
        'AddProduct:quantity': 'Введите количество заново',
        'AddProduct:image': 'Этот шаг последний',
    }


def format_price(price: float):
    """Функция для форматирования цены.

    Эта функция принимает число, форматирует его и возращает строку.

    Args:
        price (float): Цена товара.

    Returns:
        str: Возвращает строку из отформатированной цены.

    Raises:
        TypeError: Если цена - не число.
        ValueError: Если цена имеет отрицательное значение.

    Examples:
        >>> price = 1234567.89
        >>> format_price(price)
        " 1 234 567.89 ₽"

    """
    if not isinstance(price, (int, float)):
        raise TypeError("Price must be a number")
    if price < 0:
        raise ValueError("Price cannot be negative")
    return f"{price: _.2f} ₽".replace('_', ' ')


@admin.message(Command("admin"))
async def admin_command(message: types.Message):
    """Обработчик команды admin.

    Этот обработчик вызывается, когда администратор отправляет команду /admin. Бот отвечает
    сообщением с клавиатурой, на которой представлены различные административные функции.

    Args:
        message (types.Message): Сообщение, полученное от пользователя.

    Returns:
        None: Функция ничего не возвращает.

    """
    await message.answer("Что хотите сделать?", reply_markup=admin_kb)


@admin.message(F.text == 'Ассортимент')
async def admin_assortiment(message: types.Message, session: AsyncSession):
    """Обрабатывает команду 'Ассортимент' и отправляет пользователю клавиатуру с категориями товаров.

    Эта функция извлекает список категорий товаров из базы данных и формирует клавиатуру с кнопками,
    каждая из которых соответствует категории.

    Args:
        message (types.Message): Сообщение, отправленное пользователем.
        session (AsyncSession): Асинхронная сессия для работы с базой данных.

    Returns:
        None: Функция ничего не возвращает.

    """
    categories = await orm_get_categories(session)
    await message.answer("Выберите категорию", reply_markup=get_callback_btns(
        btns={category.name: f'category_{category.id}' for category in categories}))


@admin.callback_query(F.data.startswith('category_'))
async def look_at_product(callback: types.CallbackQuery, session: AsyncSession):
    """Обработчик callback-запроса, начинающегося с 'category_'

    Функция отвечает на callback-запрос, вызываемый, когда администратор выбирает категорию на Inline-клавиатуре.
    Она извлекает все продукты соответствующей категории из базы данных и
    отправляет подробную информацию о каждом продукте:
    название, описание, -  а также опции "Удалить", "Изменить".

    Args:
        callback (types.CallbackQuery): Объект, содержащий информацию об Inline-кнопке.
        session (AsyncSession): Асинхронная сессия для взаимодействия с базой данных.

    Returns:
        None: Функция ничего не возвращает.

     """
    category_id = callback.data.split('_')[-1]
    for product in await orm_get_products(session, int(category_id)):
        await callback.message.answer_photo(
            product.image,
            caption=(
                f"{product.name}\n"
                f"{product.description}\n"
                f"Стоимость: {format_price(float(product.price))}\n"
                f"Количество товаров: {product.quantity}"
            ),
            reply_markup=get_callback_btns(btns={"Удалить": f"delete_{product.id}", "Изменить": f"change_{product.id}"},
                                           sizes=(2,)))
    await callback.answer()
    await callback.message.answer("Вот список товаров")


@admin.callback_query(F.data.startswith("delete_"))
async def delete_product_callback(callback: types.CallbackQuery, session: AsyncSession):
    """Обработчик callback-запроса, начинающегося с "delete_"

    Эта функция вызывается при нажатии кнопки "Удалить", находящейся под изображением товара.
    Она удаляет товар из базы данных по id, переданном в callback-запросе.

    Args:
        callback (types.CallbackQuery): Объект, содержащий информацию об Inline-кнопке.
        session (AsyncSession): Асинхронная сессия для взаимодействия с базой данных.

    Returns:
        None: Функция ничего не возвращает.

    """
    await orm_delete_product(session, int(callback.data.split("_")[-1]))
    await callback.answer("Товар удален")
    await callback.message.answer("Товар удален!")


@admin.message(StateFilter(None), F.text == 'Добавить/изменить баннер')
async def add_content_for_banner(message: types.Message, state: FSMContext, session: AsyncSession):
    """Обработчик команды "Добавить/изменить баннер".

     Отправляет пользователю инструкцию для загрузки фото баннера с описанием страницы,
     для которой баннер предназначен. Переходит в состояние `AddBanner.image`.

     Args:
         message (types.Message): Сообщение от пользователя.
         state (FSMContext): Контекст текущего состояния пользователя.
         session (AsyncSession): Асинхронная сессия для взаимодействия с базой данных.

     Returns:
         None: Функция ничего не возвращает.

    """
    await message.answer(f"Отправьте фото баннера.\nВ описании укажите для какой страницы:\
                         \n{', '.join([page.name for page in await orm_get_info_pages(session)])}",
                         reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(Banner.image)


@admin.message(Banner.image, F.photo)
async def add_banner(message: types.Message, state: FSMContext, session: AsyncSession):
    """Обработчик для добавления/изменения фото баннера.

    Обрабатывает фото, отправленное пользователем, и добавляет его как баннер для указанной страницы.
    Проверяет корректность названия страницы, указанного в описании к изображению.

    Args:
        message (types.Message): Сообщение от пользователя с изображением.
        state (FSMContext): Контекст текущего состояния пользователя.
        session (AsyncSession): Асинхронная сессия для взаимодействия с базой данных.

    Returns:
        None: Функция ничего не возвращает.

    """
    image_id = message.photo[-1].file_id
    page_disc = message.caption.strip()
    pages_names = [page.name for page in await orm_get_info_pages(session)]
    if page_disc not in pages_names:
        await message.answer(f"Введите правильное название страницы, например:\
                         \n{', '.join(pages_names)}")
        return
    await orm_change_banner_image(session, page_disc, image_id,)
    await message.answer("Баннер добавлен/изменен.", reply_markup=admin_kb)
    await state.clear()


@admin.callback_query(StateFilter(None), F.data.startswith("change_"))
async def change_product_callback(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    """Обрабатывает callback - запрос, начинающийся с "change_".

    Эта функция вызывается при нажатии кнопки "Изменить", связанной с товаром.
    Она устанавливает текущее состояние машины состояний в `AddProduct.name`,
    чтобы пользователь мог начать процесс изменения информации о товаре.

    Args:
        callback (types.CallbackQuery): Объект callback-запроса, содержащий данные
            о нажатой кнопке, включая ID товара в формате `change_<product_id>`.
        state (FSMContext): Контекст машины состояний для управления процессом изменения.
        session (AsyncSession): Асинхронная сессия для взаимодействия с базой данных.

    Returns:
        None: Функция ничего не возвращает.

    """
    product_for_change = await orm_get_product(session, int(callback.data.split("_")[-1]))
    AddProduct.product_for_change = product_for_change

    await callback.answer()
    await callback.message.answer("Введите название товара", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(AddProduct.name)


@admin.message(StateFilter(None), F.text == "Добавить товар")
async def add_product(message: types.Message, state: FSMContext):
    """Инициализирует процесс добавления нового товара.

    Эта функция вызывается при вводе команды "Добавить товар", если у пользователя нет текущего состояния.
    Она запускает процесс добавления товара, начиная с запроса на ввод названия товара.

    Args:
        message (types.Message): Сообщение от пользователя.
        state (FSMContext): Контекст машины состояний, используемый для отслеживания прогресса добавления товара.

    Returns:
        None: Функция ничего не возвращает.

    """
    await message.answer("Введите название товара", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(AddProduct.name)


@admin.message(StateFilter('*'), F.text.casefold() == "отмена")
async def cancel(message: types.Message, state: FSMContext):
    """Отменяет текущее состояние.

    Эта функция используется для отмены текущего состояния.
    Она очищает состояние FSMContext, сбрасывает все связанные данные и завершает процесс.

    Args:
        message (types.Message): Сообщение от пользователя.
        state (FSMContext): Контекст машины состояний, который управляет процессом.

    Returns:
        None: Функция ничего не возвращает.

    """
    current_state = await state.get_state()
    if current_state is None:
        return
    if AddProduct.product_for_change:
        AddProduct.product_for_change = None
    await state.clear()
    await message.answer("Действия отменены", reply_markup=admin_kb)


@admin.message(StateFilter('*'), F.text.casefold() == "назад")
async def back_step(message: types.Message, state: FSMContext):
    """Обрабатывает команду возврата на предыдущий шаг в процессе.

    Эта функция позволяет пользователю вернуться к предыдущему шагу
    в рамках машины состояний. Она отслеживает текущее состояние
    и переводит пользователя в предыдущее состояние, если это возможно.

    Args:
        message (types.Message): Сообщение от пользователя.
        state (FSMContext): Контекст машины состояний, управляющий текущим процессом.

    Returns:
        None: Функция ничего не возвращает.

    """
    current_state = await state.get_state()
    if current_state == AddProduct.name:
        await message.answer('Предыдущего шага нет. Введите название товара или напишите "отмена"')
        return

    previous = None
    for step in AddProduct.__all_states__:
        if step == current_state:
            await state.set_state(previous)
            await message.answer(f"Вы вернулись к прошлому шагу \n {AddProduct.texts[previous.state]}")
            return
        previous = step


@admin.message(AddProduct.name, F.text)
async def add_name(message: types.Message, state: FSMContext):
    """Обрабатывает ввод названия товара в процессе добавления/изменения.

     Если пользователь отправляет название товара, оно сохраняется в контексте состояния,
     а если вводит точку (".") — используется текущее название товара (в случае изменения товара).
     Затем пользователь переходит в состояние ввода описания.

     Args:
         message (types.Message): Сообщение от пользователя.
         state (FSMContext): Контекст машины состояний, в котором сохраняются данные текущего процесса.

     Returns:
         None: Функция ничего не возвращает.

     """
    if message.text == "." and AddProduct.product_for_change:
        await state.update_data(name=AddProduct.product_for_change.name)
    else:
        await state.update_data(name=message.text)
    await message.answer("Введите описание товара")
    await state.set_state(AddProduct.description)


@admin.message(AddProduct.description, F.text)
async def add_description(message: types.Message, state: FSMContext, session: AsyncSession):
    """Обрабатывает ввод описания товара и переводит пользователя в состояние выбора категории.

    Если пользователь отправляет описание товара, оно сохраняется в контексте состояния,
    а если вводит точку (".") — используется текущее описание товара (в случае изменения товара).
    Затем пользователю отображаюся категории товаров на inline - клавиатуре.

    Args:
        message (types.Message): Сообщение от пользователя.
        state (FSMContext): Контекст машины состояний, в котором сохраняются данные текущего процесса.
        session (AsyncSession): Сессия базы данных для выполнения запросов.

    Returns:
        None: Функция ничего не возвращает.

    """
    if message.text == "." and AddProduct.product_for_change:
        await state.update_data(description=AddProduct.product_for_change.description)
    else:
        await state.update_data(description=message.text)

    categories = await orm_get_categories(session)
    await message.answer("Выберите категорию", reply_markup=get_callback_btns(
        btns={category.name: str(category.id) for category in categories}))
    await state.set_state(AddProduct.category)


@admin.callback_query(AddProduct.category)
async def category_choice_callback(callback: types.CallbackQuery, state: FSMContext):
    """Обрабатывает выбор категории пользователем и переводит его к этапу ввода цены товара.

    Args:
        callback (types.CallbackQuery): Объект обратного вызова, содержащий данные о выборе пользователя.
        state (FSMContext): Контекст машины состояний, в котором сохраняются данные текущего процесса.

    Returns:
        None: Функция ничего не возвращает.

    """
    await callback.answer()
    await state.update_data(category=callback.data)
    await callback.message.answer('Теперь введите цену товара.')
    await state.set_state(AddProduct.price)


@admin.message(AddProduct.price, F.text)
async def add_price(message: types.Message, state: FSMContext):
    """Обрабатывает ввод цены товара и переводит к этапу ввода количества товара.

    Если пользователь отправляет цену товара, она сохраняется в контексте состояния,
    а если вводит точку (".") — используется текущая цена товара (в случае изменения товара).
    Затем пользователь переходит в состояние ввода количества.

    Args:
        message (types.Message): Сообщение от пользователя.
        state (FSMContext): Контекст машины состояний, в котором сохраняются данные текущего процесса.

    Returns:
        None: Функция ничего не возвращает.

    Raises:
        ValueError: Eсли введенное значение нельзя преобразовать в число с плавающей запятой.

    """
    if message.text == "." and AddProduct.product_for_change:
        await state.update_data(price=AddProduct.product_for_change.price)
    else:
        try:
            float(message.text)
        except ValueError:
            await message.answer("Введите корректное значение цены")
            return

        await state.update_data(price=message.text)
    await message.answer("Введите количество товаров")
    await state.set_state(AddProduct.quantity)


@admin.message(AddProduct.quantity, F.text)
async def add_quantity(message: types.Message, state: FSMContext):
    """Обрабатывает ввод количества товара и переводит к этапу загрузки изображения товара.

     Если пользователь отправляет количество товара, оно сохраняется в контексте состояния,
     а если вводит точку (".") — используется текущее количество товара (в случае изменения товара).
     Затем пользователь переходит в состояние ввода фотографии.

     Args:
         message (types.Message): Сообщение от пользователя.
         state (FSMContext): Контекст машины состояний, в котором сохраняются данные текущего процесса.

     Returns:
         None: Функция ничего не возвращает.

     Raises:
         ValueError: Если введенное значение нельзя преобразовать в целое число.

     """
    if message.text == "." and AddProduct.product_for_change:
        await state.update_data(quantity=AddProduct.product_for_change.quantity)
    else:
        try:
            int(message.text)
        except ValueError:
            await message.answer("Введите корректное значение количества товара")
            return

        await state.update_data(quantity=message.text)
    await message.answer("Загрузите изображение товара")
    await state.set_state(AddProduct.image)


@admin.message(AddProduct.image, or_f(F.photo, F.text == "."))
async def add_image(message: types.Message, state: FSMContext, session: AsyncSession):
    """Обрабатывает загрузку изображения товара и завершает процесс добавления или изменения товара.

    Если пользователь отправляет фото товара, оно сохраняется в контексте состояния,
    а если пользователь вводит точку (".") — используется текущее изображение товара (в случае изменения товара).
    Затем данные сохраняются в базе данных, и пользователю отправляется уведомление о завершении операции.

    Args:
        message (types.Message): Сообщение от пользователя.
        state (FSMContext): Контекст машины состояний, в котором сохраняются данные текущего процесса.
        session (AsyncSession): Сессия для работы с базой данных, необходимая для добавления или обновления товара.

    Returns:
        None: Функция ничего не возвращает.

    """
    if message.text and message.text == "." and AddProduct.product_for_change:
        await state.update_data(image=AddProduct.product_for_change.image)
    if message.photo:
        await state.update_data(image=message.photo[-1].file_id)

    data = await state.get_data()
    if AddProduct.product_for_change:
        await orm_update_product(session, AddProduct.product_for_change.id, data)
    else:
        await orm_add_product(session, data)
    await message.answer("Товар добавлен/изменен", reply_markup=admin_kb)
    await state.clear()

    AddProduct.product_for_change = None
