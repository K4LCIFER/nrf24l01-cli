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
# TODO: Add a datasheet reference here?
################################################################################


# Command names and words. See Section 8.3.1 Table 19.
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
# See Section 9.1 Table 27.
REGISTER_MAP = {
        'CONFIG' : {
            'ADDRESS'     : 0x00,
            'MASK_RX_DR'  : 6,
            'MASK_TX_DS'  : 5,
            'MASK_MAX_RT' : 4,
            'EN_CRC'      : 3,
            'CRCO'        : 2,
            'PWR_UP'      : 1,
            'PRIM_RX'     : 0
            },
        'EN_AA': {
            'ADDRESS' : 0x01,
            'ENAA_P5' : 5,
            'ENAA_P4' : 4,
            'ENAA_P3' : 3,
            'ENAA_P2' : 2,
            'ENAA_P1' : 1,
            'ENAA_P0' : 0
            },
        'EN_RXADDR': {
            'ADDRESS': 0x02,
            'ERX_P5' : 5,
            'ERX_P4' : 4,
            'ERX_P3' : 3,
            'ERX_P2' : 2,
            'ERX_P1' : 1,
            'ERX_P0' : 0,
            },
        'SETUP_AW': { 
            'ADDRESS' : 0x03,
            'AW'      : 0  # Bit-range 1:0
            },
        'SETUP_RETR' : {
            'ADDRESS': 0x04,
            'ARD' : 4, # Bit-range 7:4
            'ARC' : 0, # Bit-range 3:0
            },
        'RF_CH' : {
            'ADDRESS': 0x05
            # Bit of the same name at bit-6:0
            },
        'RF_SETUP' : {
            'ADDRESS': 0x06,
            'CONT_WAVE'  : 7,
            'RF_DR_LOW'  : 5,
            'PLL_LOCK'   : 4,
            'RF_DR_HIGH' : 3,
            'RF_PWR'     : 1,  # Bit-range 2:1
            },
        'STATUS' :{
            'ADDRESS': 0x07,
            'RX_DR'   : 6,
            'TX_DS'   : 5,
            'MAX_RT'  : 4,
            'RX_P_NO' : 1, # Bit-range 3:1
            'TX_FULL' : 0,
            },
        'OBSERVE_TX' : {
            'ADDRESS': 0x08,
            'PLOS_CNT' : 4,    # Bit-range 7:4
            'ARC_CNT'  : 0,    # Bit-range 3:0
            },
        'RPD' : {
            'ADDRESS': 0x09  # RPD or CD?
            # Bit is of the same name at bit-0
            },
        'RX_ADDR_P0' :{
            'ADDRESS': 0x0A
            },
        'RX_ADDR_P1' :{
            'ADDRESS': 0x0B
            },
        'RX_ADDR_P2' :{
            'ADDRESS': 0x0C
            },
        'RX_ADDR_P3' :{
            'ADDRESS': 0x0D
            },
        'RX_ADDR_P4' :{
            'ADDRESS': 0x0E
            },
        'RX_ADDR_P5' :{
            'ADDRESS': 0x0F
            },
        'TX_ADDR' :{
            'ADDRESS': 0x10
            },
        'RX_PW_P0' :{
            'ADDRESS':0x11
            # Bit is of the same name at bit-5:0
            },
        'RX_PW_P1' : {
            'ADDRESS':0x12
            # Bit is of the same name at bit-5:0
            },
        'RX_PW_P2' : {
            'ADDRESS': 0x13
            # Bit is of the same name at bit-5:0
            },
        'RX_PW_P3' : {
            'ADDRESS':0x14
            # Bit is of the sa:me name at bit-5:0
            },
        'RX_PW_P4' : {
            'ADDRESS': 0x15
            # Bit is of the same name at bit-5:0
            },
        'RX_PW_P5' : {
            'ADDRESS':0x16
            # Bit is of the same name at bit-5:0
            },
        'FIFO_STATUS' : {
            'ADDRESS': 0x17,
            'TX_REUSE' : 6,
            # TX_FULL   # Repeat from the status register
            'TX_EMPTY' : 4,
            'RX_FULL'  : 1,
            'RX_EMPTY' : 0,
            },
        'DYNPD' : {
            'ADDRESS':0x1C,
            'DPL_P5' : 5,
            'DPL_P4' : 4,
            'DPL_P3' : 3,
            'DPL_P2' : 2,
            'DPL_P1' : 1,
            'DPL_P0' : 0,
            },
        'FEATURE' :{ 
            'ADDRESS': 0x1D,
            'EN_DPL'     : 2,
            'EN_ACK_PAY' : 1,
            'EN_DYN_ACK' : 0,
            }
        }

