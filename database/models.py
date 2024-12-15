from sqlalchemy import BigInteger, String, ForeignKey, Float, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs


class Base(AsyncAttrs, DeclarativeBase):
    """Базовый класс для всех моделей SQLAlchemy.

    Этот класс используется как основа для определения моделей SQLAlchemy в программе.
    Он наследуется от двух классов:
    - `AsyncAttrs`: поддерживает асинхронный доступ к атрибутам моделей.
    - `DeclarativeBase`: позволяет описывать модели с помощью классов.

    Attrs:
        Нет дополнительных атрибутов в данном классе. Он служит базой для других моделей.

    """
    pass


class Banner(Base):
    """Модель таблицы `banner`.

    Модель представляет собой таблицу баннеров.

    Attrs:
        id (int): Уникальный идентификатор баннера. Это первичный ключ, который
                      автоматически увеличивается при добавлении новой записи.
        name (str): Имя баннера, уникальное.
        image (str): Ссылка на изображение баннера (опционально).
        description (str): Описание баннера (опционально).

    """
    __tablename__ = 'banner'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(15), unique=True)
    image: Mapped[str] = mapped_column(String(150), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)


class Category(Base):
    """Модель для таблицы 'category'.

    Эта модель представляет таблицу категорий в базе данных, где каждая категория
    имеет уникальный идентификатор и название.

    Attrs:
        id (int): Уникальный идентификатор категории. Это первичный ключ, который
                    автоматически увеличивается при добавлении новой записи.
        name (str): Название категории. Это обязательное поле, не может быть NULL.

    """
    __tablename__ = 'category'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150))


class Product(Base):
    """Модель для таблицы 'product'.

    Эта модель представляет таблицу продуктов в базе данных, где каждый продукт
    имеет уникальный идентификатор, название, описание, цену, изображение, количество
    и связь с категорией.

    Attrs:
        id (int): Уникальный идентификатор продукта. Это первичный ключ, который
                    автоматически увеличивается при добавлении новой записи.
        name (str): Название продукта. Это обязательное поле, не может быть NULL.
        description (str): Описание продукта. Это поле  не может быть NULL.
        price (float): Цена продукта. Это обязательное поле, не может быть NULL.
        image (str): Ссылка на изображение продукта. Не может быть NULL.
        category_id (int): Идентификатор категории, к которой относится продукт.
                            Связан внешним ключом с атрибутом id класса category.
                            Это обязательное поле, не может быть NULL.
        quantity (int): Количество продукта в наличии. Это обязательное поле, не может быть NULL.

    """
    __tablename__ = 'product'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50))
    description: Mapped[str] = mapped_column(String(150))
    price: Mapped[float] = mapped_column(Float(asdecimal=True))
    image: Mapped[str] = mapped_column(String(150))
    category_id: Mapped[int] = mapped_column(ForeignKey('category.id', ondelete='CASCADE'))
    quantity: Mapped[int]


class User(Base):
    """Модель для таблицы 'cart'.

    Эта модель представляет собой таблицу пользователей,
    в которой имеется уникальный идентификатор записи в таблице, id пользователя в телеграм,
    его имя и фамилия в телеграм.

    Attrs:
        id (int): Уникальный идентификатор записи в таблице. Это первичный ключ, который
            автоматически увеличивается при добавлении новой записи.
        user_id (str): Уникальный идентификатор пользователя в телеграм. Это обязательное поле, не может быть NULL.
        first_name (str): Имя пользователя. Это поле может быть NULL.
        last_name (str): Фамилия пользователя. Это поле может быть NULL.

    """
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    first_name: Mapped[str] = mapped_column(String(150), nullable=True)
    last_name: Mapped[str] = mapped_column(String(150), nullable=True)


class Cart(Base):
    """Модель для таблицы 'cart'.

    Эта модель представляет собой таблицу товаров, добавленных пользователями в корзину,
    в которой имеется уникальный идентификатор записи в таблице, телеграм id пользователя,
    идентификатор продукта, добавленного в корзину, количество товаров в корзине.

    Attrs:
        id (int): Уникальный идентификатор записи в таблице. Это первичный ключ, который
            автоматически увеличивается при добавлении новой записи.
        user_id (str): Идентификатор пользователя. Это обязательное поле, не может быть NULL.
        product_id (str): Идентификатор продукта в корзине. Это обязательное поле, не может быть NULL.
        quantity (int): Количество продукта в наличии. Это обязательное поле, не может быть NULL.

    """
    __tablename__ = 'cart'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.user_id', ondelete='CASCADE'))
    product_id: Mapped[int] = mapped_column(ForeignKey('product.id', ondelete='CASCADE'))
    quantity: Mapped[int]

    product: Mapped['Product'] = relationship(backref='cart')
