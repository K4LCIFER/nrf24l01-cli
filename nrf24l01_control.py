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
# Documentation:
# 1. [nRF24L01 Datasheet](<project_directory>/nRF24L01-datasheet.pdf)
################################################################################
import serial


# Command names and words. See [1] Section 8.3.1 Table 19.
# NOTE: Should this go in the class?
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
# NOTE: Should this go in the class?
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


class nRF24L01:
    def __init__(self, port: str):
        self.port = port
        self.BAUD = 9600

    def r_register(self, register_name: str) -> bytes:
        """Read the command and status registers, and return their contents.

        Keyword arguments:
            register_name -- The register that the requested data is to be read
            from.
        Documentation:
            See [1] Table 19 for R_REGISTER.
            See [1] Section 9.1 (Table 27) for the register names, and their
            contents.
        """
        if register_name not in REGISTER_MAP:
            raise KeyError("The specified register does not exist.")
        # Transmit the UART reponse length header
        command_byte = (
            COMMANDS['R_REGISTER'] | REGISTER_MAP[register_name]['ADDRESS']
        ).to_bytes(1, 'big')
        command_length = len(command_byte)  # 1 command byte
        # [(tx) 1 command byte | (rx) 1 status byte] + (rx) the number of bytes
        # at the address.
        transfer_length = (
            1 + REGISTER_MAP[register_name]['NUMBER_OF_DATA_BYTES']
        )
        # 1 status byte + the number of bytes at the address
        response_length = (
            1 + REGISTER_MAP[register_name]['NUMBER_OF_DATA_BYTES']
        )
        with serial.Serial(self.port, self.BAUD, timeout=1) as ser:
            # Transmit the UART command length header
            ser.write(command_length.to_bytes(1, 'big'))
            # Transmit the SPI transfer length header
            ser.write(transfer_length.to_bytes(1, 'big'))
            # Transmit the UART reponse length header
            ser.write(response_length.to_bytes(1, 'big'))
            # Transmit the command byte
            ser.write(command_byte)
            # Read the data returned over UART
            uart_response = ser.read(response_length)[1:]
            # Return, from the function, all data except the status
        return uart_response

    def w_register(self, register_name: str, payload: bytes) -> None:
        """Write data to a specified register

        Keyword arguments:
            register_name -- The register that data is to be written to. The
            register name is of type string.
            payload -- The data to be written to the register specified in
            register_name. The payload data is of type bytes, and can be either
            1 byte, or 5 bytes in length.
        Documentation:
            See [1] Table 19 for W_REGISTER command.
            See [1] Section 9.1 (Table 27) for the register names, and their
            contents.
        """
        if type(payload) != bytes:
            raise TypeError("Payload must be of type <bytes>.")
        if (
            len(payload) > REGISTER_MAP[register_name]['NUMBER_OF_DATA_BYTES']
            or len(payload) < 0
        ):
            raise ValueError("Invalid payload length.")
        if register_name not in REGISTER_MAP:
            raise KeyError("The specified register does not exist.")
        # Transmit the UART reponse length header
        command_byte = (
            COMMANDS['W_REGISTER'] | REGISTER_MAP[register_name]['ADDRESS']
        ).to_bytes(1, 'big')
        # 1 command byte + number of payload bytes
        command_length = len(command_byte) + len(payload)
        # [(tx) 1 command byte | 1 status byte (rx)] + (tx) payload bytes
        transfer_length = 1 + len(payload)
        response_length = 0  # 1 status byte
        with serial.Serial(self.port, self.BAUD, timeout=1) as ser:
            # Transmit the UART command length header
            ser.write(command_length.to_bytes(1, 'big'))
            # Transmit the SPI transfer length header
            ser.write(transfer_length.to_bytes(1, 'big'))
            # Transmit the UART reponse length header
            ser.write(response_length.to_bytes(1, 'big'))
            # Transmit the command byte
            ser.write(command_byte)
            # Transmit the payload byte(s)
            ser.write(payload)
            # Read any returned data. NOTE: Probably not needed as it returns 0
            ser.read(response_length)

    def r_rx_payload(self, number_of_bytes: int) -> bytes:
        """Read, and return the received data from the RX_PLD regiser.

        Keyword arguments:
            number_of_bytes -- The number of bytes that are to be read and
            returned
            from the received data register.
        Documentation:
            See [1] Table 19 for the R_RX_PAYLOAD command.
        """
        if number_of_bytes < 0 or number_of_bytes > 32:
            raise ValueError(
                "The specified number of bytes to be read must be in"
                " the range [0,32]"
            )
        # Transmit the UART reponse length header
        command_byte = COMMANDS['R_RX_PAYLOAD'].to_bytes(1, 'big')
        # The command byte
        command_length = len(command_byte)
        # [(tx) 1 command byte | 1 status byte (rx)] + RX_PAYLOAD
        transfer_length = 1 + number_of_bytes
        response_length = 1 + number_of_bytes  # 1 status byte + RX_PAYLOAD
        with serial.Serial(self.port, self.BAUD, timeout=1) as ser:
            # Transmit the UART command length header
            ser.write(command_length.to_bytes(1, 'big'))
            # Transmit the SPI transfer length header
            ser.write(transfer_length.to_bytes(1, 'big'))
            # Transmit the UART reponse length header
            ser.write(response_length.to_bytes(1, 'big'))
            # Transmit the Command byte
            ser.write(command_byte)
            # Read and return the read receive payload (Ignore the STATUS byte).
            uart_response = ser.read(response_length)[1:]
        return uart_response

    def w_tx_payload(self, payload: bytes) -> None:
        """Write the data to be transmitted to the TX_PLD register

        Keyword arguments:
            payload -- The data that is to be transmitted. The payload data is
            of type bytes, and it can be up to 32 bytes in length.
        Documentation:
            See [1] Table 19 for the W_TX_PAYLOAD command.
        """
        if type(payload) != bytes:
            raise TypeError("Payload must be of type <bytes>.")
        if len(payload) > 32:
            raise ValueError("Payload must be 0-32 bytes in length.")
        # Transmit the UART reponse length header
        command_byte = COMMANDS['W_TX_PAYLOAD'].to_bytes(1, 'big')
        # 1 command byte + the number of payload bytes
        command_length = len(command_byte) + len(payload)
        # [(tx) 1 command byte | 1 status byte (rx)] + TX_PAYLOAD bytes
        transfer_length = 1 + len(payload)
        response_length = 0  # 1 Status byte
        with serial.Serial(self.port, self.BAUD, timeout=1) as ser:
            # Transmit the UART Command length header
            ser.write(command_length.to_bytes(1, 'big'))
            # Transmit the SPI transfer length header
            ser.write(transfer_length.to_bytes(1, 'big'))
            # Transmit the UART reponse length header
            ser.write(response_length.to_bytes(1, 'big'))
            # Transmit the command byte
            ser.write(command_byte)
            # Transmit the payload
            ser.write(payload)
            # Read any returned data. NOTE: Probably not needed as it returns 0
            ser.read(response_length)

    def flush_tx(self) -> None:
        """Flush any exising data out of the TX_PLD FIFOs.

        Documentation:
            See [1] Table 19 for the FLUSH_TX command.
        """
        # Setup the uart data
        command_byte = COMMANDS['FLUSH_TX'].to_bytes(1, 'big')
        command_length = len(command_byte)  # 1 command byte
        transfer_length = 1  # [(tx) 1 command byte | (rx) 1 status byte]
        response_length = 0  # None (Ignore the STATUS byte).
        with serial.Serial(self.port, self.BAUD, timeout=1) as ser:
            # Transmit the UART command length header
            ser.write(command_length.to_bytes(1, 'big'))
            # Transmit the SPI transfer length header
            ser.write(transfer_length.to_bytes(1, 'big'))
            # Transmit the UART reponse length header
            ser.write(response_length.to_bytes(1, 'big'))
            # Transmit the command byte
            ser.write(command_byte)
            # Read any returned data. NOTE: Probably not needed as it returns 0
            ser.read(response_length)

    def flush_rx(self) -> None:
        """Flush any exising data out of the RX_PLD FIFOs.

        Documentation:
            See [1] Table 19 for the FLUSH_RX command.
        """
        # Setup the uart data
        command_byte = COMMANDS['FLUSH_RX'].to_bytes(1, 'big')
        command_length = len(command_byte)  # 1 command byte
        transfer_length = 1  # [(tx) 1 command byte | (rx) 1 status byte]
        response_length = 0  # None (Ignore the STATUS byet).
        with serial.Serial(self.port, self.BAUD, timeout=1) as ser:
            # Transmit the UART command length header
            ser.write(command_length.to_bytes(1, 'big'))
            # Transmit the SPI transfer length header
            ser.write(transfer_length.to_bytes(1, 'big'))
            # Transmit the UART reponse length header
            ser.write(response_length.to_bytes(1, 'big'))
            # Transmit the command byte
            ser.write(command_byte)
            # Read any returned data. NOTE: Probably not needed as it returns 0
            ser.read(response_length)

    def reuse_tx_pl(self) -> None:
        """Reuse the last transmitted payload.

        Documentation:
            See [1] Table 19 for the REUSE_TX_PL command.
        """
        # Setup the uart data
        command_byte = COMMANDS['REUSE_TX_PL'].to_bytes(1, 'big')
        command_length = len(command_byte)  # 1 command byte
        transfer_length = 1  # [(tx) 1 command byte | (rx) 1 status byte]
        response_length = 0  # None (Ignore the STATUS byte).
        with serial.Serial(self.port, self.BAUD, timeout=1) as ser:
            # Transmit the UART command length header
            ser.write(command_length.to_bytes(1, 'big'))
            # Transmit the SPI transfer length header
            ser.write(transfer_length.to_bytes(1, 'big'))
            # Transmit the UART reponse length header
            ser.write(response_length.to_bytes(1, 'big'))
            # Transmit the command byte
            ser.write(command_byte)
            # Read any returned data. NOTE: Probably not needed as it returns 0
            ser.read(response_length)

    def r_rx_pl_wid(self) -> int:
        """Read, and return the width of the payload at the top of the RX FIFO.

        Documentation:
            See [1] Table 19 for the R_RX_PL_WID command.
        """
        # Setup the uart data
        command_byte = COMMANDS['R_RX_PL_WID'].to_bytes(1, 'big')
        command_length = len(command_byte)  # 1 command byte
        transfer_length = 2  # [(tx) 1 command byte | (rx) 1 status byte]
        response_length = 2  # 1 status byte + 1 RX_PL_WID byte
        with serial.Serial(self.port, self.BAUD, timeout=1) as ser:
            # Transmit the UART command length header
            ser.write(command_length.to_bytes(1, 'big'))
            # Transmit the SPI transfer length header
            ser.write(transfer_length.to_bytes(1, 'big'))
            # Transmit the UART reponse length header
            ser.write(response_length.to_bytes(1, 'big'))
            # Transmit the command byte
            ser.write(command_byte)
            # Read and return the receive payload width (Skip the STATUS byte).
            uart_response = ser.read(response_length)[1:]
            rx_pl_wid = int(uart_response)
        return rx_pl_wid

    def w_ack_payload(self, payload: bytes, pipe: int) -> None:
        # TODO: This command is nonfunctoinal at the momoent, and it requires
        # the logic for the pipe argument.
        """Write the payload to be transmitted together with the ACK packet.

        Keyword arguments:
            payload -- The data to be transmitted. Can be 32 bytes in length or
            less. The payload must be of type <bytes>.
            pipe -- The pipe to transmit the ACK payload to. The pipe is an
            integer in the range [0,5]
        Documentation:
            See [1] Table 19 for the W_ACK_PAYLOAD command.
        """
        if type(payload) != bytes:
            raise TypeError("Payload must be of type <bytes>.")
        if len(payload) > 32:
            raise ValueError("Payload must be 0-32 bytes in length.")
        if pipe < 0 or pipe > 5:
            raise ValueError("The specified pipe must be in rane [0,5].")
        # Setup the uart data
        command_byte = (COMMANDS['W_ACK_PAYLOAD'] | pipe).to_bytes(1, 'big')
        # 1 command byte + payload bytes
        command_length = len(command_byte) + len(payload)
        # [(tx) 1 command byte | (rx) 1 status byte] + payload bytes
        transfer_length = 1 + len(payload)
        response_length = 0  # 1 status byte
        with serial.Serial(self.port, self.BAUD, timeout=1) as ser:
            # Transmit the UART command length header
            ser.write(command_length.to_bytes(1, 'big'))
            # Transmit the SPI transfer length header
            ser.write(transfer_length.to_bytes(1, 'big'))
            # Transmit the UART reponse length header
            ser.write(response_length.to_bytes(1, 'big'))
            # Transmit the command byte
            # The pipe is or'd with the command byte. See [1] Section 8.3.1
            # Table 19
            ser.write(command_byte)
            # Transmit the payload
            ser.write(payload)
            # Read any returned data. NOTE: Probably not needed as it returns 0
            ser.read(response_length)

    def w_tx_payload_noack(self, payload: bytes) -> None:
        """Transmit the payload data with AUTOACK disabled on this packet.

        Keyword arguments:
            payload -- The data to be transmitted. Can be 32 bytes in length or
            less. The payload must be of type <bytes>.
        Documentation:
            See [1] Table 19 for the W_TX_PAYLOAD_NOACK command.
        """
        if type(payload) != bytes:
            raise TypeError("The payload data must be of type <bytes>.")
        if len(payload) > 32:
            raise ValueError("Payload must be 0-32 bytes in length.")
        # Setup the uart data
        command_byte = COMMANDS['W_TX_PAYLOAD_NOACK'].to_bytes(1, 'big')
        # 1 command byte + payload bytes
        command_length = len(command_byte) + len(payload)
        # [(tx) 1 command byte | (rx) 1 status byte] + (tx) payload bytes
        transfer_length = 1 + len(payload)
        response_length = 0  # None (Ignore the status byte)
        with serial.Serial(self.port, self.BAUD, timeout=1) as ser:
            # Transmit the UART command length header
            ser.write(command_length.to_bytes(1, 'big'))
            # Transmit the SPI transfer length header
            ser.write(transfer_length.to_bytes(1, 'big'))
            # Transmit the UART reponse length header
            ser.write(response_length.to_bytes(1, 'big'))
            # Transmit the command byte
            ser.write(command_byte)
            # Transmit the payload
            ser.write(payload)
            # Read any returned data. NOTE: Probably not needed as it returns 0
            ser.read(response_length)

    def nop(self) -> None:
        """No operation. Sends 0xFF to the nRF24L01.

        Documentation:
            See [1] Table 19 for the NOP command.
        """
        # Setup the UART data
        command_byte = COMMANDS['NOP'].to_bytes(1, 'big')
        command_length = len(command_byte)  # 1 command byte
        transfer_length = 1  # [(tx) 1 command byte | (rx) 1 status byte]
        response_length = 0  # Return nothing (Ignore the STATUS byte).
        # Transceive the UART data
        with serial.Serial(self.port, self.BAUD, timeout=1) as ser:
            # Transmit the UART command length header
            ser.write(command_length.to_bytes(1, 'big'))
            # Transmit the SPI trans length header
            ser.write(transfer_length.to_bytes(1, 'big'))
            # Transmit the UART response length header
            ser.write(response_length.to_bytes(1, 'big'))
            # Transmit the command byte
            ser.write(command_byte)
            # Read any returned data. NOTE: Probably not needed as it returns 0
            ser.read(response_length)


# TODO: Add an option to the command functions `return_status=False`, if true,
# then the function also returns the status register. The reason being that I
# want to simplify the returned data.
# TODO: Send a packet to detect if the receiver (mcu) is listening. If it is not
# listening, then raise an error. Sort of a RTS, and ACK idea.
# TODO: Add the ability to detect the presence of a device or not, and raise an
# error to say that the device was not found. (Same as the above TODO?)
