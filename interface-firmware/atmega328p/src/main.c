/*
 *   This program is free software: you can redistribute it and/or modify
 *   it under the terms of the GNU General Public License as published by
 *   the Free Software Foundation, either version 3 of the License, or
 *   (at your option) any later version.
 *
 *   This program is distributed in the hope that it will be useful,
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *   GNU General Public License for more details.
 *
 *   You should have received a copy of the GNU General Public License
 *   along with this program.  If not, see <https://www.gnu.org/licenses/>.
 *
 *   Copyright (c) 2021, Kalcifer
 *
 *   For more information, see https://github.com/K4LCIFER/nrf24l01-debugger
 */
#define __AVR_ATmega328P__  // Specify the device for the header includes.
#include <avr/io.h>
/*#include "uart.h"   // Need to add a uart.c and uart.h file to the directory.*/
/*#include "spi.h"    // Same as above. Structure these like the arduino library.*/
// See Table 20-6 Row 3 Column 2



#define USART_BAUD_PRESCALER 51



void initialize_uart(void)
{
    // TODO Need to change this later to account for different CPU frequencies.
    // See Section 20.5 and 20.11.5
    UBRR0H = (unsigned char) (USART_BAUD_PRESCALER >> 8);
    UBRR0L = (unsigned char) USART_BAUD_PRESCALER;
    // Set the frame size of the receiver and transmitter to 8-bits. See
    // Table 20-11
    UCSR0C |= (UCSZ01 | UCSZ00);
    // Enable the transmitter and the rceiver. See Section 20.11.3.
    UCSR0B |= (TXEN0 | RXEN0);
}



int main()
{
}
