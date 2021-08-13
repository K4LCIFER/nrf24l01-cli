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
    print("Platform \"" + platform.system() + "\" is not supported!")



# Command names and words. See [1]Section 8.3.1 Table 19.
# NOTE: I am not sure if it is correct to vertically align these in this
# scenario. According to PEP8, it seems to be incorrect. Further research is 
# required.
COMMANDS = {
        'R_REGISTER'         : 0x00,
        'W_REGISTER'         : 0x20,
        'R_RX_PAYLOAD'       : 0x61,
        'W_TX_PAYLOAD'       : 0xA0,
        'FLUSH_TX'           : 0xE1,
        'FLUSH_RX'           : 0xE2,
        'REUSE_TX_PL'        : 0xE3,
        'R_RX_PL_WID'        : 0x60,
        'W_ACK_PAYLOAD'      : 0xA8,
        'W_TX_PAYLOAD_NOACK' : 0xB0,
        'NOP'                : 0xFF
        }


# Register mnemonics and addresses with their bit mnemonics and bit positions.
# See [1]Section 9.1 Table 27.
REGISTER_MAP = {
        'CONFIG': {
            'ADDRESS': 0x00,
            'MASK_RX_DR': {
                'LENGTH': 1,
                'OFFSET': 6
                },
            'MASK_TX_DS': {
                'LENGTH': 1,
                'OFFSET': 5
                },
            'MASK_MAX_RT': {
                'LENGTH': 1,
                'OFFSET': 4
                },
            'EN_CRC': {
                'LENGTH': 1,
                'OFFSET': 3
                },
            'CRCO': {
                'LENGTH': 1,
                'OFFSET': 2
                },
            'PWR_UP': {
                'LENGTH': 1,
                'OFFSET': 1
                },
            'PRIM_RX': {
                'LENGTH': 1,
                'OFFSET': 0
                }
            },
        'EN_AA': {
            'ADDRESS': 0x01,
            'ENAA_P5': {
                'LENGTH': 1,
                'OFFSET': 5
                },
            'ENAA_P4': {
                'LENGTH': 1,
                'OFFSET': 4
                },
            'ENAA_P3': {
                'LENGTH': 1,
                'OFFSET': 3
                },
            'ENAA_P2': {
                'LENGTH': 1,
                'OFFSET': 2
                },
            'ENAA_P1': {
                'LENGTH': 1,
                'OFFSET': 1
                },
            'ENAA_P0': {
                'LENGTH': 1,
                'OFFSET': 0
                }
            },
        'EN_RXADDR': {
            'ADDRESS': 0x02,
            'ERX_P5': {
                'LENGTH': 1,
                'OFFSET': 5
                },
            'ERX_P4': {
                'LENGTH': 1,
                'OFFSET': 4
                },
            'ERX_P3': {
                'LENGTH': 1,
                'OFFSET': 3
                },
            'ERX_P2': {
                'LENGTH': 1,
                'OFFSET': 2
                },
            'ERX_P1': {
                'LENGTH': 1,
                'OFFSET': 1
                },
            'ERX_P0': {
                'LENGTH': 1,
                'OFFSET': 0
                }
            },
        'SETUP_AW': { 
            'ADDRESS': 0x03,
            'AW': {
                'LENGTH': 2,
                'OFFSET': 0
                }
            },
        'SETUP_RETR': {
            'ADDRESS': 0x04,
            'ARD': {
                'LENGTH': 4,
                'OFFSET': 4
                },
            'ARC': {
                'LENGTH': 4,
                'OFFSET': 0
                }
            },
        'RF_CH': {
            'ADDRESS': 0x05,
            'RF_CH': {
                'LENGTH': 7,
                'OFFSET': 0
                }
            },
        'RF_SETUP': {
            'ADDRESS': 0x06,
            'CONT_WAVE': {
                'LENGTH': 1,
                'OFFSET': 7
                },
            'RF_DR_LOW': {
                'LENGTH': 1,
                'OFFSET': 5
                },
            'PLL_LOCK': {
                'LENGTH': 1,
                'OFFSET': 4
                },
            'RF_DR_HIGH': {
                'LENGTH': 1,
                'OFFSET': 3
                },
            'RF_PWR': {
                'LENGTH': 2,
                'OFFSET': 1
                }
            },
        'STATUS': {
            'ADDRESS': 0x07,
            'RX_DR': {
                'LENGTH': 1,
                'OFFSET': 6
                },
            'TX_DS': {
                'LENGTH': 1,
                'OFFSET': 5
                },
            'MAX_RT': {
                'LENGTH': 1,
                'OFFSET': 4
                },
            'RX_P_NO': {
                'LENGTH': 3,
                'OFFSET': 1
                },
            'TX_FULL': {
                'LENGTH': 1,
                'OFFSET': 0
                },
            },
        'OBSERVE_TX': {
            'ADDRESS': 0x08,
            'PLOS_CNT': {
                'LENGTH': 4,
                'OFFSET': 4
                },
            'ARC_CNT': {
                'LENGTH': 4,
                'OFFSET': 0
                }
            },
        'RPD': { # RPD or CD?
            'ADDRESS': 0x09,
            'RPD': {
                'LENGTH': 1,
                'OFFSET': 0
                }
            },
        'RX_ADDR_P0': {
            'ADDRESS': 0x0A
            },
        'RX_ADDR_P1': {
            'ADDRESS': 0x0B
            },
        'RX_ADDR_P2': {
            'ADDRESS': 0x0C
            },
        'RX_ADDR_P3': {
            'ADDRESS': 0x0D
            },
        'RX_ADDR_P4': {
            'ADDRESS': 0x0E
            },
        'RX_ADDR_P5': {
            'ADDRESS': 0x0F
            },
        'TX_ADDR': {
            'ADDRESS': 0x10
            },
        'RX_PW_P0': {
            'ADDRESS': 0x11,
            'RX_PW_P0': {
                'LENGTH': 6,
                'OFFSET': 0
                }
            },
        'RX_PW_P1': {
            'ADDRESS': 0x12,
            'RX_PW_P1': {
                'LENGTH': 6,
                'OFFSET': 0
                }
            },
        'RX_PW_P2': {
            'ADDRESS': 0x13,
            'RX_PW_P2': {
                'LENGTH': 6,
                'OFFSET': 0
                }
            },
        'RX_PW_P3': {
            'ADDRESS': 0x14,
            'RX_PW_P3': {
                'LENGTH': 6,
                'OFFSET': 0
                }
            },
        'RX_PW_P4': {
            'ADDRESS': 0x15,
            'RX_PW_P4': {
                'LENGTH': 6,
                'OFFSET': 0
                }
            },
        'RX_PW_P5': {
            'ADDRESS': 0x16,
            'RX_PW_P5': {
                'LENGTH': 6,
                'OFFSET': 0
                }
            },
        'FIFO_STATUS': {
            'ADDRESS': 0x17,
            'TX_REUSE': {
                'LENGTH': 1,
                'OFFSET': 6
                },
            'TX_FULL': {
                'LENGTH': 1,
                'OFFSET': 5
                },
            'TX_EMPTY': {
                'LENGTH': 1,
                'OFFSET': 4
                },
            'RX_FULL': {
                'LENGTH': 1,
                'OFFSET': 1
                },
            'RX_EMPTY': {
                'LENGTH': 1,
                'OFFSET': 0
                }
            },
        'DYNPD': {
            'ADDRESS':0x1C,
            'DPL_P5': {
                'LENGTH': 1,
                'OFFSET': 5
                },
            'DPL_P4': {
                'LENGTH': 1,
                'OFFSET': 4
                },
            'DPL_P3': {
                'LENGTH': 1,
                'OFFSET': 3
                },
            'DPL_P2': {
                'LENGTH': 1,
                'OFFSET': 2
                },
            'DPL_P1': {
                'LENGTH': 1,
                'OFFSET': 1
                },
            'DPL_P0': {
                'LENGTH': 1,
                'OFFSET': 0
                }
            },
        'FEATURE': {
            'ADDRESS': 0x1D,
            'EN_DPL': {
                'LENGTH': 1,
                'OFFSET': 2
                },
            'EN_ACK_PAY': {
                'LENGTH': 1,
                'OFFSET': 1
                },
            'EN_DYN_ACK': {
                'LENGTH': 1,
                'OFFSET': 0
                }
            }
        }

# Extracts the value from one or more bits in binary data.
def _extract_bit_value(data, number_of_bits, offset):
    return ((1 << number_of_bits) - 1) & (data >> offset)

# Retrieve the contents of the status register of the nRF24L01, and return it as
# a dictionary.
def get_status():
    # TODO: Need to add the functionality to retrieve the FIFO_STATUS, as well.
    with serial.Serial(PORT, BAUD, timeout=1) as ser:
        ser.write(bytes([COMMANDS['NOP']]))    # Send an empty packet
        # Read the status register. (convert  bytes data type to int)
        status = int.from_bytes(ser.read(1), byteorder='big',
                signed=False)

    # Separate each portion of the received status register data into its
    # separate bit mnemonic sections.
    status_register = {}
    status_register['RAW'] = status # Raw received data
    status_register['RX_DR'] = _extract_bit_value(status,
        REGISTER_MAP['STATUS']['RX_DR']['LENGTH'],
        REGISTER_MAP['STATUS']['RX_DR']['OFFSET'])
    status_register['TX_DS'] = _extract_bit_value(status,
        REGISTER_MAP['STATUS']['TX_DS']['LENGTH'],
        REGISTER_MAP['STATUS']['TX_DS']['OFFSET'])
    status_register['MAX_RT'] = _extract_bit_value(status,
        REGISTER_MAP['STATUS']['MAX_RT']['LENGTH'],
        REGISTER_MAP['STATUS']['MAX_RT']['OFFSET'])
    status_register['RX_P_NO'] = _extract_bit_value(status,
        REGISTER_MAP['STATUS']['RX_P_NO']['LENGTH'],
        REGISTER_MAP['STATUS']['RX_P_NO']['OFFSET'])
    status_register['TX_FULL'] = _extract_bit_value(status,
        REGISTER_MAP['STATUS']['TX_FULL']['LENGTH'],
        REGISTER_MAP['STATUS']['TX_FULL']['OFFSET'])

    return status_register
