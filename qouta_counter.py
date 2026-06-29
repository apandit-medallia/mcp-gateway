from threading import Lock


class QuotaCounter:
    """
    Simple in-memory quota counter.
    This is global for entire gateway.

    In production
    This should be backed by Redis.
    Qouta should be maintained per user or per tenant level
    This qouta can be used for billing purpose as well.
    """

    def __init__(self, quota: int = 100):
        self.quota = quota
        self._count = 0
        self._lock = Lock()


    def check_qouta(self) -> tuple[bool]:
        """
        Increments the counter.

        Returns:
            (allowed)
        """

        with self._lock:
            if self._count >= self.quota:
                return True

            self._count += 1
            return False
