class MethodBase:
    NAME = ''
    DESCRIPTION = ''
    EXEMPLE_PARAMS = {}

    @property
    def name(self) -> str:
        return self.NAME

    @property
    def description(self) -> str:
        return self.DESCRIPTION

    @property
    def exemple_params(self) -> dict:
        return self.EXEMPLE_PARAMS
