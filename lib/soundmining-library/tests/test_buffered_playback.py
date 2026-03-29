import unittest
from soundmining_library import buffered_playback
from pythonosc import osc_bundle
from pythonosc import osc_bundle_builder

import time


class TestBufferedPlayback(unittest.TestCase):
    def __make_simple_bundle(timestamp: float) -> osc_bundle.OscBundle:
        builder = osc_bundle_builder.OscBundleBuilder(timestamp)
        return builder.build()

    def test_due_bundle_queue(self) -> None:
        now = time.time()
        future_bundle_time = now + 1.0
        bundle = TestBufferedPlayback.__make_simple_bundle(future_bundle_time)
        bundle_queue = buffered_playback.PlaybackBundleQueue()
        bundle_queue.add_bundle(bundle)
        due_bundles = bundle_queue.get_due_bundles(now)
        self.assertAlmostEqual
        self.assertAlmostEqual(due_bundles[0].timestamp, future_bundle_time, places=3)

    def test_not_due_bundle_queue(self) -> None:
        now = time.time()
        future_bundle_time = now + 5.0
        bundle = TestBufferedPlayback.__make_simple_bundle(future_bundle_time)
        bundle_queue = buffered_playback.PlaybackBundleQueue()
        bundle_queue.add_bundle(bundle)
        due_bundles = bundle_queue.get_due_bundles(now)
        self.assertTrue(not due_bundles)

    def test_due_late_bundle_queue(self) -> None:
        now = time.time()
        future_bundle_time = now - 1.0
        bundle = TestBufferedPlayback.__make_simple_bundle(future_bundle_time)
        bundle_queue = buffered_playback.PlaybackBundleQueue()
        bundle_queue.add_bundle(bundle)
        due_bundles = bundle_queue.get_due_bundles(now)
        self.assertAlmostEqual(due_bundles[0].timestamp, bundle.timestamp)
