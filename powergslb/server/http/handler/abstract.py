import abc

__all__ = ['AbstractContentHandler']


class AbstractContentHandler(object):
    """
    AbstractContentHandler class
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, request_handler):
        self.body = request_handler.body
        self.database = request_handler.database
	self.cache = request_handler.cache
        self.dirs = request_handler.dirs
        self.headers = request_handler.headers
        self.path = request_handler.path
        self.remote_ip = request_handler.remote_ip
        self.query = request_handler.query

    @abc.abstractmethod
    def content(self):
        pass
