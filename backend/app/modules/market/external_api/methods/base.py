class MethodBase:
    """Базовый класс метода провайдера.

    Метод — единица работы провайдера (загрузка тикеров, обновление цен и т.п.),
    вызывается из задачи через Provider.execute(method, **kwargs).
    NAME и PARAMETERS_SCHEMA декларируют метод и его параметры для админки.
    Контракт исполнения (сигнатуру run и формат коллбеков) задаёт докстринг подкласса.
    """

    NAME = ''
    EXEMPLE_PARAMS = {}
    PARAMETERS_SCHEMA: list[dict] = []

    @property
    def name(self) -> str:
        return self.NAME

    @property
    def exemple_params(self) -> dict:
        return self.EXEMPLE_PARAMS

    @property
    def parameters_schema(self) -> list[dict]:
        return self.PARAMETERS_SCHEMA
