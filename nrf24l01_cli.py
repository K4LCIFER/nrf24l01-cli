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
import argparse
from nrf24l01_control import nRF24L01, REGISTER_MAP

# nrf24l01 = nRF24L01('/dev/ttyUSB0')

# Extracts the value from one or more bits in binary data.
def extract_bit_value(data, number_of_bits, offset):
    return ((1 << number_of_bits) - 1) & (data >> offset)


# Get the number of bytes that an integer requires
def byte_length(i):
    return (i.bit_length() + 7) // 8


# Define the command line subcommands and arguments
def get_args():
    parser = argparse.ArgumentParser(
        description="Debug and control an nRF24L01 module from the command \
                line."
    )
    parser.add_argument('--version', '-v', action='store_true')

    subparsers = parser.add_subparsers(
        dest='command_name', help="Commands to interract with the nRF24L01."
    )

    ############################################################################
    # The `status` command:
    # The status command fetches the contents of the STATUS, and FIFO_STATUS
    # registers, and prints them.
    status_parser = subparsers.add_parser('status')
    # Allows the user to switch between the default output of the total value
    # of the status registers, and the broken down bit mnemonic values
    status_parser.add_argument('--verbose', '-v', action='store_true')
    # NOTE: Change this parser mutually exclusive group name. too long.  Switch
    # the output to different integer formats: hexadecimal, binary.  The
    # default output is decimal.
    status_parser_number_format = status_parser.add_mutually_exclusive_group()
    status_parser_number_format.add_argument(
        '--hexadecimal', '-x', action='store_true'
    )
    status_parser_number_format.add_argument(
        '--binary', '-b', action='store_true'
    )
    # status_parser_number_format.add_argument(
    # '--decimal', '-d', action='store_true'
    # )
    ############################################################################
    # The `reset` command:
    # The reset command resets all registers to their default value.
    # TODO Perhaps add a reset --mode option to reset only the tx or rx state
    # to power down or standby or something.
    reset_parser = subparsers.add_parser('reset')
    # Print the operational output of the reset command.
    reset_parser.add_argument('--verbose', '-v', action='store_true')
    ############################################################################
    # The `config` command:
    # The config command provides a means to cofigure
    config_parser = subparsers.add_parser('config')
    config_parser.add_argument(
        '--rx-dr-irq',
        dest='rx_dr_irq',
        action='store',
        nargs='?',
        const=True,
        default=None,
        choices=['enable', 'disable'],
    )
    config_parser.add_argument(
        '--tx-ds-irq',
        dest='tx_ds_irq',
        action='store',
        nargs='?',
        const=True,
        default=None,
        choices=['enable', 'disable'],
    )
    config_parser.add_argument(
        '--max-rt-irq',
        dest='max_rt_irq',
        action='store',
        nargs='?',
        const=True,
        default=None,
        choices=['enable', 'disable'],
    )
    config_parser.add_argument(
        '--crc',
        dest='crc',
        action='store',
        nargs='?',
        const=True,
        default=None,
        choices=['1', '2', 'disable'],
    )
    # NOTE: Perhaps combine ard and arc into one auto-retransmit option;
    # although, I am unsure the proper way to get the data. For Now I am going
    # to hold of on these to as I'm not sure on the best way to set up the
    # option.
    config_parser.add_argument('--ard', action='store', type=int)
    config_parser.add_argument('--arc', action='store')
    config_parser.add_argument(
        '--rf-ch',
        dest='rf_ch',
        action='store',
        type=int,
        nargs='?',
        const=True,
        default=None,
        metavar='[0...127]',
    )
    config_parser.add_argument(
        '--cont-wave',
        dest='cont_wave',
        action='store',
        nargs='?',
        const=True,
        default=None,
        choices=['enable', 'disable'],
    )
    config_parser.add_argument(
        '--rf-dr',
        dest='rf_dr',
        action='store',
        nargs='?',
        const=True,
        default=None,
        choices=[
            'high',
            'med',
            'low',
        ],  # Change to max med min?
    )
    config_parser.add_argument(
        '--pll-lock',
        dest='pll_lock',
        action='store',
        nargs='?',
        const=True,
        default=None,
        choices=[
            'enable',
            'disable',
        ],
    )
    config_parser.add_argument(
        '--rf-pwr',
        dest='rf_pwr',
        action='store',
        nargs='?',
        const=True,
        default=None,
        choices=[
            'min',
            'low',
            'med',
            'max',
        ],
    )
    config_parser.add_argument(
        '--rx-addr-p0',
        dest='rx_addr_p0',
        action='store',
        nargs='?',
        const=True,
        default=None,
    )
    config_parser.add_argument(
        '--rx-addr-p1',
        dest='rx_addr_p1',
        action='store',
        nargs='?',
        const=True,
        default=None,
    )
    config_parser.add_argument(
        '--rx-addr-p2',
        dest='rx_addr_p2',
        action='store',
        nargs='?',
        const=True,
        default=None,
    )
    config_parser.add_argument(
        '--rx-addr-p3',
        dest='rx_addr_p3',
        action='store',
        nargs='?',
        const=True,
        default=None,
    )
    config_parser.add_argument(
        '--rx-addr-p4',
        dest='rx_addr_p4',
        action='store',
        nargs='?',
        const=True,
        default=None,
    )
    config_parser.add_argument(
        '--rx-addr-p5',
        dest='rx_addr_p5',
        action='store',
        nargs='?',
        const=True,
        default=None,
    )
    config_parser.add_argument(
        '--tx-addr',
        dest='tx_addr',
        action='store',
        nargs='?',
        const=True,
        default=None,
    )
    ############################################################################
    # The `dump` command:
    dump_parser = subparsers.add_parser('dump')
    dump_parser.add_argument(
        '--verbose', '-v', dest='verbose', action='store_true'
    )
    dump_parser.add_argument('-b', dest='binary', action='store_true')
    dump_parser.add_argument('-d', dest='decimal', action='store_true')
    dump_parser.add_argument('-x', dest='hexadecimal', action='store_true')
    dump_parser.add_argument('register', action='store')
    ############################################################################
    # The `load` command:
    load_parser = subparsers.add_parser('load')
    load_parser.add_argument(
        '--verbose', '-v', dest='verbose', action='store_true'
    )
    load_parser.add_argument('-b', dest='binary', action='store_true')
    load_parser.add_argument('-d', dest='decimal', action='store_true')
    load_parser.add_argument('-x', dest='hexadecimal', action='store_true')
    load_parser.add_argument('register', action='store')
    load_parser.add_argument('payload', action='store')
    ############################################################################
    # The `transmit` command:
    # TODO add metavar for pipe and width to show their ranges.
    # TODO make the payload format options all mutually exclusive as it doesn't
    # make sense for say binary and decimal to be specified at the same time.
    transmit_parser = subparsers.add_parser('transmit')
    transmit_parser.add_argument('--hexadecimal', '-x', action='store_true')
    transmit_parser.add_argument('--binary', '-b', action='store_true')
    transmit_parser.add_argument('--decimal', '-d', action='store_true')
    transmit_parser.add_argument('--string', '-s', action='store_true')
    transmit_parser.add_argument(
        'payload', action='store'  # lambda x: int(x, 0),
    )
    transmit_parser.add_argument(
        '--pipe', action='store', type=int, default=None
    )
    transmit_parser.add_argument(
        '--width', action='store', type=int, default=None
    )
    ############################################################################
    # The `receive` command:
    receive_parser = subparsers.add_parser('receive')
    # Enable the receiver to receive in the background, to receive the
    # specified number of bytes.
    # TODO: Change these two options to be mutually exclusive. They don't make
    # a whole lot of sense to be in the same command, and I don't think that
    # they would even work if they are in the same command.
    receive_parser.add_argument('--detach', action='store_true')
    receive_parser.add_argument(
        '--number-of-packets',
        '-n',
        dest='number_of_packets',
        action='store',
        type=int,
    )
    receive_parser.add_argument(
        '--width',
        action='store',
        type=int,
        required=True,
    )
    receive_parser.add_argument(
        '--pipe',
        action='store',
        type=int,
    )
    ############################################################################
    return parser.parse_args()


def status(args, nrf24l01):
    # Read and store the contents of the STATUS, and FIFO_STATUS registers.
    status = int.from_bytes(nrf24l01.r_register('STATUS'), 'big')
    fifo_status = int.from_bytes(nrf24l01.r_register('FIFO_STATUS'), 'big')
    if args.verbose:
        print("STATUS:")
        # Extract the values of each bit mnemonic and print them.
        for bit_mnemonic in REGISTER_MAP['STATUS']:
            # NOTE: I don't like that I need this if statement. I need to
            # alter the memory map to not need this if statement.
            if (
                bit_mnemonic != 'ADDRESS'
                and bit_mnemonic != 'NUMBER_OF_DATA_BYTES'
                and bit_mnemonic != 'RESET_VALUE'
            ):
                bit_mnemonic_value = extract_bit_value(
                    status,
                    REGISTER_MAP['STATUS'][bit_mnemonic]['LENGTH'],
                    REGISTER_MAP['STATUS'][bit_mnemonic]['OFFSET'],
                )
                if args.hexadecimal:
                    bit_mnemonic_value = format(bit_mnemonic_value, 'X')
                elif args.binary:
                    bit_mnemonic_value = format(bit_mnemonic_value, 'b')
                # Default to printing in decimal. NOTE: possbly change this
                # to default to printing in binary, since it would be of
                # more use.
                else:
                    bit_mnemonic_value = format(bit_mnemonic_value, 'd')
                print("  {0}: {1}".format(bit_mnemonic, bit_mnemonic_value))
        print("\n", end='')
        print("FIFO_STATUS:")
        for bit_mnemonic in REGISTER_MAP['FIFO_STATUS']:
            # NOTE: I don't like that I need this if statement. I need to
            # alter the memory map to not need this if statement.
            if (
                bit_mnemonic != 'ADDRESS'
                and bit_mnemonic != 'NUMBER_OF_DATA_BYTES'
                and bit_mnemonic != 'RESET_VALUE'
            ):
                # TODO: Create a local function for bit excraction instead
                # of using the function local to the nrf24l01 module.
                bit_mnemonic_value = extract_bit_value(
                    status,
                    REGISTER_MAP['FIFO_STATUS'][bit_mnemonic]['LENGTH'],
                    REGISTER_MAP['FIFO_STATUS'][bit_mnemonic]['OFFSET'],
                )
                if args.hexadecimal:
                    bit_mnemonic_value = format(bit_mnemonic_value, 'X')
                elif args.binary:
                    bit_mnemonic_value = format(bit_mnemonic_value, 'b')
                # Default to printing in decimal. NOTE: possbly change this
                # to default to printing in binary, since it would be of
                # more use.
                else:
                    bit_mnemonic_value = format(bit_mnemonic_value, 'd')
                print("  {0}: {1}".format(bit_mnemonic, bit_mnemonic_value))
    elif not args.verbose:
        if args.hexadecimal:
            status = format(status, 'X')
            fifo_status = format(fifo_status, 'X')
        elif args.binary:
            status = format(status, '08b')
            fifo_status = format(fifo_status, '08b')
        else:
            status = format(status, 'd')
            fifo_status = format(fifo_status, 'd')
        print("STATUS: {0}".format(status))
        print("FIFO_STATUS: {0}".format(fifo_status))


def reset(args, nrf24l01):
    verification_failure = False
    # NOTE: Should a verification step be performed afterwards?
    # Reset all registers.
    for register_name in REGISTER_MAP:
        if register_name not in [
            'STATUS',
            'OBSERVE_TX',
            'RPD',
            'FIFO_STATUS',
        ]:
            # Get the reset value for the specific regegister.
            reset_value = REGISTER_MAP[register_name]['RESET_VALUE'].to_bytes(
                # Some registers have more than 1 byte, so that needs to be
                # fetched, so that the right number of bytes are written.
                REGISTER_MAP[register_name]['NUMBER_OF_DATA_BYTES'],
                'big',
            )
            # If requested, give feedback on the status of the reset
            # command.
            if args.verbose:
                print(
                    "Resetting "
                    + register_name
                    + " to {0:#0x}...".format(
                        int.from_bytes(reset_value, 'big'),
                    )
                )
            # Write the reset value to the register.
            nrf24l01.w_register(register_name, reset_value)
            # Perform a verification step to check if the register was
            # successfully reset.
            # TODO: Clean up the command line output. It's somewhat messy.
            if args.verbose:
                print("Verifying " + register_name + "... ", end='')
            stored_value = nrf24l01.r_register(register_name)
            if stored_value == reset_value:
                if args.verbose:
                    print("PASSED")
            elif stored_value != reset_value:
                if args.verbose:
                    print("FAILED")
                verification_failure = True
        # Flush tx, and rx
        if args.verbose:
            print("Flushing TX_DATA...")
        nrf24l01.flush_tx()
        if args.verbose:
            print("Flushing RX_DATA...")
        nrf24l01.flush_rx()
        if args.verbose:
            print("Done")
        # Let the user know that there werer errors in the reset regardless of
        # the specified verbosity.
        if verification_failure:
            print("Reset failed due to 1, or more errors.")


def config(args, nrf24l01):
    # TODO: Perhaps look into simplifying some of these options by
    # condensing them into one itterative operation. Probably store a
    # dictionary of option names, and itterate over it.
    # The `--rx-dr-irq` option:
    if args.rx_dr_irq:  # TODO: Change to the new simplified version.
        # Retrieve and store the value of the CONFIG register
        current_register_value = int.from_bytes(
            nrf24l01.r_register('CONFIG'), 'big'
        )
        # Clear CONFIG:MASK_RX_DR to enable it
        if args.rx_dr_irq == 'enable':
            new_register_value = current_register_value & ~(
                1 << REGISTER_MAP['CONFIG']['MASK_RX_DR']['OFFSET']
            )
            nrf24l01.w_register('CONFIG', new_register_value.to_bytes(1, 'big'))
        # Set CONFIG:MASK_RX_DR to disable it
        elif args.rx_dr_irq == 'disable':
            new_register_value = current_register_value | (
                1 << REGISTER_MAP['CONFIG']['MASK_RX_DR']['OFFSET']
            )
            nrf24l01.w_register('CONFIG', new_register_value.to_bytes(1, 'big'))
        # Possibly change this one.
        # List the value in CONFIG:MASK_RX_DR
        elif args.rx_dr_irq is True:
            bit_value = extract_bit_value(
                current_register_value,
                REGISTER_MAP['CONFIG']['MASK_RX_DR']['LENGTH'],
                REGISTER_MAP['CONFIG']['MASK_RX_DR']['OFFSET'],
            )
            print("MASK_RX_DR = {0}".format(bit_value))
    # The `--tx-ds-irq` option:
    if args.tx_ds_irq:  # TODO: Change to the new simplified version.
        # Retrieve and store the value of the CONFIG register
        current_register_value = int.from_bytes(
            nrf24l01.r_register('CONFIG'), 'big'
        )
        # Clear CONFIG:MASK_TX_DS to enable it
        if args.tx_ds_irq == 'enable':
            new_register_value = current_register_value & ~(
                1 << REGISTER_MAP['CONFIG']['MASK_TX_DS']['OFFSET']
            )
            nrf24l01.w_register('CONFIG', new_register_value.to_bytes(1, 'big'))
        # Set CONFIG:MASK_TX_DS to disable it
        elif args.tx_ds_irq == 'disable':
            new_register_value = current_register_value | (
                1 << REGISTER_MAP['CONFIG']['MASK_TX_DS']['OFFSET']
            )
            nrf24l01.w_register('CONFIG', new_register_value.to_bytes(1, 'big'))
        # Possibly change this one.
        # List the value in CONFIG:MASK_TX_DS
        elif args.tx_ds_irq is True:
            bit_value = extract_bit_value(
                current_register_value,
                REGISTER_MAP['CONFIG']['MASK_TX_DS']['LENGTH'],
                REGISTER_MAP['CONFIG']['MASK_TX_DS']['OFFSET'],
            )
            print("MASK_TX_DS = {0}".format(bit_value))
    # The `--max-rt-irq` option:
    if args.max_rt_irq:  # TODO: Change to the new simplified version.
        # Retrieve and store the value of the CONFIG register
        current_register_value = int.from_bytes(
            nrf24l01.r_register('CONFIG'), 'big'
        )
        # Clear CONFIG:MASK_MAX_RT to enable it
        if args.max_rt_irq == 'enable':
            new_register_value = current_register_value & ~(
                1 << REGISTER_MAP['CONFIG']['MASK_MAX_RT']['OFFSET']
            )
            nrf24l01.w_register('CONFIG', new_register_value.to_bytes(1, 'big'))
        # Set CONFIG:MASK_MAX_RT to disable it
        elif args.max_rt_irq == 'disable':
            new_register_value = current_register_value | (
                1 << REGISTER_MAP['CONFIG']['MASK_MAX_RT']['OFFSET']
            )
            nrf24l01.w_register('CONFIG', new_register_value.to_bytes(1, 'big'))
        # Possibly change this one.
        # List the value in CONFIG:MASK_MAX_RT
        elif args.max_rt_irq is True:
            bit_value = extract_bit_value(
                current_register_value,
                REGISTER_MAP['CONFIG']['MASK_MAX_RT']['LENGTH'],
                REGISTER_MAP['CONFIG']['MASK_MAX_RT']['OFFSET'],
            )
            print("MASK_MAX_RT = {0}".format(bit_value))
    # The `--crc` option:
    if args.crc:
        # The CRC encoding scheme specified as 1 byte
        if args.crc == '1':
            # Ensure that CRC is enabled by setting CONFIG:EN_CRC NOTE:
            # perhaps put this in its own if statement:
            # if args.crc == '1' or args.crc == '2'
            # Store the current value of the CONFIG register
            current_register_value = int.from_bytes(
                nrf24l01.r_register('CONFIG'), 'big'
            )
            # Set CONFIG:EN_CRC
            new_register_value = current_register_value | (
                1 << REGISTER_MAP['CONFIG']['EN_CRC']['OFFSET']
            )
            nrf24l01.w_register('CONFIG', new_register_value.to_bytes(1, 'big'))
            # Set the CRC encoding scheme to 1 byte by clearing CONFIG:CRCO.
            # Store the current value of the CONFIG register
            current_register_value = int.from_bytes(
                nrf24l01.r_register('CONFIG'), 'big'
            )
            # Clear CONFIG:CRCO
            new_register_value = current_register_value & ~(
                1 << REGISTER_MAP['CONFIG']['CRCO']['OFFSET']
            )
            nrf24l01.w_register('CONFIG', new_register_value.to_bytes(1, 'big'))
        # The CRC encoding scheme specified as 2 bytes
        elif args.crc == '2':
            # Ensure that CRC is enabled by setting CONFIG:EN_CRC
            # Store the current value of the CONFIG register
            current_register_value = int.from_bytes(
                nrf24l01.r_register('CONFIG'), 'big'
            )
            # Set CONFIG:EN_CRC
            new_register_value = current_register_value | (
                1 << REGISTER_MAP['CONFIG']['EN_CRC']['OFFSET']
            )
            nrf24l01.w_register('CONFIG', new_register_value.to_bytes(1, 'big'))
            # Set the CRC encoding scheme to 2 bytes by setting CONFIG:CRCO
            # Store the currente value of the CONFIG register
            current_register_value = int.from_bytes(
                nrf24l01.r_register('CONFIG'), 'big'
            )
            # Set CONFIG:CRCO
            new_register_value = current_register_value | (
                1 << REGISTER_MAP['CONFIG']['CRCO']['OFFSET']
            )
            nrf24l01.w_register('CONFIG', new_register_value.to_bytes(1, 'big'))
        # Disable the CRC by clearing CONFIG:EN_CRC
        elif args.crc == 'disable':
            # Retrieve and store the value of the CONFIG register
            current_register_value = int.from_bytes(
                nrf24l01.r_register('CONFIG'), 'big'
            )
            new_register_value = current_register_value & ~(
                1 << REGISTER_MAP['CONFIG']['EN_CRC']['OFFSET']
            )
            nrf24l01.w_register('CONFIG', new_register_value.to_bytes(1, 'big'))
        # List the configuration of the CRC
        elif args.crc is True:
            # Retrieve and store the value of the CONFIG register
            current_register_value = int.from_bytes(
                nrf24l01.r_register('CONFIG'), 'big'
            )
            if (
                extract_bit_value(
                    current_register_value,
                    REGISTER_MAP['CONFIG']['EN_CRC']['LENGTH'],
                    REGISTER_MAP['CONFIG']['EN_CRC']['OFFSET'],
                )
                == 1
            ):
                crco = extract_bit_value(
                    current_register_value,
                    REGISTER_MAP['CONFIG']['CRCO']['LENGTH'],
                    REGISTER_MAP['CONFIG']['CRCO']['OFFSET'],
                )
                if crco == 0:
                    print("1 byte")
                elif crco == 1:
                    print("2 bytes")
            else:
                print("disabled")
    if args.rf_ch != None:
        # If a value was given, use it to set the channel
        if type(args.rf_ch) == int:
            if 0 <= args.rf_ch <= 127:
                nrf24l01.w_register('RF_CH', args.rf_ch.to_bytes(1, 'big'))
            else:
                # NOTE: Not sure if its best to raise the error or just
                # print a standard message. probably best to raise the error
                # for successful command completion purposes.
                raise ValueError(
                    "Specified channel must be in the range: [0,127]"
                )
        # If a value was not given, print the current channel
        elif args.rf_ch is True:
            print(int.from_bytes(nrf24l01.r_register('RF_CH'), 'big'))
    if args.cont_wave:
        current_register_value = int.from_bytes(
            nrf24l01.r_register('RF_SETUP'), 'big'
        )
        # Print the value of RF_SETUP:CONT_WAVE
        if args.cont_wave is True:
            # Get the current value of RF_SETUP:CONT_WAVE
            cont_wave_value = extract_bit_value(
                current_register_value,
                REGISTER_MAP['RF_SETUP']['CONT_WAVE']['LENGTH'],
                REGISTER_MAP['RF_SETUP']['CONT_WAVE']['OFFSET'],
            )
            if cont_wave_value == 1:
                print("enabled")
            elif cont_wave_value == 0:
                print("disabled")
        # Enable continuous carrier transmit by setting RF_SETUP:CONT_WAVE
        elif args.cont_wave == 'enable':
            new_register_value = current_register_value | (
                1 << REGISTER_MAP['RF_SETUP']['CONT_WAVE']['OFFSET']
            )
            nrf24l01.w_register(
                'RF_SETUP', new_register_value.to_bytes(1, 'big')
            )
        # Disable continuous carrier transmit by clearing RF_SETUP:CONT_WAVE
        elif args.cont_wave == 'disable':
            new_register_value = current_register_value & ~(
                1 << REGISTER_MAP['RF_SETUP']['CONT_WAVE']['OFFSET']
            )
            nrf24l01.w_register(
                'RF_SETUP', new_register_value.to_bytes(1, 'big')
            )
    if args.rf_dr:
        current_register_value = int.from_bytes(
            nrf24l01.r_register('RF_SETUP'), 'big'
        )
        # Print the RF data rate
        if args.rf_dr is True:
            rf_dr = extract_bit_value(
                current_register_value,
                REGISTER_MAP['RF_SETUP']['RF_DR_HIGH']['LENGTH'],
                REGISTER_MAP['RF_SETUP']['RF_DR_HIGH']['OFFSET'],
            ) << 1 | extract_bit_value(
                current_register_value,
                REGISTER_MAP['RF_SETUP']['RF_DR_LOW']['LENGTH'],
                REGISTER_MAP['RF_SETUP']['RF_DR_LOW']['OFFSET'],
            )
            if rf_dr == 0b00:
                print("med (1Mbps)")
            elif rf_dr == 0b01:
                print("high (2Mbps)")
            elif rf_dr == 0b10:
                print("low (250kbps)")
        # Set the RF data rate to 250kbps
        elif args.rf_dr == 'low':
            # Clear RF_SETUP:RF_DR_LOW and Set RF_SETUP:RF_DR_HIGH
            # Clear RF_SETUP:RF_DR_LOW
            new_register_value = current_register_value & ~(
                1 << REGISTER_MAP['RF_SETUP']['RF_DR_LOW']['OFFSET']
            )
            # Set RF_SETUP:RF_DR_HIGH
            new_register_value |= (
                1 << REGISTER_MAP['RF_SETUP']['RF_DR_HIGH']['OFFSET']
            )
            nrf24l01.w_register(
                'RF_SETUP', new_register_value.to_bytes(1, 'big')
            )
        # Set the RF data rate to 1Mbps
        elif args.rf_dr == 'med':
            # Clear RF_SETUP:RF_DR_LOW and clear RF_SETUP:RF_DR_HIGH
            # Clear RF_SETUP:RF_DR_LOW
            new_register_value = current_register_value & ~(
                1 << REGISTER_MAP['RF_SETUP']['RF_DR_LOW']['OFFSET']
            )
            # Clear RF_SETUP:RF_DR_HIGH
            new_register_value &= ~(
                1 << REGISTER_MAP['RF_SETUP']['RF_DR_HIGH']['OFFSET']
            )
            nrf24l01.w_register(
                'RF_SETUP', new_register_value.to_bytes(1, 'big')
            )
        # Set the RF data rate to 2Mbps
        elif args.rf_dr == 'high':
            # Set RF_SETUP:RF_DR_LOW and clear RF_SETUP:RF_DR_HIGH
            # Set RF_SETUP:RF_DR_LOW
            new_register_value = current_register_value | (
                1 << REGISTER_MAP['RF_SETUP']['RF_DR_LOW']['OFFSET']
            )
            # Clear RF_SETUP:RF_DR_HIGH
            new_register_value &= ~(
                1 << REGISTER_MAP['RF_SETUP']['RF_DR_HIGH']['OFFSET']
            )
            nrf24l01.w_register(
                'RF_SETUP', new_register_value.to_bytes(1, 'big')
            )
    if args.pll_lock:
        current_register_value = int.from_bytes(
            nrf24l01.r_register('RF_SETUP'), 'big'
        )
        # Print the value of RF_SETUP:PLL_LOCK
        if args.pll_lock is True:
            # Get the current value of RF_SETUP:PLL_LOCK
            pll_lock_value = extract_bit_value(
                current_register_value,
                REGISTER_MAP['RF_SETUP']['PLL_LOCK']['LENGTH'],
                REGISTER_MAP['RF_SETUP']['PLL_LOCK']['OFFSET'],
            )
            if pll_lock_value == 1:
                print("enabled")
            elif pll_lock_value == 0:
                print("disabled")
        # Enable continuous carrier transmit by setting RF_SETUP:PLL_LOCK
        elif args.pll_lock == 'enable':
            new_register_value = current_register_value | (
                1 << REGISTER_MAP['RF_SETUP']['PLL_LOCK']['OFFSET']
            )
            nrf24l01.w_register(
                'RF_SETUP', new_register_value.to_bytes(1, 'big')
            )
        # Disable continuous carrier transmit by clearing RF_SETUP:PLL_LOCK
        elif args.pll_lock == 'disable':
            new_register_value = current_register_value & ~(
                1 << REGISTER_MAP['RF_SETUP']['PLL_LOCK']['OFFSET']
            )
            nrf24l01.w_register(
                'RF_SETUP', new_register_value.to_bytes(1, 'big')
            )
    if args.rf_pwr:
        # Get, and store the current value of the RF_SETUP register
        current_register_value = int.from_bytes(
            nrf24l01.r_register('RF_SETUP'), 'big'
        )
        if args.rf_pwr is True:
            rf_pwr = extract_bit_value(
                current_register_value,
                REGISTER_MAP['RF_SETUP']['RF_PWR']['LENGTH'],
                REGISTER_MAP['RF_SETUP']['RF_PWR']['OFFSET'],
            )
            if rf_pwr == 0b00:
                print("min power (-18dBm)")
            elif rf_pwr == 0b01:
                print("low power (-12dBm)")
            elif rf_pwr == 0b10:
                print("med power (-6dBm)")
            elif rf_pwr == 0b11:
                print("max power (0dBm)")
        elif args.rf_pwr == 'min':
            new_register_value = current_register_value & (
                0 << REGISTER_MAP['RF_SETUP']['RF_PWR']['OFFSET']
            )
            nrf24l01.w_register(
                'RF_SETUP', new_register_value.to_bytes(1, 'big')
            )
        elif args.rf_pwr == 'low':
            new_register_value = current_register_value & (
                1 << REGISTER_MAP['RF_SETUP']['RF_PWR']['OFFSET']
            )
            nrf24l01.w_register(
                'RF_SETUP', new_register_value.to_bytes(1, 'big')
            )
        elif args.rf_pwr == 'med':
            new_register_value = current_register_value & (
                2 << REGISTER_MAP['RF_SETUP']['RF_PWR']['OFFSET']
            )
            nrf24l01.w_register(
                'RF_SETUP', new_register_value.to_bytes(1, 'big')
            )
        elif args.rf_pwr == 'max':
            new_register_value = current_register_value & (
                3 << REGISTER_MAP['RF_SETUP']['RF_PWR']['OFFSET']
            )
            nrf24l01.w_register(
                'RF_SETUP', new_register_value.to_bytes(1, 'big')
            )
    if args.rx_addr_p0:
        if args.rx_addr_p0 is True:
            rx_addr_p0 = int.from_bytes(
                nrf24l01.r_register('RX_ADDR_P0'), 'big'
            )
            print(format(rx_addr_p0, 'X'))
        else:
            if len(int(args.rx_addr_p0, 16).to_bytes(5, 'big')) == 5:
                rx_addr_p0 = int(args.rx_addr_p0, 16)
                nrf24l01.w_register('RX_ADDR_P0', rx_addr_p0.to_bytes(5, 'big'))
            else:
                print("Error: Addreses length must be 5 bytes.")
    if args.rx_addr_p1:
        if args.rx_addr_p1 is True:
            rx_addr_p1 = int.from_bytes(
                nrf24l01.r_register('RX_ADDR_P1'), 'big'
            )
            print(format(rx_addr_p1, 'X'))
        else:
            if len(int(args.rx_addr_p1, 16).to_bytes(5, 'big')) == 5:
                rx_addr_p1 = int(args.rx_addr_p1, 16)
                nrf24l01.w_register('RX_ADDR_P1', rx_addr_p1.to_bytes(5, 'big'))
            else:
                print("Error: Addreses length must be 5 bytes.")
    if args.rx_addr_p3:
        if args.rx_addr_p3 is True:
            rx_addr_p3 = int.from_bytes(
                nrf24l01.r_register('RX_ADDR_P3'), 'big'
            )
            print(format(rx_addr_p3, 'X'))
        else:
            if len(int(args.rx_addr_p3, 16).to_bytes(1, 'big')) == 5:
                rx_addr_p3 = int(args.rx_addr_p3, 16)
                nrf24l01.w_register('RX_ADDR_P3', rx_addr_p3.to_bytes(1, 'big'))
            else:
                print("Error: Addreses length must be 1 byte.")
    if args.rx_addr_p4:
        if args.rx_addr_p4 is True:
            rx_addr_p4 = int.from_bytes(
                nrf24l01.r_register('RX_ADDR_P4'), 'big'
            )
            print(format(rx_addr_p4, 'X'))
        else:
            if len(int(args.rx_addr_p4, 16).to_bytes(1, 'big')) == 5:
                rx_addr_p4 = int(args.rx_addr_p4, 16)
                nrf24l01.w_register('RX_ADDR_P4', rx_addr_p4.to_bytes(1, 'big'))
            else:
                print("Error: Addreses length must be 1 byte.")
    if args.rx_addr_p5:
        if args.rx_addr_p5 is True:
            rx_addr_p5 = int.from_bytes(
                nrf24l01.r_register('RX_ADDR_P5'), 'big'
            )
            print(format(rx_addr_p5, 'X'))
        else:
            if len(int(args.rx_addr_p5, 16).to_bytes(1, 'big')) == 5:
                rx_addr_p5 = int(args.rx_addr_p5, 16)
                nrf24l01.w_register('RX_ADDR_P5', rx_addr_p5.to_bytes(1, 'big'))
            else:
                print("Error: Addreses length must be 1 byte.")
    if args.tx_addr:
        if args.tx_addr is True:
            tx_addr = int.from_bytes(nrf24l01.r_register('TX_ADDR'), 'big')
            print(format(tx_addr, 'X'))
        else:
            if len(int(args.tx_addr, 16).to_bytes(5, 'big')) == 5:
                tx_addr = int(args.tx_addr, 16)
                nrf24l01.w_register('TX_ADDR', tx_addr.to_bytes(5, 'big'))
            else:
                print("Error: Addreses length must be 5 bytes.")


def dump(args, nrf24l01):
    # Special case for if RX_PLD was requested, then read the data from the
    # RX FIFO. (NOTE: Might remove later.)
    if args.register == 'RX_PLD':
        register_contents = nrf24l01.r_rx_payload(32)
    # Read the data from the command and status registers
    else:
        register_contents = nrf24l01.r_register(args.register)
    # Format the data
    if args.verbose:
        # TODO: Verbose should output the value of each individual bit
        # mnemonic. (NOTE: For now, just adding the register name will be
        # enough.)
        print(args.register + ': ', end='')
    formatted_bytes = []
    if args.binary:
        for byte in register_contents:
            formatted_bytes.append(format(byte, '08b'))
    elif args.decimal:
        for byte in register_contents:
            formatted_bytes.append(format(byte, 'd'))
    elif args.hexadecimal:
        for byte in register_contents:
            formatted_bytes.append(format(byte, '02X'))
    else:
        # Default to binary? Perhaps defaulting to a string is better.
        # TODO Add decode logic?
        for byte in register_contents:
            formatted_bytes.append(format(byte, '08b'))
    formatted_register_contents = ' '.join(formatted_bytes)
    print(formatted_register_contents)


def load(args, nrf24l01):
    # NOTE: Do I need to add a verbosity setting?
    # Parse the payload data to be of type int
    # Binary format
    if args.binary:
        payload = int(args.payload, 2)
    # Decimal format
    elif args.decimal:
        payload = int(args.payload, 10)
    # Hexadecimal format
    elif args.hexadecimal:
        payload = int(args.payload, 16)
    # String format
    else:
        payload = args.payload
    # Special case for if TX_PLD was requested: Write the payload to the
    # TX_FIFO (NOTE: Might remove this later.)
    if args.regiser == 'TX_PLD':
        nrf24l01.w_tx_payload(payload.to_bytes(byte_length(payload), 'big'))
    else:
        nrf24l01.w_register(
            args.register, payload.to_bytes(byte_length(payload), 'big')
        )


def transmit(args, nrf24l01):
    # 1. set PWR_UP to false to ensure that the module is taken out of any
    # previously set mode:
    # Get the current value of the CONFIG register
    config_register_value = int.from_bytes(nrf24l01.r_register('CONFIG'), 'big')
    # Clear CONFIG:PWR_UP
    new_config_register_value = config_register_value & ~(
        (1 << REGISTER_MAP['CONFIG']['PWR_UP']['OFFSET'])
    )
    nrf24l01.w_register('CONFIG', new_config_register_value.to_bytes(1, 'big'))
    # 2. Set PRIM_RX to false to put the module into transmit mode:
    # Get the current value of the CONFIG register
    config_register_value = int.from_bytes(nrf24l01.r_register('CONFIG'), 'big')
    # Clear CONFIG:PRIM_RX
    new_config_register_value = config_register_value & ~(
        (1 << REGISTER_MAP['CONFIG']['PRIM_RX']['OFFSET'])
    )
    nrf24l01.w_register('CONFIG', new_config_register_value.to_bytes(1, 'big'))
    # 3. set PWR_UP to true to put the module into its operational mode:
    # Get the current value of the CONFIG register
    config_register_value = int.from_bytes(nrf24l01.r_register('CONFIG'), 'big')
    # Set CONFIG:PWR_UP
    modified_register_value = config_register_value | (
        (1 << REGISTER_MAP['CONFIG']['PWR_UP']['OFFSET'])
    )
    nrf24l01.w_register('CONFIG', modified_register_value.to_bytes(1, 'big'))
    # Set the Tx address to the specified pipe address; otherwise, if the
    # pipe address is not specified, default the pipe to pipe 0.
    # NOTE: For the sake of simplicity, I want to keep the address to
    # 5 bytes in length.
    # TODO: Add a --manual setting, so that none of the specified arguments
    # can be used, and only what is used with the dump and load commands.
    if args.pipe != None:  # If the user species a pipe
        # Make sure that the pipe exists
        if 0 <= args.pipe <= 5:
            pipe_address = nrf24l01.r_register(('RX_ADDR_P' + str(args.pipe)))
            # TODO This will not work with pipes 2-5. I need to fix it to
            # take the 4 MSbytes from P1 and append the address byte from
            # the specified pipe to the end. See the Multiceiver part in the
            # datasheet.
            nrf24l01.w_register('TX_ADDR', pipe_address)
        else:
            raise ValueError("The specified pipe must be in the range [0,5].")
    else:  # Set the default Tx address to be that of pipe 0
        pipe_address = nrf24l01.r_register('RX_ADDR_P0')
        nrf24l01.w_register('TX_ADDR', pipe_address)
    # Specify how many bytes each transmitted payload will contain. This
    # also specifies how many packets a chunk of data will require by
    # splitting it up as specified by the number of bytes.
    if args.width != None:
        if 1 <= args.width <= 32:
            transmit_payload_width = args.width
        else:
            raise ValueError(
                "The specified payload width must be in the range [1,32]"
            )
    else:  # Specify a default payload width of 1
        transmit_payload_width = 1
    # Format the payload as specified by the user
    if args.hexadecimal:
        transmit_payload = int(args.payload, 16)
        transmit_payload = transmit_payload.to_bytes(
            byte_length(transmit_payload), 'big'
        )
    elif args.decimal:
        transmit_payload = int(args.payload, 10)
        transmit_payload = transmit_payload.to_bytes(
            byte_length(transmit_payload), 'big'
        )
    elif args.binary:
        transmit_payload = int(args.payload, 2)
        transmit_payload = transmit_payload.to_bytes(
            byte_length(transmit_payload), 'big'
        )
    elif args.string:
        # TODO: When picking the length to transmit, assume each character
        # in the string is 8 bits (1 byte) and just convert the string to
        # a list and count.
        transmit_payload = args.payload
    else:
        # NOTE: should probably give a warning that the default is used.
        transmit_payload = args.payload
    print(transmit_payload)
    # This clears the interrupt flags. TODO remove magic numbers.
    nrf24l01.w_register('STATUS', (0x70).to_bytes(1, 'big'))
    packet_bytes = []
    for index, byte in enumerate(transmit_payload):
        packet_bytes.append(byte.to_bytes(1, 'big'))
        if len(packet_bytes) == transmit_payload_width:
            packet = b''.join(packet_bytes)
            print(packet)
            nrf24l01.w_tx_payload(packet)
            packet_bytes = []
        elif index == len(transmit_payload) - 1 and len(packet_bytes) > 0:
            while len(packet_bytes) < transmit_payload_width:
                packet_bytes.append(b'\x00')
                packet = b''.join(packet_bytes)
                print("2")
                print(packet)
                nrf24l01.w_tx_payload(packet)
                packet_bytes = []


def receive(args, nrf24l01):
    # 1. set PWR_UP to false to ensure that the module is taken out of any
    # previously set mode:
    # Get the current value of the CONFIG register
    config_register_value = int.from_bytes(nrf24l01.r_register('CONFIG'), 'big')
    # Clear CONFIG:PWR_UP
    new_config_register_value = config_register_value & ~(
        (1 << REGISTER_MAP['CONFIG']['PWR_UP']['OFFSET'])
    )
    nrf24l01.w_register('CONFIG', new_config_register_value.to_bytes(1, 'big'))
    # 2. Set PRIM_RX to true to put the module into receive mode:
    # Get the current value of the CONFIG register
    config_register_value = int.from_bytes(nrf24l01.r_register('CONFIG'), 'big')
    # Set CONFIG:PRIM_RX
    new_config_register_value = config_register_value | (
        (1 << REGISTER_MAP['CONFIG']['PRIM_RX']['OFFSET'])
    )
    nrf24l01.w_register('CONFIG', new_config_register_value.to_bytes(1, 'big'))
    # TODO add  option for auto acknowledgement. (no ack?)
    if args.pipe != None:
        # Enable the specified pipe. args.pipe is equal to the bit position
        # of the pipes enable bit in EN_RXADDR, so bit shifting 1 by the
        # value of args.pipe in EN_RXADDR enables that address. and clears
        # the rest.
        en_rxaddr = 1 << args.pipe
        nrf24l01.w_register('EN_RXADDR', en_rxaddr.to_bytes(1, 'big'))
    # If no specific pipe is specified, then enable them all by default.
    # To enable all pipes, write 0xFF to EN_RXADDR. This sets all ERX_P[0-5]
    # bits in EN_RXADDR.
    else:
        nrf24l01.w_register('EN_RXADDR', b'\xFF')
    # If specified, set the payload width to the specified value.
    if args.width != None:
        # If the user specifies a pipe, only set the width of that specific
        # pipe. NOTE: This is probably superfluous.
        if args.pipe != None:
            pass
        # If the user does not specify a pipe, then set the width to
        # data pipes accross the device.
        else:
            pass
    if args.detach:
        # 3. set PWR_UP to true to put the module into its operational mode:
        # Get the current value of the CONFIG register
        config_register_value = int.from_bytes(
            nrf24l01.r_register('CONFIG'), 'big'
        )
        # Set CONFIG:PWR_UP
        modified_register_value = config_register_value | (
            (1 << REGISTER_MAP['CONFIG']['PWR_UP']['OFFSET'])
        )
        nrf24l01.w_register(
            'CONFIG', modified_register_value.to_bytes(1, 'big')
        )
    else:
        # Poll the data received bit, and when set, print it to the display.
        # either print continuous or only print one packet that was
        # specified (by length?)
        # If number-of-packets is specified, then only print out/receive
        # that many and then break, otherwise receive infinitely. Although,
        # that may introduce other problems as it would require the user to
        # send an interrupt signal to the running python program which could
        # interrupt a data transfer in progress which would then put the
        # mcu or the uart fifo in an undesireable state that would need to
        # be fixed with a power cycle. The other way to get around this
        # would be to fix the code of the microcotroller to implement either
        # a watchdog timer, or a timered clear of the values. Although a
        # watchdog timer might actually be the best route. Good practice too.
        # TODO Add the functionality to be able to print the received pipe
        # along with the receivd data. (should this be something that is
        # part of a verbose option?)
        number_of_received_packets = 0
        while True:
            status_value = int.from_bytes(nrf24l01.r_register('STATUS'), 'big')
            rx_dr_value = extract_bit_value(
                status_value,
                REGISTER_MAP['STATUS']['RX_DR']['LENGTH'],
                REGISTER_MAP['STATUS']['RX_DR']['OFFSET'],
            )
            if rx_dr_value == 1:
                received_data = nrf24l01.r_rx_payload(nrf24l01.r_rx_pl_wid())
                print(received_data)
                if args.number_of_packets != None:
                    number_of_received_packets += 1
                    if number_of_received_packets == args.number_of_packets:
                        break
            else:
                pass


def main():
    # Create an instance of the module at the specified port.
    nrf24l01 = nRF24L01('/dev/ttyUSB0')
    args = get_args()
    if args.version:
        print("dev")
    ############################################################################
    if args.command_name == 'status':
        status(args, nrf24l01)
    ############################################################################
    elif args.command_name == 'reset':
        reset(args, nrf24l01)
    ############################################################################
    # # The `config` command:
    elif args.command_name == 'config':
        config(args, nrf24l01)
    ############################################################################
    elif args.command_name == 'dump':
        dump(args, nrf24l01)
    ############################################################################
    elif args.command_name == 'load':
        load(args, nrf24l01)
    ############################################################################
    # # TODO: Add to the `transmit` command with --noack option (EN_ACK_PAY and
    # # EN_DYN_ACK?) (maybe also the --reuse-tx-pl option with no arguments)
    # # Before transmitting, the chip is powered down, and then the prim_rx
    # # bit is cleared and then then PWR_UP is set.
    elif args.command_name == 'transmit':
        transmit(args, nrf24l01)
    ############################################################################
    elif args.command_name == 'receive':
        receive(args, nrf24l01)


if __name__ == '__main__':
    main()

# TODO - Future Version: Change this command line interface to use click?
# Argparse is not ideal. No nesting of mutually exclusive, or regular groups,
# no different logical command requirements, very verbose etc.
# TODO Ability to store, and restore settings from a config file.
# TODO Sweep Channels command. an option for transmitting to sweep channels to
# find an optimal one?
# TODO: Add more visual feedback with each communication (verbosity setting) to
# show if communications are being successful, and at what point the
# communications are at.
# TODO: Create a bit toggling function since I will be doing that often.
# TODO: Add docstrings?
# NOTE: Think of a better way to write comments to make it more obvious that a
# comment  in python is multiline. Check PEP8? maybe post on stack overflow.
# TODO: Add binary and decimal output to reset?
# TODO: Add platform detection for port selection. It would  look something like
# the following:
# import platform
# # BAUD = 9600
# # if platform.system() == 'Linux':
# # PORT = '/dev/ttyUSB0'
# # elif platform.system() == 'Windows':
# # PORT = 'COM99'  # I'm not sure what COM port this should be.
# # else:
# # print('Platform \"' + platform.system() + '\" is not supported!')
# TODO Maybe change the arguments of the subcommand functions. eg change
# nrf24l01 to device? not sure what args would change to. 
