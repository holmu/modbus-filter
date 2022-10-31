#!/usr/bin/python

from pymodbus.client.sync import ModbusTcpClient
from pymodbus.server.sync import StartTcpServer
from pymodbus.pdu import ModbusRequest
from pymodbus.bit_read_message import ReadBitsRequestBase
import struct
import argparse

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
        result = client.read_coils(self.address, count=self.count, slave=self.unit_id)
        return result

class ProxiedReadDiscreteInputsRequest(ModbusRequest):
    function_code = 2

    def __init__(self, address=None, count=None, unit=0, **kwargs):
        ReadBitsRequestBase.__init__(self, address, count, unit, **kwargs)

    def execute(self, context):
        result = client.read_discrete_inputs(self.address, count=self.count, slave=self.unit_id)
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
        result = client.read_holding_registers(self.address, count=self.count, slave=self.unit_id)
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
        result = client.read_input_registers(self.address, count=self.count, slave=self.unit_id)
        return result

def main(client_address, client_port, listen_address, listen_port):
    global client
    client = ModbusTcpClient(client_address, port=client_port)
    StartTcpServer(address=(listen_address, listen_port), custom_functions=[
            ProxiedReadCoilsRequest,
            ProxiedReadDiscreteInputsRequest,
            ProxiedReadHoldingRegistersRequest,
            ProxiedReadInputRegistersRequest
        ])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Modbus/TCP filter forwarding only write requests.')
    parser.add_argument('--client-address', metavar='ip', type=str, default="127.0.0.1",
                        help='ip address of the Modbus/TCP client')
    parser.add_argument('--client-port', metavar='port', type=int, default=5020,
                        help='tcp port of the Modbus/TCP client')
    parser.add_argument('--listen-address', metavar='ip', type=str, default="0.0.0.0",
                    help='ip address of the Modbus/TCP filter to listen on')
    parser.add_argument('--listen-port', metavar='port', type=int, default=502,
                    help='tcp port of the Modbus/TCP filter to listen on')

    args = parser.parse_args()
    main(args.client_address, args.client_port, args.listen_address, args.listen_port)