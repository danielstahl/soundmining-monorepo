import logging
import time
from pathlib import Path

from pythonosc import osc_bundle, osc_bundle_builder, osc_message, osc_message_builder, udp_client

from soundmining_library import buffered_playback

PLAYBACK_DELAY = 2.0


class SupercolliderClient:
    def start(self) -> None:
        logging.info("Start Supercollider Client")
        self.client = udp_client.SimpleUDPClient("127.0.0.1", 57110)
        self.buffered_playback = buffered_playback.BufferedPlayback(self.client)
        self.buffered_playback.start()
        self.reset_clock()

    def stop(self) -> None:
        logging.info("Stop Supercollider Client")
        self.buffered_playback.stop()

    def reset_clock(self) -> None:
        self.clock_time = time.time()

    def send_message(self, message: osc_message.OscMessage) -> None:
        logging.info("Send {} message".format(message.address))
        self.client.send(message)

    def send_bundle(self, bundle: osc_bundle.OscBundle) -> None:
        logging.info("Send bundle of size {} with time {}".format(bundle.num_contents, bundle.timestamp))
        self.client.send(bundle)

    def schedule_bundle(self, bundle: osc_bundle.OscBundle) -> None:
        logging.info("Schdule bundle with time {}".format(bundle.timestamp))
        self.buffered_playback.add_bundle(bundle)

    def get_playback_time(self) -> float:
        return time.time() - self.clock_time + PLAYBACK_DELAY

    def make_bundle(self, delta_time: float, messages: list[osc_message.OscMessage]) -> osc_bundle.OscBundle:
        builder = osc_bundle_builder.OscBundleBuilder(self.clock_time + PLAYBACK_DELAY + delta_time)
        for message in messages:
            builder.add_content(message)
        return builder.build()


def make_message(address: str, args: list[osc_message_builder.ArgValue]) -> osc_message.OscMessage:
    builder = osc_message_builder.OscMessageBuilder(address)
    for arg in args:
        builder.add_arg(arg)
    return builder.build()


def new_synth(instrument_name: str, add_action: int, node_id: int, args: list[osc_message_builder.ArgValue]) -> osc_message.OscMessage:
    message_args = [instrument_name, -1, add_action, node_id] + args
    return make_message("/s_new", message_args)


def new_synths(graph: list[list[any]]) -> list[osc_message.OscMessage]:
    osc_messages = []
    for message in graph:
        osc_messages.append(make_message("/s_new", message))
    return osc_messages


def group_head(group_id: int, node_id: int) -> osc_message.OscMessage:
    return make_message("/g_new", [node_id, 0, group_id])


def c_set() -> osc_message.OscMessage:
    return make_message("/c_set", [0, 0])


def group_tail(group_id: int, node_id: int) -> osc_message.OscMessage:
    return make_message("/g_new", [node_id, 3, group_id])


def add_head_node(group_id: int, node_id: int) -> osc_message.OscMessage:
    return make_message("/g_head", [group_id, node_id])


def add_tail_node(group_id: int, node_id: int) -> osc_message.OscMessage:
    return make_message("/g_tail", [group_id, node_id])


def free_all(node_id: int) -> osc_message.OscMessage:
    return make_message("/g_freeAll", [node_id])


def deep_free(node_id: int) -> osc_message.OscMessage:
    return make_message("/g_deepFree", [node_id])


def clear_sched() -> osc_message.OscMessage:
    return make_message("/clearSched", [])


def alloc_buffer(buffer_number: int, number_of_frames: int, number_of_channels: int = 2) -> osc_message.OscMessage:
    return make_message("/b_alloc", [buffer_number, number_of_frames, number_of_channels])


def free_buffer(buffer_number: int) -> osc_message.OscMessage:
    return make_message("/b_free", [buffer_number])


def alloc_read(buffer_number: int, path_name: str) -> osc_message.OscMessage:
    return make_message("/b_allocRead", [buffer_number, path_name])


def load_dir(path_name: Path) -> osc_message.OscMessage:
    return make_message("/d_loadDir", [str(path_name)])


def dump_osc(enable: bool) -> osc_message.OscMessage:
    return make_message("/dumpOSC", [enable])


def sc_notify(enable: bool) -> osc_message.OscMessage:
    return make_message("/notify", [enable])
