class Paginator:
    """Класс для управления пагинацией массива данных.

    Этот класс предоставляет методы для работы с массивом,
    включая получение картины по текущей странице и проверку наличия предыдущей и следующей страниц.

    Attrs:
        array (list | tuple): Исходный массив данных, которых нужно пагинировать.
        page (int): Текущий номер страницы. По умолчанию 1.
        len (int): Длина исходного массива.
        pages (int): Общее количество страниц.

    Methods:
        __init__(): инициализирует объект класса Paginator

        get_item() -> list | tuple:
              озвращает элемент текущей страницы.

        has_next() -> int | bool:
            Проверяет наличие следующей страницы. Возвращает номер следующей страницы или False.

        has_previous() -> int | bool:
            Проверяет наличие предыдущей страницы. Возвращает номер предыдущей страницы или False.

    """
    def __init__(self, array: list | tuple, page: int = 1):
        """Инициализирует объект класса Paginator.

        Raises:
            ValueError: Если массив данных пустой или номер страницы отрицательныый.
            IndexError: Если общее число страниц меньше номера текущей страницы.

        """
        if not array:
            raise ValueError("Array cannot be empty")
        if page < 1:
            raise ValueError("Page must be greater than 0")
        if len(array) < page:
            raise IndexError("This page doesn't exist")

        self.array = array
        self.page = page
        self.len = len(self.array)
        self.pages = self.len

    def get_item(self):
        """Возвращает элемент текущей страницы.

        Returns:
            Any: элемент по индексу.

        """
        ind = self.page - 1
        return self.array[ind]

    def has_next(self):
        """Проверяет наличие следующей страницы.

        Returns:
            int | bool: Номер следующей страницы, если она существует, иначе - False.

        """
        if self.page < self.pages:
            return self.page + 1
        return False

    def has_previous(self):
        """Проверяет наличие предыдущей страницы.

        Returns:
            int | bool: Номер предыдущей страницы, если она существует, иначе - False.

        """
        if self.page > 1:
            return self.page - 1
        return False
