class MethodBase:
    NAME = ''
    DESCRIPTION = ''
    EXEMPLE_PARAMS = {}
    PARAMETERS_SCHEMA: list[dict] = []

    @property
    def name(self) -> str:
        return self.NAME

    @property
    def description(self) -> str:
        return self.DESCRIPTION

    @property
    def exemple_params(self) -> dict:
        return self.EXEMPLE_PARAMS

    @property
    def parameters_schema(self) -> list[dict]:
        return self.PARAMETERS_SCHEMA
