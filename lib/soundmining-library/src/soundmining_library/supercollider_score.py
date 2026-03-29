
from pythonosc import osc_bundle
from pythonosc import osc_message
from soundmining_library import supercollider_client
import io


class SupercolliderScore:
    def __init__(self) -> None:
        self.messages = []

    def reset(self) -> None:
        self.messages = []

    def add_bundle(self, bundle: osc_bundle.OscBundle) -> None:
        for message in bundle:
            match message:
                case osc_bundle.OscBundle:
                    self.add_bundle(message)
                case osc_message.OscMessage:
                    self.add_message(bundle.timestamp, message)

    def add_message(self, message: osc_message.OscMessage, time: float = 0) -> None:
        self.messages.append((time, message))

    def message_duration(self, message: osc_message.OscMessage) -> float:
        try:
            params = message.params
            dur_index = params.index("dur")
            return params[dur_index + 1]
        except ValueError:
            return 0

    def score_address(self, address: str) -> str:
        return address.replace('/', '\\', 1)

    def new_synth_message_to_string(self, timestamp: float, message: osc_message.OscMessage) -> str:
        params = message.params
        instrument_args = []
        instrument_args.append("\\s_new")
        instrument_args.append(f"\\{params[0]}")
        instrument_args.append(str(params[1]))
        instrument_args.append(str(params[2]))
        instrument_args.append(str(params[3]))
        is_array_argument = False
        for i in range(4, len(params), 2):
            instrument_args.append(f"\\{params[i]}")
            match params[i + 1]:
                case list() as array_param:
                    # if len(array_param) > 1:
                    is_array_argument = True
                    joined_array_param = ", ".join([str(p) for p in array_param])
                    instrument_args.append(f"[{joined_array_param}]")
                case _ as default_param:
                    instrument_args.append(str(default_param))
        joined_instrument_args = ", ".join(instrument_args)
        instrument_args_str = f"[{joined_instrument_args}]"
        if is_array_argument:
            instrument_args_str = instrument_args_str + ".asOSCArgArray"
        messaage_str = f"[{str(timestamp)}, {instrument_args_str}]"
        return messaage_str

    def message_to_string(self, timestamp: float, message: osc_message.OscMessage) -> str:
        match message.address:
            case "/c_set":
                return f"[{timestamp}, [{self.score_address(message.address)}, {message.params[0]}, {message.params[1]}]]"
            case "/g_new":
                return f"[{timestamp}, [{self.score_address(message.address)}, {message.params[0]}, {message.params[1]}, {message.params[2]}]]"
            case "/d_loadDir":
                return f"[{timestamp}, [{self.score_address(message.address)}, '{message.params[0]}']]"
            case "/b_allocRead":
                return f"[{timestamp}, [{self.score_address(message.address)}, {message.params[0]}, '{message.params[1]}']]"
            case "/s_new":
                return self.new_synth_message_to_string(timestamp, message)
            case _ as unknown_address:
                raise Exception(f"{unknown_address} is not a known osc message address")

    def total_duration(self) -> float:
        duration = 0
        for timestamp, message in self.messages:
            duration = max(duration, timestamp + self.message_duration(message))
        return duration

    def make_score(self, io_stream: io.TextIOBase) -> None:
        sorted_messages = sorted(self.messages, key=lambda pair: pair[0])
        duration = self.total_duration()
        sorted_messages.append((duration, supercollider_client.c_set()))
        io_stream.write("[\n")
        message_strings = []
        for timestamp, message in sorted_messages:
            message_string = self.message_to_string(timestamp, message)
            message_strings.append(message_string)
        io_stream.write(",\n".join(message_strings))
        io_stream.write("\n]\n")

    def make_score_file(self, file_name: str) -> None:
        with open(file_name, "w+") as io_file:
            self.make_score(io_file)

    def make_score_string(self) -> None:
        io_str = io.StringIO()
        self.make_score(io_str)
        return io_str.getvalue()
