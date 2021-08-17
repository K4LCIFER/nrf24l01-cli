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
# This file was adapted from
# [this](https://github.com/maniacbug/RF24/blob/master/nRF24L01.h) header file.
# 2021-08-11
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


# Command names and words. See [1]Section 8.3.1 Table 19.
# NOTE: I am not sure if it is correct to vertically align these in this
# scenario. According to PEP8, it seems to be incorrect. Further research is
# required.
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
# See [1]Section 9.1 Table 27.
REGISTER_MAP = {
    'CONFIG': {
        'ADDRESS': 0x00,
        'NUMBER_OF_DATA_BYTES': 1,
        'MASK_RX_DR': {'LENGTH': 1, 'OFFSET': 6},
        'MASK_TX_DS': {'LENGTH': 1, 'OFFSET': 5},
        'MASK_MAX_RT': {'LENGTH': 1, 'OFFSET': 4},
        'EN_CRC': {'LENGTH': 1, 'OFFSET': 3},
        'CRCO': {'LENGTH': 1, 'OFFSET': 2},
        'PWR_UP': {'LENGTH': 1, 'OFFSET': 1},
        'PRIM_RX': {'LENGTH': 1, 'OFFSET': 0},
    },
    'EN_AA': {
        'ADDRESS': 0x01,
        'NUMBER_OF_DATA_BYTES': 1,
        'ENAA_P5': {'LENGTH': 1, 'OFFSET': 5},
        'ENAA_P4': {'LENGTH': 1, 'OFFSET': 4},
        'ENAA_P3': {'LENGTH': 1, 'OFFSET': 3},
        'ENAA_P2': {'LENGTH': 1, 'OFFSET': 2},
        'ENAA_P1': {'LENGTH': 1, 'OFFSET': 1},
        'ENAA_P0': {'LENGTH': 1, 'OFFSET': 0},
    },
    'EN_RXADDR': {
        'ADDRESS': 0x02,
        'NUMBER_OF_DATA_BYTES': 1,
        'ERX_P5': {'LENGTH': 1, 'OFFSET': 5},
        'ERX_P4': {'LENGTH': 1, 'OFFSET': 4},
        'ERX_P3': {'LENGTH': 1, 'OFFSET': 3},
        'ERX_P2': {'LENGTH': 1, 'OFFSET': 2},
        'ERX_P1': {'LENGTH': 1, 'OFFSET': 1},
        'ERX_P0': {'LENGTH': 1, 'OFFSET': 0},
    },
    'SETUP_AW': {
        'ADDRESS': 0x03,
        'NUMBER_OF_DATA_BYTES': 1,
        'AW': {'LENGTH': 2, 'OFFSET': 0},
    },
    'SETUP_RETR': {
        'ADDRESS': 0x04,
        'NUMBER_OF_DATA_BYTES': 1,
        'ARD': {'LENGTH': 4, 'OFFSET': 4},
        'ARC': {'LENGTH': 4, 'OFFSET': 0},
    },
    'RF_CH': {
        'ADDRESS': 0x05,
        'NUMBER_OF_DATA_BYTES': 1,
        'RF_CH': {'LENGTH': 7, 'OFFSET': 0},
    },
    'RF_SETUP': {
        'ADDRESS': 0x06,
        'NUMBER_OF_DATA_BYTES': 1,
        'CONT_WAVE': {'LENGTH': 1, 'OFFSET': 7},
        'RF_DR_LOW': {'LENGTH': 1, 'OFFSET': 5},
        'PLL_LOCK': {'LENGTH': 1, 'OFFSET': 4},
        'RF_DR_HIGH': {'LENGTH': 1, 'OFFSET': 3},
        'RF_PWR': {'LENGTH': 2, 'OFFSET': 1},
    },
    'STATUS': {
        'ADDRESS': 0x07,
        'NUMBER_OF_DATA_BYTES': 1,
        'RX_DR': {'LENGTH': 1, 'OFFSET': 6},
        'TX_DS': {'LENGTH': 1, 'OFFSET': 5},
        'MAX_RT': {'LENGTH': 1, 'OFFSET': 4},
        'RX_P_NO': {'LENGTH': 3, 'OFFSET': 1},
        'TX_FULL': {'LENGTH': 1, 'OFFSET': 0},
    },
    'OBSERVE_TX': {
        'NUMBER_OF_DATA_BYTES': 1,
        'ADDRESS': 0x08,
        'PLOS_CNT': {'LENGTH': 4, 'OFFSET': 4},
        'ARC_CNT': {'LENGTH': 4, 'OFFSET': 0},
    },
    'RPD': {
        'ADDRESS': 0x09,
        'NUMBER_OF_DATA_BYTES': 1,
        'RPD': {'LENGTH': 1, 'OFFSET': 0},
    },  # RPD or CD?
    'RX_ADDR_P0': {
        'ADDRESS': 0x0A,
        'NUMBER_OF_DATA_BYTES': 5,
    },
    'RX_ADDR_P1': {
        'ADDRESS': 0x0B,
        'NUMBER_OF_DATA_BYTES': 5,
    },
    'RX_ADDR_P2': {
        'ADDRESS': 0x0C,
        'NUMBER_OF_DATA_BYTES': 1,
    },
    'RX_ADDR_P3': {
        'ADDRESS': 0x0D,
        'NUMBER_OF_DATA_BYTES': 1,
    },
    'RX_ADDR_P4': {
        'ADDRESS': 0x0E,
        'NUMBER_OF_DATA_BYTES': 1,
    },
    'RX_ADDR_P5': {
        'ADDRESS': 0x0F,
        'NUMBER_OF_DATA_BYTES': 1,
    },
    'TX_ADDR': {'ADDRESS': 0x10, 'NUMBER_OF_DATA_BYTES': 5},
    'RX_PW_P0': {
        'ADDRESS': 0x11,
        'NUMBER_OF_DATA_BYTES': 1,
        'RX_PW_P0': {'LENGTH': 6, 'OFFSET': 0},
    },
    'RX_PW_P1': {
        'ADDRESS': 0x12,
        'NUMBER_OF_DATA_BYTES': 1,
        'RX_PW_P1': {'LENGTH': 6, 'OFFSET': 0},
    },
    'RX_PW_P2': {
        'ADDRESS': 0x13,
        'NUMBER_OF_DATA_BYTES': 1,
        'RX_PW_P2': {'LENGTH': 6, 'OFFSET': 0},
    },
    'RX_PW_P3': {
        'ADDRESS': 0x14,
        'NUMBER_OF_DATA_BYTES': 1,
        'RX_PW_P3': {'LENGTH': 6, 'OFFSET': 0},
    },
    'RX_PW_P4': {
        'ADDRESS': 0x15,
        'NUMBER_OF_DATA_BYTES': 1,
        'RX_PW_P4': {'LENGTH': 6, 'OFFSET': 0},
    },
    'RX_PW_P5': {
        'ADDRESS': 0x16,
        'NUMBER_OF_DATA_BYTES': 1,
        'RX_PW_P5': {'LENGTH': 6, 'OFFSET': 0},
    },
    'FIFO_STATUS': {
        'ADDRESS': 0x17,
        'NUMBER_OF_DATA_BYTES': 1,
        'TX_REUSE': {'LENGTH': 1, 'OFFSET': 6},
        'TX_FULL': {'LENGTH': 1, 'OFFSET': 5},
        'TX_EMPTY': {'LENGTH': 1, 'OFFSET': 4},
        'RX_FULL': {'LENGTH': 1, 'OFFSET': 1},
        'RX_EMPTY': {'LENGTH': 1, 'OFFSET': 0},
    },
    'DYNPD': {
        'ADDRESS': 0x1C,
        'NUMBER_OF_DATA_BYTES': 1,
        'DPL_P5': {'LENGTH': 1, 'OFFSET': 5},
        'DPL_P4': {'LENGTH': 1, 'OFFSET': 4},
        'DPL_P3': {'LENGTH': 1, 'OFFSET': 3},
        'DPL_P2': {'LENGTH': 1, 'OFFSET': 2},
        'DPL_P1': {'LENGTH': 1, 'OFFSET': 1},
        'DPL_P0': {'LENGTH': 1, 'OFFSET': 0},
    },
    'FEATURE': {
        'ADDRESS': 0x1D,
        'NUMBER_OF_DATA_BYTES': 1,
        'EN_DPL': {'LENGTH': 1, 'OFFSET': 2},
        'EN_ACK_PAY': {'LENGTH': 1, 'OFFSET': 1},
        'EN_DYN_ACK': {'LENGTH': 1, 'OFFSET': 0},
    },
}

# Extracts the value from one or more bits in binary data.
def _extract_bit_value(data, number_of_bits, offset):
    return ((1 << number_of_bits) - 1) & (data >> offset)


# Retrieve the contents of the status register of the nRF24L01, and return it as
# a dictionary.
def get_status():  # WARNING MUST REDO THIS. remove perhaps?
    # TODO: Need to add the functionality to retrieve the FIFO_STATUS, as well.
    with serial.Serial(PORT, BAUD, timeout=1) as ser:
        ser.write(bytes([COMMANDS['NOP']]))  # Send an empty packet
        # Read the status register. (convert  bytes data type to int)
        status = int.from_bytes(ser.read(1), byteorder='big', signed=False)

    # Separate each portion of the received status register data into its
    # separate bit mnemonic sections.
    status_register = {}
    status_register['RAW'] = status  # Raw received data
    status_register['RX_DR'] = _extract_bit_value(
        status,
        REGISTER_MAP['STATUS']['RX_DR']['LENGTH'],
        REGISTER_MAP['STATUS']['RX_DR']['OFFSET'],
    )
    status_register['TX_DS'] = _extract_bit_value(
        status,
        REGISTER_MAP['STATUS']['TX_DS']['LENGTH'],
        REGISTER_MAP['STATUS']['TX_DS']['OFFSET'],
    )
    status_register['MAX_RT'] = _extract_bit_value(
        status,
        REGISTER_MAP['STATUS']['MAX_RT']['LENGTH'],
        REGISTER_MAP['STATUS']['MAX_RT']['OFFSET'],
    )
    status_register['RX_P_NO'] = _extract_bit_value(
        status,
        REGISTER_MAP['STATUS']['RX_P_NO']['LENGTH'],
        REGISTER_MAP['STATUS']['RX_P_NO']['OFFSET'],
    )
    status_register['TX_FULL'] = _extract_bit_value(
        status,
        REGISTER_MAP['STATUS']['TX_FULL']['LENGTH'],
        REGISTER_MAP['STATUS']['TX_FULL']['OFFSET'],
    )

    return status_register


def r_register(register_name):
    with serial.Serial(PORT, BAUD, timeout=1) as ser:
        # Send two header bytes:
        # This first byte is always 0x01 for the read command as the command
        # word and address are only 1 byte.
        ser.write(b'\x01')  # Length of the transmitted command.
        # TODO: Add some logic to check if the requested override is longer than
        # the maximum data bytes at the address. (Also less than 32).
        # Specify the length of the requested data associated with the
        # command word + 1 for the status register.
        ser.write(
            (REGISTER_MAP[register_name]['NUMBER_OF_DATA_BYTES'] + 1).to_bytes(
                1, 'big'
            )
        )
        # Transmit the command byte.
        ser.write(
            (
                COMMANDS['R_REGISTER'] | REGISTER_MAP[register_name]['ADDRESS']
            ).to_bytes(1, 'big')
        )
        # Read the UART response.
        uart_response_formatted = {}
        # Read the data returned over UART.
        uart_response = int.from_bytes(
            ser.read(
                REGISTER_MAP[register_name]['NUMBER_OF_DATA_BYTES'] + 1,
            ),
            'big',
        )
        # Save an entry for the raw returned data.
        uart_response_formatted['RAW'] = uart_response
        # TODO: Add the returned status register to the returned dictionary.
        # There is an issue where with the STATUS register is included in the
        # final data, so it must be removed.
        # The following is a special case of the registers in the nRF24L01. If
        # a register has only one byte associated with it, then it will always
        # have bit mnemonics describing the bits that are at the specified
        # register adderss; however, if the register containts more than one
        # byte, then it does not have any bit mnemonics describing the bit
        # positions of the register, and instead has whole chunks of data.
        if REGISTER_MAP[register_name]['NUMBER_OF_DATA_BYTES'] == 1:
            # First collect the bit mnemonic(s) into a dictionary and assign
            # each of them their respecive returned value.
            uart_response_bit_mnemonics = {}
            for bit_mnemonic in REGISTER_MAP[register_name]:
                # Ignore the ADDRESS and NUMBER_OF_DATA_BYTES keys.
                if (
                    bit_mnemonic != 'ADDRESS'
                    and bit_mnemonic != 'NUMBER_OF_DATA_BYTES'
                ):
                    # Extract the respective bit menmonics bit value from the
                    # raw received data and write it to the dictionary.
                    uart_response_bit_mnemonics[
                        bit_mnemonic
                    ] = _extract_bit_value(
                        uart_response,
                        REGISTER_MAP[register_name][bit_mnemonic]['LENGTH'],
                        REGISTER_MAP[register_name][bit_mnemonic]['OFFSET'],
                    )
                    # Add the bit_mnemonics to the main UART dictionary.
                    uart_response_formatted[
                        register_name
                    ] = uart_response_bit_mnemonics
        elif REGISTER_MAP[register_name]['NUMBER_OF_DATA_BYTES'] > 1:
            # Dump the total received data into the dictionary.
            uart_response_formatted[register_name] = uart_response
        return uart_response_formatted


def w_register(register_name, payload):
    # NOTE: Might change this stuff.
    if type(payload) == list:
        if len(payload) != REGISTER_MAP[register_name]['NUMBER_OF_DATA_BYTES']:
            raise ValueError("Incorrect payload length!")
    if type(payload) == int:
        if payload > 255:
            raise ValueError("")
    with serial.Serial(PORT, BAUD, timeout=1) as ser:
        # Send header bytes:
        # Transmit data length - Command Byte + the number of Data Bytes.
        ser.write(
            (REGISTER_MAP[register_name]['NUMBER_OF_DATA_BYTES'] + 1).to_bytes(
                1, 'big'
            )
        )
        # NOTE: I don't like "Returned data length". It isn't overly descriptive
        # of what it is/does. It should be more like number of transfer bytes,
        # in reference to SPI, as it is for the spi; however it is also for the
        # data returned to the UART sometimes. Some more thought is needed for
        # this.
        # Returned data length - Status Register + the number of Data Bytes.
        ser.write(
            (REGISTER_MAP[register_name]['NUMBER_OF_DATA_BYTES'] + 1).to_bytes(
                1, 'big'
            )
        )
        # Send command byte:
        ser.write(
            (
                COMMANDS['W_REGISTER'] | REGISTER_MAP[register_name]['ADDRESS']
            ).to_bytes(1, 'big')
        )
        # Send the data bytes:
        # TODO: Allow this statement to handle multiple types.
        if isinstance(payload, list):
            for byte in payload:
                ser.write(byte.to_bytes(1, 'big'))
        elif isinstance(payload, int):
            ser.write(payload.to_bytes(1, 'big'))
        # Read and return the status register.
        # TODO: Need to add the status register to the returned data dictionary.
        uart_response = int.from_bytes(ser.read(1), 'big')
        uart_response_formatted = {}
        uart_response_formatted['RAW'] = uart_response
        return uart_response_formatted


def r_rx_payload():
    payload_length = 33
    with serial.Serial(PORT, BAUD, timeout=1) as ser:
        # Transmit UART headers:
        # Transmit UART Command length: One command word
        ser.write((1).to_bytes(1, 'big'))
        # Transmit SPI transfer length: 1 command byte + 32 data bytes
        # See [1] Section 8.3.1 Table 19
        ser.write((payload_length).to_bytes(1, 'big'))
        # Transmit the Command byte
        ser.write(COMMANDS['R_RX_PAYLOAD'].to_bytes(1, 'big'))
        # Read and return the Rx Payload, and the Status Register data.
        # uart_response = int.from_bytes(ser.read(1), 'big')
        uart_response = ser.read(payload_length)
        uart_response_formatted = {}
        # NOTE: Should data be in bytes or int? bytes is probably more readable
        # and useable than int for the raw data.
        uart_response_formatted['RAW'] = uart_response
        uart_response_formatted['STATUS'] = uart_response[0].to_bytes(1, 'big')
        uart_response_formatted['PAYLOAD'] = uart_response[1:]
    return uart_response_formatted


def w_tx_payload(payload):
    return


def flush_tx():
    return


def fulsh_rx():
    return


def reuse_tx_pl():
    return


def r_rx_pl_wid():
    return


def w_ack_payload(payload):
    return


def w_tx_payload_no_ack(payload):
    return


def nop():
    return
