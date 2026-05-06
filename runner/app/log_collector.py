import logging
import threading

logger = logging.getLogger(__name__)

class LogCollector:
    def __init__(self, api_client, step_id: str):
        self.api_client = api_client
        self.step_id = step_id
        self.batch_size = 50
        self.logs_buffer = []
        self._lock = threading.RLock()
        self._stop_event = threading.Event()
        self._worker_thread = None
        self._line_counter = 0

    def start_collecting(self, container):
        """Starts collecting logs from the given container."""
        logger.info(f"Starting log collection for step {self.step_id}")
        self._stop_event.clear()
        self._worker_thread = threading.Thread(target=self._stream_logs, args=(container,))
        self._worker_thread.start()

    def stop_collecting(self):
        """Stops the log collection thread and flushes remaining logs."""
        logger.info(f"Stopping log collection for step {self.step_id}")
        self._stop_event.set()
        if self._worker_thread:
            # wait a short time for the thread to finish naturally after container stops
            self._worker_thread.join(timeout=2)
        self._flush_logs()

    def _stream_logs(self, container):
        try:
            # docker-py 7.x logs() strips stream-type from the multiplexed header.
            # Use attach_socket + frames_iter_no_tty to preserve stdout/stderr identity.
            from docker.utils.socket import frames_iter_no_tty, STDERR
            sock = container.client.api.attach_socket(
                container.id,
                params={'logs': 1, 'stream': 1, 'stdout': 1, 'stderr': 1, 'follow': 1}
            )
            for stream_id, data in frames_iter_no_tty(sock):
                if self._stop_event.is_set():
                    break
                stream = "stderr" if stream_id == STDERR else "stdout"
                for raw_line in data.decode('utf-8', errors='replace').splitlines():
                    line = raw_line.rstrip('\r')
                    with self._lock:
                        self.logs_buffer.append((line, stream))
                        if len(self.logs_buffer) >= self.batch_size:
                            self._flush_logs()
        except Exception as e:
            logger.error(f"Error streaming logs for step {self.step_id}: {e}")

    def _flush_logs(self):
        logs_to_send = []
        start_line = 1
        with self._lock:
            if not self.logs_buffer:
                return
            logs_to_send = list(self.logs_buffer)
            self.logs_buffer.clear()
            start_line = self._line_counter + 1
            self._line_counter += len(logs_to_send)

        self.api_client.send_step_logs(self.step_id, logs_to_send, start_line=start_line)
