from pymodbus.client.sync import ModbusTcpClient
from pymodbus.server.sync import StartTcpServer
from pymodbus.pdu import ModbusRequest
from pymodbus.device import ModbusDeviceIdentification
import struct
import signal

slaveId = 255

client = ModbusTcpClient("127.0.0.1", port=5020)

class ProxiedReadCoilsRequest(ModbusRequest):
    function_code = 1
    _rtu_frame_size = 8

    def __init__(self, address=None, count=None, unit=0, **kwargs):
        ModbusRequest.__init__(self, **kwargs)
        self.address = address
        self.count = count

    def encode(self):
        return struct.pack(">HH", self.address, self.count)

    def decode(self, data):
        self.address, self.count = struct.unpack(">HH", data)

    def get_response_pdu_size(self):
        count = self.count // 8
        if self.count % 8:
            count += 1

        return 1 + 1 + count

    def execute(self, context):
        result = client.read_coils(self.address, count=self.count, slave=255)
        return result

class ProxiedReadHoldingRegistersRequest(ModbusRequest):
    function_code = 3
    _rtu_frame_size = 8

    def __init__(self, address=None, count=None, unit=0, **kwargs):
        ModbusRequest.__init__(self, **kwargs)
        self.address = address
        self.count = count

    def encode(self):
        return struct.pack(">HH", self.address, self.count)

    def decode(self, data):
        self.address, self.count = struct.unpack(">HH", data)

    def get_response_pdu_size(self):
        return 1 + 1 + 2 * self.count

    def execute(self, context):
        result = client.read_holding_registers(self.address, count=self.count, slave=255)
        return result

class ProxiedReadInputRegistersRequest(ModbusRequest):
    function_code = 4
    _rtu_frame_size = 8

    def __init__(self, address=None, count=None, unit=0, **kwargs):
        ModbusRequest.__init__(self, **kwargs)
        self.address = address
        self.count = count

    def encode(self):
        return struct.pack(">HH", self.address, self.count)

    def decode(self, data):
        self.address, self.count = struct.unpack(">HH", data)

    def get_response_pdu_size(self):
        return 1 + 1 + 2 * self.count

    def execute(self, context):
        result = client.read_input_registers(self.address, count=self.count, slave=255)
        return result

StartTcpServer(address=("0.0.0.0", 502), custom_functions=[ProxiedReadInputRegistersRequest, ProxiedReadHoldingRegistersRequest, ProxiedReadCoilsRequest])
