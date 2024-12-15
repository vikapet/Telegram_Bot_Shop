from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_

from database.models import Banner, Cart, Category, Product, User


# Категории
async def orm_get_categories(session: AsyncSession):
    """Получение всех категорий из базы данных.

    Args:
        session (AsyncSession): Асинхронная сессия SQLAlchemy.

    Returns:
    List[Category]: Список объектов категории.

    """
    query = select(Category)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_create_categories(session: AsyncSession, categories: list):
    """Создает категории в базе данных, если их еще нет.

    Эта функция проверяет, существуют ли уже категории в базе данных. Если их нет, она добавляет
    переданный список категорий в таблицу `Category`.

    Args:
        session (AsyncSession): Асинхронная сессия для работы с базой данных.
        categories (List[str]): Список строк, содержащий названия категорий для добавления.

    Returns:
        None: Функция ничего не возвращает.

    """
    query = select(Category)
    result = await session.execute(query)
    if result.first():
        return
    session.add_all([Category(name=name) for name in categories])
    await session.commit()


# Баннер
async def orm_add_banner_description(session: AsyncSession, data: dict):
    """Добавляет описания баннеров в базу данных.

    Функция проверяет, существуют ли записи в таблице Banner. Если нет,
    она добавляет название и описание баннера в базу данных.

    Args:
        session (AsyncSession): Асинхронная сессия для взаимодействия с базой данных.
        data (dict): Словарь с названием баннера и его описанием. Формат: {name: description}.

    Returns:
        None: Функция ничего не возвращает.

    """
    query = select(Banner)
    result = await session.execute(query)
    if result.first():
        return
    session.add_all([Banner(name=name, description=description) for name, description in data.items()])
    await session.commit()


async def orm_change_banner_image(session: AsyncSession, name: str, image: str):
    """Обновляет изображение для баннера в таблице `Banner`.

    Функция ищет баннер в базе данных по его имени и для данного баннера обновляет изображение.

    Args:
        session (AsyncSession): Асинхронная сессия для взаимодействия с базой данных.
        name (str): Название баннера, для которого нужно обновить изображение.
        image (str): Идентификатор изображения.

    Returns:
        None: Функция ничего не возвращает.

    """
    query = update(Banner).where(Banner.name == name).values(image=image)
    await session.execute(query)
    await session.commit()


async def orm_get_banner(session: AsyncSession, name: str):
    """Получает баннер для указанной страницы.

    Функция ищет баннер, у которого название совпадает с именем страницы, и возвращает его объект.

    Args:
        session (AsyncSession): Асинхронная сессия для работы с базой данных.
        name (str): Название страницы, для которой нужно получить баннер.

    Returns:
        Banner: Объект баннера, соответствующий странице.

    """
    query = select(Banner).where(Banner.name == name)
    result = await session.execute(query)
    return result.scalar()


async def orm_get_info_pages(session: AsyncSession):
    """Возвращает список объектов баннеров.

    Args:
        session (AsyncSession): Асинхронная сессия для работы с базой данных.

    Returns:
        list[Banner]: Список всех объектов баннеров.

    """
    query = select(Banner)
    result = await session.execute(query)
    return result.scalars().all()


# Взаимодействие с продуктами
async def orm_add_product(session: AsyncSession, data: dict):
    """Добавляет новый продукт в базу данных.

     Эта функция принимает словарь `data`, который должен содержать информацию о новом
     продукте, и добавляет этот продукт в базу данных. Все поля продукта, такие как
     имя, описание, цена, количество, изображение и категория, извлекаются из словаря
     и сохраняются в таблице `Product`.

     Args:
         session (AsyncSession): Асинхронная сессия SQLAlchemy для взаимодействия с базой данных.
         data (dict): Словарь с данными о продукте. Ожидаемые ключи:
             - "name" (str): Название продукта.
             - "description" (str): Описание продукта.
             - "price" (float): Цена продукта.
             - "quantity" (int): Количество продукта.
             - "image" (str): Ссылка на изображение продукта.
             - "category" (int): ID категории продукта.

     Returns:
         None: Функция ничего не возвращает.

     """
    obj = Product(
        name=data["name"],
        description=data["description"],
        price=float(data["price"]),
        quantity=int(data["quantity"]),
        image=data["image"],
        category_id=int(data["category"]),
    )
    session.add(obj)
    await session.commit()


async def orm_get_products(session: AsyncSession, category_id):
    """Получает список продуктов, отфильтрованных по категории.

    Эта функция выполняет запрос к базе данных, чтобы извлечь все продукты,
    относящиеся к указанной категории. Продукты возвращаются в виде списка.

    Args:
        session (AsyncSession): Асинхронная сессия SQLAlchemy для работы с базой данных.
        category_id (int): ID категории, по которой будут отфильтрованы продукты.

    Returns:
        list[Product]: Список объектов `Product`, соответствующих заданной категории.

    """
    query = select(Product).where(Product.category_id == category_id)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_get_product(session: AsyncSession, product_id: int):
    """Получает один продукт по ID.

    Эта функция выполняет запрос к базе данных для извлечения одного продукта по
    его уникальному идентификатору.

    Args:
        session (AsyncSession): Асинхронная сессия SQLAlchemy для работы с базой данных.
        product_id (int): ID продукта, который требуется извлечь.

    Returns:
        Product | None: Объект `Product`, если продукт найден, или `None`, если продукт с таким ID не существует.

    """
    query = select(Product).where(Product.id == product_id)
    result = await session.execute(query)
    return result.scalar()


async def orm_update_product(session: AsyncSession, product_id: int, data):
    """Обновляет данные продукта в базе данных.

    Эта функция выполняет обновление данных продукта по его ID. Все поля продукта
    могут быть изменены, включая имя, описание, цену, количество, изображение и категорию.

    Args:
        session (AsyncSession): Асинхронная сессия SQLAlchemy для работы с базой данных.
        product_id (int): Уникальный идентификатор продукта, который нужно обновить.
        data (dict): Словарь с новыми данными для обновления продукта. Ожидаемые ключи:
            - "name" (str): Название продукта.
            - "description" (str): Описание продукта.
            - "price" (float): Цена продукта.
            - "quantity" (int): Количество продукта на складе.
            - "image" (str): Ссылка или путь к изображению продукта.
            - "category" (int): ID категории продукта.

    Returns:
        None: Функция ничего не возвращает.

    """
    query = update(Product).where(Product.id == product_id).values(
            name=data["name"],
            description=data["description"],
            price=float(data["price"]),
            quantity=int(data["quantity"]),
            image=data["image"],
            category_id=int(data["category"]),
        )

    await session.execute(query)
    await session.commit()


async def orm_delete_product(session: AsyncSession, product_id: int):
    """Удаляет продукт из базы данных по его ID.

    Эта функция выполняет запрос на удаление продукта из базы данных, используя его уникальный идентификатор.

    Args:
        session (AsyncSession): Асинхронная сессия SQLAlchemy для работы с базой данных.
        product_id (int): Уникальный идентификатор продукта, который нужно удалить.

    Returns:
        None: Функция ничего не возвращает.

    """
    query = delete(Product).where(Product.id == product_id)
    await session.execute(query)
    await session.commit()


# Добавление юзера в БД
async def orm_add_user(
        session: AsyncSession,
        user_id: int,
        first_name: str | None = None,
        last_name: str | None = None):
    """Добавляет нового пользователя в базу данных, если его еще не существует.

    Args:
        session (AsyncSession): Асинхронная сессия для работы с базой данных.
        user_id (int): Уникальный идентификатор пользователя.
        first_name (str | None): Имя пользователя. По умолчанию None.
        last_name (str | None): Фамилия пользователя. По умолчанию None.

    Returns:
        None: Функция ничего не возвращает.

    """
    query = select(User).where(User.user_id == user_id)
    result = await session.execute(query)
    if result.first() is None:
        session.add(User(user_id=user_id, first_name=first_name, last_name=last_name))
        await session.commit()


# Корзина
async def orm_add_to_cart(session: AsyncSession, user_id: int, product_id: int):
    """Добавляет товар в корзину пользователя или обновляет количество товара в корзине.

    Функция извлекает продукт из базы данных по id. Если продукта нет или он закончился, возвращает False.
    Затем извлекается запись в корзине пользователя по его id и id продукта. Если запись есть,
    продукт добавляется в корзину пользователя, если нет - создается новая запись.

    Args:
        session (AsyncSession): Асинхронная сессия для работы с базой данных.
        user_id (int): Уникальный идентификатор пользователя.
        product_id (int): Уникальный идентификатор товара.

    Returns:
        bool: True, если товар был добавлен в корзину или была создана новая запись.
            False, если товара нет или его количество равно нулю (или меньше нуля).

    """
    item_query = select(Product).where(Product.id == product_id).with_for_update()
    item_res = await session.execute(item_query)
    product = item_res.scalar()

    if not product or product.quantity <= 0:
        return False

    cart_query = select(Cart).where(and_(Cart.user_id == user_id, Cart.product_id == product_id))
    cart_res = await session.execute(cart_query)
    cart = cart_res.scalar()

    if cart:
        cart.quantity += 1
        product.quantity -= 1
    else:
        cart = Cart(
            user_id=user_id,
            product_id=product_id,
            quantity=1
        )
        product.quantity -= 1
        session.add(cart)

    await session.commit()
    return True


async def orm_get_user_carts(session: AsyncSession, user_id):
    """Извлекает все товары, находящиеся в корзине пользователя, включая данные о товарах.

    Args:
        session (AsyncSession): Асинхронная сессия для работы с базой данных.
        user_id (int): Уникальный идентификатор пользователя.

    Returns:
        list[Cart]: Список объектов корзины с включенными данными о товаре.

    """
    query = select(Cart).where(Cart.user_id == user_id).options(joinedload(Cart.product))
    result = await session.execute(query)
    return result.scalars().all()


async def orm_delete_from_cart(session: AsyncSession, user_id: int, product_id: int):
    """Удаляет товар из корзины пользователя, возвращая его количество обратно на "склад".

    Args:
        session (AsyncSession): Асинхронная сессия для работы с базой данных.
        user_id (int): Уникальный идентификатор пользователя.
        product_id (int): Уникальный идентификатор товара.

    Returns:
        None: Функция ничего не возвращает.

    """
    query = select(Cart).where(Cart.user_id == user_id, Cart.product_id == product_id).options(joinedload(Cart.product))
    res = await session.execute(query)
    cart = res.scalar()

    if cart:
        product = cart.product
        product.quantity += cart.quantity
        await session.delete(cart)
        await session.commit()


async def orm_reduce_product_in_cart(session: AsyncSession, user_id: int, product_id: int):
    """Уменьшает количество товара к ворзине.

    Функция уменьшает количество товара в корзине пользователя на 1 и увеличивает количество товара на "складе" на 1.
    Если в корзине остался только один товар, он удаляется из нее.

    Args:
        session (AsyncSession): Асинхронная сессия для работы с базой данных.
        user_id (int): Уникальный идентификатор пользователя.
        product_id (int): Уникальный идентификатор товара.

    Returns:
        bool: Возвращает True, если запись для данного пользователя и данного товара существует в корзине,
            иначе - False.

    """
    query = select(Cart).where(Cart.user_id == user_id, Cart.product_id == product_id).options(joinedload(Cart.product))
    cart_res = await session.execute(query)
    cart = cart_res.scalar()

    if cart:
        if cart.quantity > 1:
            cart.quantity -= 1
            cart.product.quantity += 1
            await session.commit()
            return True
        else:
            cart.product.quantity += 1
            await session.delete(cart)
            await session.commit()
            return False
    return False
