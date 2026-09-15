class AnalysisError(Exception):
    def __init__(self, message: str, code: str = "invalid_data", status: int = 422):
        super().__init__(message)
        self.code = code
        self.status = status
