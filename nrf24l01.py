################################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#    Copyright (c) 2021, Kalcifer
#
#    For more information, see https://github.com/K4LCIFER/nrf24l01-debugger
################################################################################
# 1. [nRF24L01 Datasheet](<project_directory>/nRF24L01-datasheet.pdf)
################################################################################

import serial
import platform


BAUD = 9600
if platform.system() == 'Linux':
    PORT = '/dev/ttyUSB0'
elif platform.system() == 'Windows':
    PORT = 'COM99'  # I'm not sure what COM port this should be.
else:
    print('Platform \"' + platform.system() + '\" is not supported!')

# TODO: Add the ability to detect the presence of a device or not, and raise an
# error to say that the device was not found.


# Command names and words. See [1] Section 8.3.1 Table 19.
COMMANDS = {
    'R_REGISTER': 0x00,
    'W_REGISTER': 0x20,
    'R_RX_PAYLOAD': 0x61,
    'W_TX_PAYLOAD': 0xA0,
    'FLUSH_TX': 0xE1,
    'FLUSH_RX': 0xE2,
    'REUSE_TX_PL': 0xE3,
    'R_RX_PL_WID': 0x60,
    'W_ACK_PAYLOAD': 0xA8,
    'W_TX_PAYLOAD_NOACK': 0xB0,
    'NOP': 0xFF,
}


# Register mnemonics and addresses with their bit mnemonics and bit positions.
# See [1] Section 9.1 Table 27.
REGISTER_MAP = {
    'CONFIG': {
        'ADDRESS': 0x00,
        'NUMBER_OF_DATA_BYTES': 1,
        'RESET_VALUE': 0x08,
        'MASK_RX_DR': {'LENGTH': 1, 'OFFSET': 6, 'RESET_VALUE': 0x00},
        'MASK_TX_DS': {'LENGTH': 1, 'OFFSET': 5, 'RESET_VALUE': 0x00},
        'MASK_MAX_RT': {'LENGTH': 1, 'OFFSET': 4, 'RESET_VALUE': 0x00},
        'EN_CRC': {'LENGTH': 1, 'OFFSET': 3, 'RESET_VALUE': 0x00},
        'CRCO': {'LENGTH': 1, 'OFFSET': 2, 'RESET_VALUE': 0x01},
        'PWR_UP': {'LENGTH': 1, 'OFFSET': 1, 'RESET_VALUE': 0x00},
        'PRIM_RX': {'LENGTH': 1, 'OFFSET': 0, 'RESET_VALUE': 0x00},
    },
    'EN_AA': {
        'ADDRESS': 0x01,
        'NUMBER_OF_DATA_BYTES': 1,
        'RESET_VALUE': 0x3F,
        'ENAA_P5': {'LENGTH': 1, 'OFFSET': 5, 'RESET_VALUE': 0x01},
        'ENAA_P4': {'LENGTH': 1, 'OFFSET': 4, 'RESET_VALUE': 0x01},
        'ENAA_P3': {'LENGTH': 1, 'OFFSET': 3, 'RESET_VALUE': 0x01},
        'ENAA_P2': {'LENGTH': 1, 'OFFSET': 2, 'RESET_VALUE': 0x01},
        'ENAA_P1': {'LENGTH': 1, 'OFFSET': 1, 'RESET_VALUE': 0x01},
        'ENAA_P0': {'LENGTH': 1, 'OFFSET': 0, 'RESET_VALUE': 0x01},
    },
    'EN_RXADDR': {
        'ADDRESS': 0x02,
        'NUMBER_OF_DATA_BYTES': 1,
        'RESET_VALUE': 0x02,
        'ERX_P5': {'LENGTH': 1, 'OFFSET': 5, 'RESET_VALUE': 0x00},
        'ERX_P4': {'LENGTH': 1, 'OFFSET': 4, 'RESET_VALUE': 0x00},
        'ERX_P3': {'LENGTH': 1, 'OFFSET': 3, 'RESET_VALUE': 0x00},
        'ERX_P2': {'LENGTH': 1, 'OFFSET': 2, 'RESET_VALUE': 0x00},
        'ERX_P1': {'LENGTH': 1, 'OFFSET': 1, 'RESET_VALUE': 0x01},
        'ERX_P0': {'LENGTH': 1, 'OFFSET': 0, 'RESET_VALUE': 0x01},
    },
    'SETUP_AW': {
        'ADDRESS': 0x03,
        'NUMBER_OF_DATA_BYTES': 1,
        'RESET_VALUE': 0x03,
        'AW': {'LENGTH': 2, 'OFFSET': 0, 'RESET_VALUE': 0x03},
    },
    'SETUP_RETR': {
        'ADDRESS': 0x04,
        'NUMBER_OF_DATA_BYTES': 1,
        'RESET_VALUE': 0x03,
        'ARD': {'LENGTH': 4, 'OFFSET': 4, 'RESET_VALUE': 0x00},
        'ARC': {'LENGTH': 4, 'OFFSET': 0, 'RESET_VALUE': 0x03},
    },
    'RF_CH': {
        'ADDRESS': 0x05,
        'NUMBER_OF_DATA_BYTES': 1,
        'RESET_VALUE': 0x02,
        'RF_CH': {'LENGTH': 7, 'OFFSET': 0, 'RESET_VALUE': 0x02},
    },
    'RF_SETUP': {
        'ADDRESS': 0x06,
        'NUMBER_OF_DATA_BYTES': 1,
        'RESET_VALUE': 0x0E,
        'CONT_WAVE': {'LENGTH': 1, 'OFFSET': 7, 'RESET_VALUE': 0x00},
        'RF_DR_LOW': {'LENGTH': 1, 'OFFSET': 5, 'RESET_VALUE': 0x00},
        'PLL_LOCK': {'LENGTH': 1, 'OFFSET': 4, 'RESET_VALUE': 0x00},
        'RF_DR_HIGH': {'LENGTH': 1, 'OFFSET': 3, 'RESET_VALUE': 0x01},
        'RF_PWR': {'LENGTH': 2, 'OFFSET': 1, 'RESET_VALUE': 0x03},
    },
    'STATUS': {
        'ADDRESS': 0x07,
        'NUMBER_OF_DATA_BYTES': 1,
        'RESET_VALUE': 0x0E,
        'RX_DR': {'LENGTH': 1, 'OFFSET': 6, 'RESET_VALUE': 0x00},
        'TX_DS': {'LENGTH': 1, 'OFFSET': 5, 'RESET_VALUE': 0x00},
        'MAX_RT': {'LENGTH': 1, 'OFFSET': 4, 'RESET_VALUE': 0x00},
        'RX_P_NO': {'LENGTH': 3, 'OFFSET': 1, 'RESET_VALUE': 0x07},
        'TX_FULL': {'LENGTH': 1, 'OFFSET': 0, 'RESET_VALUE': 0x00},
    },
    'OBSERVE_TX': {
        'ADDRESS': 0x08,
        'NUMBER_OF_DATA_BYTES': 1,
        'RESET_VALUE': 0x3F,
        'PLOS_CNT': {'LENGTH': 4, 'OFFSET': 4, 'RESET_VALUE': 0x00},
        'ARC_CNT': {'LENGTH': 4, 'OFFSET': 0, 'RESET_VALUE': 0x00},
    },
    'RPD': {
        'ADDRESS': 0x09,
        'NUMBER_OF_DATA_BYTES': 1,
        'RESET_VALUE': 0x00,
        'RPD': {'LENGTH': 1, 'OFFSET': 0, 'RESET_VALUE': 0x00},
    },  # RPD or CD?
    'RX_ADDR_P0': {
        'ADDRESS': 0x0A,
        'NUMBER_OF_DATA_BYTES': 5,
        'RESET_VALUE': 0xE7E7E7E7E7,
    },
    'RX_ADDR_P1': {
        'ADDRESS': 0x0B,
        'NUMBER_OF_DATA_BYTES': 5,
        'RESET_VALUE': 0xC2C2C2C2C2,
    },
    'RX_ADDR_P2': {
        'ADDRESS': 0x0C,
        'NUMBER_OF_DATA_BYTES': 1,
        'RESET_VALUE': 0xC3,
    },
    'RX_ADDR_P3': {
        'ADDRESS': 0x0D,
        'NUMBER_OF_DATA_BYTES': 1,
        'RESET_VALUE': 0xC4,
    },
    'RX_ADDR_P4': {
        'ADDRESS': 0x0E,
        'NUMBER_OF_DATA_BYTES': 1,
        'RESET_VALUE': 0xC5,
    },
    'RX_ADDR_P5': {
        'ADDRESS': 0x0F,
        'NUMBER_OF_DATA_BYTES': 1,
        'RESET_VALUE': 0xC6,
    },
    'TX_ADDR': {
        'ADDRESS': 0x10,
        'NUMBER_OF_DATA_BYTES': 5,
        'RESET_VALUE': 0xE7E7E7E7E7,
    },
    'RX_PW_P0': {
        'ADDRESS': 0x11,
        'NUMBER_OF_DATA_BYTES': 1,
        'RESET_VALUE': 0x00,
        'RX_PW_P0': {'LENGTH': 6, 'OFFSET': 0, 'RESET_VALUE': 0x00},
    },
    'RX_PW_P1': {
        'ADDRESS': 0x12,
        'NUMBER_OF_DATA_BYTES': 1,
        'RESET_VALUE': 0x00,
        'RX_PW_P1': {'LENGTH': 6, 'OFFSET': 0, 'RESET_VALUE': 0x00},
    },
    'RX_PW_P2': {
        'ADDRESS': 0x13,
        'NUMBER_OF_DATA_BYTES': 1,
        'RESET_VALUE': 0x00,
        'RX_PW_P2': {'LENGTH': 6, 'OFFSET': 0, 'RESET_VALUE': 0x00},
    },
    'RX_PW_P3': {
        'ADDRESS': 0x14,
        'NUMBER_OF_DATA_BYTES': 1,
        'RESET_VALUE': 0x00,
        'RX_PW_P3': {'LENGTH': 6, 'OFFSET': 0, 'RESET_VALUE': 0x00},
    },
    'RX_PW_P4': {
        'ADDRESS': 0x15,
        'NUMBER_OF_DATA_BYTES': 1,
        'RESET_VALUE': 0x00,
        'RX_PW_P4': {'LENGTH': 6, 'OFFSET': 0, 'RESET_VALUE': 0x00},
    },
    'RX_PW_P5': {
        'ADDRESS': 0x16,
        'NUMBER_OF_DATA_BYTES': 1,
        'RESET_VALUE': 0x00,
        'RX_PW_P5': {'LENGTH': 6, 'OFFSET': 0, 'RESET_VALUE': 0x00},
    },
    'FIFO_STATUS': {
        'ADDRESS': 0x17,
        'NUMBER_OF_DATA_BYTES': 1,
        'RESET_VALUE': 0x11,
        'TX_REUSE': {'LENGTH': 1, 'OFFSET': 6, 'RESET_VALUE': 0x00},
        'TX_FULL': {'LENGTH': 1, 'OFFSET': 5, 'RESET_VALUE': 0x00},
        'TX_EMPTY': {'LENGTH': 1, 'OFFSET': 4, 'RESET_VALUE': 0x01},
        'RX_FULL': {'LENGTH': 1, 'OFFSET': 1, 'RESET_VALUE': 0x00},
        'RX_EMPTY': {'LENGTH': 1, 'OFFSET': 0, 'RESET_VALUE': 0x01},
    },
    'DYNPD': {
        'ADDRESS': 0x1C,
        'NUMBER_OF_DATA_BYTES': 1,
        'RESET_VALUE': 0x00,
        'DPL_P5': {'LENGTH': 1, 'OFFSET': 5, 'RESET_VALUE': 0x00},
        'DPL_P4': {'LENGTH': 1, 'OFFSET': 4, 'RESET_VALUE': 0x00},
        'DPL_P3': {'LENGTH': 1, 'OFFSET': 3, 'RESET_VALUE': 0x00},
        'DPL_P2': {'LENGTH': 1, 'OFFSET': 2, 'RESET_VALUE': 0x00},
        'DPL_P1': {'LENGTH': 1, 'OFFSET': 1, 'RESET_VALUE': 0x00},
        'DPL_P0': {'LENGTH': 1, 'OFFSET': 0, 'RESET_VALUE': 0x00},
    },
    'FEATURE': {
        'ADDRESS': 0x1D,
        'NUMBER_OF_DATA_BYTES': 1,
        'RESET_VALUE': 0x00,
        'EN_DPL': {'LENGTH': 1, 'OFFSET': 2, 'RESET_VALUE': 0x00},
        'EN_ACK_PAY': {'LENGTH': 1, 'OFFSET': 1, 'RESET_VALUE': 0x00},
        'EN_DYN_ACK': {'LENGTH': 1, 'OFFSET': 0, 'RESET_VALUE': 0x00},
    },
}

# Extracts the value from one or more bits in binary data.
def _extract_bit_value(data, number_of_bits, offset):
    return ((1 << number_of_bits) - 1) & (data >> offset)


def _format_byte_from_register(byte_to_format, reference_register):
    formatted_byte = {}
    for bit_mnemonic in REGISTER_MAP[reference_register]:
        # NOTE: Should probably think of a way to change this if statement.
        # I don't like it, as it isn't overly modular or expandable.
        if (
            bit_mnemonic != 'ADDRESS'
            and bit_mnemonic != 'NUMBER_OF_DATA_BYTES'
            and bit_mnemonic != 'RESET_VALUE'
        ):
            formatted_byte[bit_mnemonic] = _extract_bit_value(
                int.from_bytes(byte_to_format, 'big'),
                REGISTER_MAP[reference_register][bit_mnemonic]['LENGTH'],
                REGISTER_MAP[reference_register][bit_mnemonic]['OFFSET'],
            )
    return formatted_byte


def r_register(register_name):
    command_byte = (
        COMMANDS['R_REGISTER'] | REGISTER_MAP[register_name]['ADDRESS']
    ).to_bytes(1, 'big')
    command_length = len(command_byte)  # 1 command byte
    # [(tx) 1 command byte | (rx) 1 status byte] + (rx) the number of bytes at
    # the address.
    transfer_length = 1 + REGISTER_MAP[register_name]['NUMBER_OF_DATA_BYTES']
    # 1 status byte + the number of bytes at the address
    response_length = 1 + REGISTER_MAP[register_name]['NUMBER_OF_DATA_BYTES']
    with serial.Serial(PORT, BAUD, timeout=1) as ser:
        # Transmit the UART command length header
        ser.write(command_length.to_bytes(1, 'big'))
        # Transmit the SPI transfer length header
        ser.write(transfer_length.to_bytes(1, 'big'))
        # Transmit the command byte
        ser.write(command_byte)
        # Read and return the UART response
        uart_response = ser.read(response_length)
        uart_response_formatted = {}
        uart_response_formatted['RAW'] = uart_response
        uart_response_formatted['STATUS'] = {}
        uart_response_formatted['STATUS']['RAW'] = uart_response[:1]
        uart_response_formatted['STATUS'][
            'FORMATTED'
        ] = _format_byte_from_register(
            uart_response_formatted['STATUS']['RAW'], 'STATUS'
        )
        # Special case where if there is only one byte associated with the
        # register, then there are multiple bit mnemonics within the byte;
        # however, if there ard multiple bytes associated with the register,
        # then there are no bit mnemonics.
        if REGISTER_MAP[register_name]['NUMBER_OF_DATA_BYTES'] == 1:
            uart_response_formatted[register_name] = {}
            uart_response_formatted[register_name]['RAW'] = uart_response[:1]
            uart_response_formatted[register_name][
                'FORMATTED'
            ] = _format_byte_from_register(
                uart_response_formatted[register_name]['RAW'], register_name
            )
        else:
            uart_response_formatted[register_name] = uart_response[1:]
    return uart_response_formatted


def w_register(register_name, payload):
    # NOTE: I don't think that this is necessary.
    # # Ensure that the correct number of bytes are present in the payload.
    # if len(payload) != REGISTER_MAP[register_name]['NUMBER_OF_DATA_BYTES']:
    # raise ValueError("Incorrect payload length!")
    command_byte = (
        COMMANDS['W_REGISTER'] | REGISTER_MAP[register_name]['ADDRESS']
    ).to_bytes(1, 'big')
    # 1 command byte + number of payload bytes
    command_length = len(command_byte) + len(payload)
    # [(tx) 1 command byte | 1 status byte (rx)] + (tx) payload bytes
    transfer_length = 1 + len(payload)
    response_length = 1  # 1 status byte
    with serial.Serial(PORT, BAUD, timeout=1) as ser:
        # Transmit the UART command length header
        ser.write(command_length.to_bytes(1, 'big'))
        # Transmit the SPI transfer length header
        ser.write(transfer_length.to_bytes(1, 'big'))
        # Transmit the command byte
        ser.write(command_byte)
        # Transmit the payload byte(s)
        ser.write(payload)
        # Read and return the UART response
        uart_response = ser.read(response_length)
        uart_response_formatted = {}
        uart_response_formatted['RAW'] = uart_response
        uart_response_formatted['STATUS'] = {}
        uart_response_formatted['STATUS']['RAW'] = uart_response[:1]
        uart_response_formatted['STATUS'][
            'FORMATTED'
        ] = _format_byte_from_register(
            uart_response_formatted['STATUS']['RAW'], 'STATUS'
        )
    return uart_response_formatted


def r_rx_payload():
    command_byte = COMMANDS['R_RX_PAYLOAD'].to_bytes(1, 'big')
    # The command byte + 32 RX_PAYLOAD bytes
    command_length = len(command_byte) + 32
    # [(tx) 1 command byte | 1 status byte (rx)] + 32 RX_PAYLOAD bytes
    transfer_length = 33
    response_length = 33  # 1 status byte + 32 RX_PAYLOAD bytes
    with serial.Serial(PORT, BAUD, timeout=1) as ser:
        # Transmit the UART command length header
        ser.write(command_length.to_bytes(1, 'big'))
        # Transmit the SPI transfer length header
        ser.write(transfer_length.to_bytes(1, 'big'))
        # Transmit the Command byte
        ser.write(command_byte)
        # Read and return the UART response
        uart_response = ser.read(response_length)
        uart_response_formatted = {}
        uart_response_formatted['RAW'] = uart_response
        uart_response_formatted['STATUS'] = {}
        uart_response_formatted['STATUS']['RAW'] = uart_response[:1]
        uart_response_formatted['STATUS'][
            'FORMATTED'
        ] = _format_byte_from_register(
            uart_response_formatted['STATUS']['RAW'], 'STATUS'
        )
        uart_response_formatted['RX_PAYLOAD'] = uart_response[1:].strip(b'\x00')
    return uart_response_formatted


def w_tx_payload(payload):
    if type(payload) != bytes:
        raise TypeError("Payload must be of type <bytes>.")
    # NOTE: I think this is uneeded
    # if len(payload) != 32:
    # raise ValueError("Incorrect payload length! Payload length must be 32.")
    command_byte = COMMANDS['W_TX_PAYLOAD'].to_bytes(1, 'big')
    # 1 command byte + the number of payload bytes
    command_length = len(command_byte) + len(payload)
    # [(tx) 1 command byte | 1 status byte (rx)] + TX_PAYLOAD bytes
    transfer_length = 1 + len(payload)
    response_length = 1  # 1 Status byte
    with serial.Serial(PORT, BAUD, timeout=1) as ser:
        # Transmit the UART Command length header
        ser.write(command_length.to_bytes(1, 'big'))
        # Transmit the SPI transfer length header
        ser.write(transfer_length.to_bytes(1, 'big'))
        # Transmit the command byte
        ser.write(command_byte)
        # Transmit the payload
        ser.write(payload)
        # Read and return the UART response
        uart_response = ser.read(response_length)
        uart_response_formatted = {}
        uart_response_formatted['RAW'] = uart_response
        uart_response_formatted['STATUS'] = {}
        uart_response_formatted['STATUS']['RAW'] = uart_response[:1]
        uart_response_formatted['STATUS'][
            'FORMATTED'
        ] = _format_byte_from_register(
            uart_response_formatted['STATUS']['RAW'], 'STATUS'
        )
    return uart_response_formatted


def flush_tx():
    command_byte = COMMANDS['FLUSH_TX'].to_bytes(1, 'big')
    command_length = len(command_byte)  # 1 command byte
    transfer_length = 1  # [(tx) 1 command byte | (rx) 1 status byte]
    response_length = 1  # 1 status byte
    with serial.Serial(PORT, BAUD, timeout=1) as ser:
        # Transmit the UART command length header
        ser.write(command_length.to_bytes(1, 'big'))
        # Transmit the SPI transfer length header
        ser.write(transfer_length.to_bytes(1, 'big'))
        # Transmit the command byte
        ser.write(command_byte)
        # Read and return the UART response
        uart_response = ser.read(response_length)
        uart_response_formatted = {}
        uart_response_formatted['RAW'] = uart_response
        uart_response_formatted['STATUS'] = {}
        uart_response_formatted['STATUS']['RAW'] = uart_response[:1]
        uart_response_formatted['STATUS'][
            'FORMATTED'
        ] = _format_byte_from_register(
            uart_response_formatted['STATUS']['RAW'], 'STATUS'
        )
    return uart_response_formatted


def flush_rx():
    command_byte = COMMANDS['FLUSH_RX'].to_bytes(1, 'big')
    command_length = len(command_byte)  # 1 command byte
    transfer_length = 1  # [(tx) 1 command byte | (rx) 1 status byte]
    response_length = 1  # 1 status byte
    with serial.Serial(PORT, BAUD, timeout=1) as ser:
        # Transmit the UART command length header
        ser.write(command_length.to_bytes(1, 'big'))
        # Transmit the SPI transfer length header
        ser.write(transfer_length.to_bytes(1, 'big'))
        # Transmit the command byte
        ser.write(command_byte)
        # Read and return the UART response
        uart_response = ser.read(response_length)
        uart_response_formatted = {}
        uart_response_formatted['RAW'] = uart_response
        uart_response_formatted['STATUS'] = {}
        uart_response_formatted['STATUS']['RAW'] = uart_response[:1]
        uart_response_formatted['STATUS'][
            'FORMATTED'
        ] = _format_byte_from_register(
            uart_response_formatted['STATUS']['RAW'], 'STATUS'
        )
    return uart_response_formatted


def reuse_tx_pl():
    command_byte = COMMANDS['REUSE_TX_PL'].to_bytes(1, 'big')
    command_length = len(command_byte)  # 1 command byte
    transfer_length = 1  # [(tx) 1 command byte | (rx) 1 status byte]
    response_length = 1  # 1 status byte
    with serial.Serial(PORT, BAUD, timeout=1) as ser:
        # Transmit the UART command length header
        ser.write(command_length.to_bytes(1, 'big'))
        # Transmit the SPI transfer length header
        ser.write(transfer_length.to_bytes(1, 'big'))
        # Transmit the command byte
        ser.write(command_byte)
        # Read and return the UART response
        uart_response = ser.read(response_length)
        uart_response_formatted = {}
        uart_response_formatted['RAW'] = uart_response
        uart_response_formatted['STATUS'] = {}
        uart_response_formatted['STATUS']['RAW'] = uart_response[:1]
        uart_response_formatted['STATUS'][
            'FORMATTED'
        ] = _format_byte_from_register(
            uart_response_formatted['STATUS']['RAW'], 'STATUS'
        )
    return uart_response_formatted


def r_rx_pl_wid():
    command_byte = COMMANDS['R_RX_PL_WID'].to_bytes(1, 'big')
    command_length = len(command_byte)  # 1 command byte
    transfer_length = 2  # [(tx) 1 command byte | (rx) 1 status byte]
    response_length = 2  # 1 status byte + 1 RX_PL_WID byte
    with serial.Serial(PORT, BAUD, timeout=1) as ser:
        # Transmit the UART command length header
        ser.write(command_length.to_bytes(1, 'big'))
        # Transmit the SPI transfer length header
        ser.write(transfer_length.to_bytes(1, 'big'))
        # Transmit the command byte
        ser.write(command_byte)
        # Read and return the UART response
        uart_response = ser.read(response_length)
        uart_response_formatted = {}
        uart_response_formatted['RAW'] = uart_response
        uart_response_formatted['STATUS'] = {}
        uart_response_formatted['STATUS']['RAW'] = uart_response[:1]
        uart_response_formatted['STATUS'][
            'FORMATTED'
        ] = _format_byte_from_register(
            uart_response_formatted['STATUS']['RAW'], 'STATUS'
        )
        uart_response_formatted['RX_PL_WID'] = uart_response[1:]
    return uart_response_formatted


def w_ack_payload(payload, pipe):
    command_byte = (COMMANDS['W_ACK_PAYLOAD'] | pipe).to_bytes(1, 'big')
    # 1 command byte + payload bytes
    command_length = len(command_byte) + len(payload)
    # [(tx) 1 command byte | (rx) 1 status byte] + payload bytes
    transfer_length = 1 + len(payload)
    response_length = 1  # 1 status byte
    with serial.Serial(PORT, BAUD, timeout=1) as ser:
        # Transmit the UART command length header
        ser.write(command_length.to_bytes(1, 'big'))
        # Transmit the SPI transfer length header
        ser.write(transfer_length.to_bytes(1, 'big'))
        # Transmit the command byte
        # The pipe is or'd with the command byte. See [1] Section 8.3.1 Table 19
        ser.write(command_byte)
        # Transmit the payload
        ser.write(payload)
        # Read and return the UART response
        uart_response = ser.read(response_length)
        uart_response_formatted = {}
        uart_response_formatted['RAW'] = uart_response
        uart_response_formatted['STATUS'] = {}
        uart_response_formatted['STATUS']['RAW'] = uart_response[:1]
        uart_response_formatted['STATUS'][
            'FORMATTED'
        ] = _format_byte_from_register(
            uart_response_formatted['STATUS']['RAW'], 'STATUS'
        )
    return uart_response_formatted


def w_tx_payload_noack(payload):
    command_byte = COMMANDS['W_TX_PAYLOAD_NOACK'].to_bytes(1, 'big')
    # 1 command byte + payload bytes
    command_length = len(command_byte) + len(payload)
    # [(tx) 1 command byte | (rx) 1 status byte] + (tx) payload bytes
    transfer_length = 1 + len(payload)
    response_length = 1  # 1 status byte
    with serial.Serial(PORT, BAUD, timeout=1) as ser:
        # Transmit the UART command length header
        ser.write(command_length.to_bytes(1, 'big'))
        # Transmit the SPI transfer length header
        ser.write(transfer_length.to_bytes(1, 'big'))
        # Transmit the command byte
        ser.write(command_byte)
        # Transmit the payload
        ser.write(payload)
        # Read and return the UART response
        uart_response = ser.read(response_length)
        uart_response_formatted = {}
        uart_response_formatted['RAW'] = uart_response
        uart_response_formatted['STATUS'] = {}
        uart_response_formatted['STATUS']['RAW'] = uart_response[:1]
        uart_response_formatted['STATUS'][
            'FORMATTED'
        ] = _format_byte_from_register(
            uart_response_formatted['STATUS']['RAW'], 'STATUS'
        )
    return uart_response_formatted


def nop():
    command_byte = COMMANDS['NOP'].to_bytes(1, 'big')
    command_length = len(command_byte)  # 1 command byte
    transfer_length = 1  # [(tx) 1 command byte | (rx) 1 status byte]
    response_length = 1  # 1 status byte
    with serial.Serial(PORT, BAUD, timeout=1) as ser:
        # Transmit the UART command length header
        ser.write(command_length.to_bytes(1, 'big'))
        # Transmit the SPI transfer length header
        ser.write(transfer_length.to_bytes(1, 'big'))
        # Transmit the command byte
        ser.write(command_byte)
        # Read and return the UART response
        uart_response = ser.read(response_length)
        uart_response_formatted = {}
        uart_response_formatted['RAW'] = uart_response
        uart_response_formatted['STATUS'] = {}
        uart_response_formatted['STATUS']['RAW'] = uart_response[:1]
        uart_response_formatted['STATUS'][
            'FORMATTED'
        ] = _format_byte_from_register(
            uart_response_formatted['STATUS']['RAW'], 'STATUS'
        )
    return uart_response_formatted


# NOTE: Should I format the returned status key in the returned dictionary to
# display its bit mnemonics?
# TODO: Add a check to make sure that the data given to the functions are of
# type <bytes>
# NOTE: Should all of these functions be part of a class?
# NOTE: Maybe remove the raw data values from the dictionaries. I dont see much
# use or their existence.
# TODO: Add a human readable alias to the register names
# TODO: Add a reset value to each register.
# NOTE: Should I add a NULL bit to represent the bits that have no use in the
# register map? e.g. the obsolete, reserved, and read-only bits. I can't think
# of a useful reason for its addition at this moment.
