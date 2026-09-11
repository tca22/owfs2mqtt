from pyownet.protocol import proxy

class OWServerClient:
    def __init__(self, host, port, timeout=5):
        self.host = host
        self.port = port
        self.timeout = timeout
        self._proxy = None

    def connect(self):
        self._proxy = proxy(host=self.host, port=self.port)
        self._proxy.ping()
        return self

    def _ensure(self):
        if self._proxy is None:
            self.connect()
        return self._proxy

    def dir(self, path="/"):
        return self._ensure().dir(path)

    def read(self, path):
        value = self._ensure().read(path)
        if isinstance(value, bytes):
            value = value.decode("utf-8", errors="replace")
        return str(value).strip()

    def present(self, path):
        return bool(self._ensure().present(path))

    def close(self):
        # pyownet manages its own request sockets; drop proxy on shutdown.
        self._proxy = None
