
from dataclasses import dataclass, field
from pythonosc import osc_bundle
from queue import PriorityQueue
import time
import logging
import concurrent.futures
from pythonosc import udp_client

BUFFER_TIME = 3.0


class PlaybackBundleQueue:
    def __init__(self) -> None:
        self.bundle_queue = PriorityQueue()

    def reset(self) -> None:
        while not self.bundle_queue.empty():
            self.bundle_queue.get()

    def add_bundle(self, bundle: osc_bundle.OscBundle) -> None:
        self.bundle_queue.put(PrioritizedBundle(timestamp=bundle.timestamp, bundle=bundle))

    def is_peek_due(self, current_time: float) -> bool:
        if self.bundle_queue.empty():
            return False
        else:
            peek_timesamp = self.bundle_queue.queue[0].timestamp
            return (peek_timesamp - BUFFER_TIME) < current_time

    def get_due_bundles(self, current_time: int) -> list[osc_bundle.OscBundle]:
        result = []
        while self.is_peek_due(current_time):
            result.append(self.bundle_queue.get().bundle)
        return result


@dataclass(order=True)
class PrioritizedBundle:
    timestamp: float
    bundle: osc_bundle.OscBundle = field(compare=False)


class BufferedPlayback:
    def __init__(self, udp_client: udp_client.UDPClient) -> None:
        self.playback_bundle_queue = PlaybackBundleQueue()
        self.udp_client = udp_client
        self.started = False
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)

    def run_schedule_bundles(self) -> None:
        logging.info("Starting schedule bundles")
        while self.started:
            due_bundles = self.playback_bundle_queue.get_due_bundles(time.time())
            for bundle in due_bundles:
                logging.info("Send bundle of size {} with time {}".format(bundle.size, bundle.timestamp))
                self.udp_client.send(bundle)
            time.sleep(2)
        logging.info("Stop schedule bundles")

    def add_bundle(self, bundle: osc_bundle.OscBundle) -> None:
        self.playback_bundle_queue.add_bundle(bundle)

    def start(self) -> None:
        logging.info("Starting BufferedPlayback")
        self.started = True
        self.executor.submit(self.run_schedule_bundles)

    def stop(self) -> None:
        logging.info("Stopping BufferedPlayback")
        self.started = False
