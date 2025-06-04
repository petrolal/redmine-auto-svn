class Spinner:
    def __init__(self, message="Processando..."):
        self.message = message
        self._running = False
        self._thread = None
        self.spinner_cycle = ['|', '/', '-', '\\']

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._spin)
        self._thread.start()

    def _spin(self):
        idx = 0
        while self._running:
            print(f"\r{self.message} {self.spinner_cycle[idx % len(self.spinner_cycle)]}", end='', flush=True)
            idx += 1
            time.sleep(0.1)

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join()
        print("\r", end='', flush=True)