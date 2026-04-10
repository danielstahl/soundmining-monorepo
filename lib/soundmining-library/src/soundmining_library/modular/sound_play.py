import logging

from soundmining_library import supercollider_client
from soundmining_library.supercollider_client import SupercolliderClient


class BufNumAllocator:
    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.buf_num = 0

    def next(self) -> int:
        next_buf_num = self.buf_num
        self.buf_num = next_buf_num + 1
        return next_buf_num


class SoundPlay:
    def __init__(self, sound_path: str, start: float, end: float) -> None:
        self.sound_path = sound_path
        self.start = start
        self.end = end
        self.buf_num = None

    def absolut_time(self, time: float, rate: float) -> float:
        return abs((time - self.start) / rate)

    def duration(self, rate: float) -> float:
        return self.absolut_time(self.end, rate)

    def init(self, buf_num: int, client: SupercolliderClient) -> None:
        if not self.buf_num:
            self.buf_num = buf_num
            client.send_message(supercollider_client.alloc_read(buf_num, self.sound_path))
        else:
            logging.warning(f"{self.sound_path} is already allocated with buf num {self.buf_num}")

    def stop(self, client: SupercolliderClient) -> None:
        if self.buf_num:
            client.send_message(supercollider_client.free_buffer(self.buf_num))
            self.buf_num = None
        else:
            logging.warn(f"{self.sound_path} is not allocated")


class ImpulseResponse:
    def __init__(self, left_sound_path: str, right_sound_path: str) -> None:
        self.left_sound_path = left_sound_path
        self.righ_sound_path = right_sound_path
        self.left_buf_num = None
        self.right_buf_num = None

    def init(self, left_buf_num: int, right_buf_num: int, client: SupercolliderClient) -> None:
        if not self.left_buf_num:
            self.left_buf_num = left_buf_num
            client.send_message(supercollider_client.alloc_read(self.left_buf_num, self.left_sound_path))
        if not self.right_buf_num:
            self.right_buf_num = right_buf_num
            client.send_message(supercollider_client.alloc_read(self.right_buf_num, self.righ_sound_path))

    def stop(self, client: SupercolliderClient) -> None:
        if self.left_buf_num:
            client.send_message(supercollider_client.free_buffer(self.left_buf_num))
            self.left_buf_num = None
        if not self.right_buf_num:
            client.send_message(supercollider_client.free_buffer(self.right_buf_num))
            self.right_buf_num = None
