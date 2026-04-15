# parent of all custom errors
# ye koi b exception ko apni jagah leke jayega
# idhr class appexception harr error class me he inherited


class AppException(Exception):
    """
    Base class for all custom application exceptions.
    Every custom exception should inherit from this.
    """

    def __init__(self, message: str = "Something went wrong"):
        self.message = message
        super().__init__(self.message)