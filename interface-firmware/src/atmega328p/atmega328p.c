/*******************************************************************************
 *  This program is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program.  If not, see <https://www.gnu.org/licenses/>.
 *
 *  Copyright (c) 2021, Kalcifer
 *
 *  For more information, see https://github.com/K4LCIFER/nrf24l01-debugger
 ******************************************************************************/
/*******************************************************************************
 * 1. [ATmega328p Datasheet]()
 * 2. [nRF24L01 Datasheet]()
 ******************************************************************************/
/******************************************************************************/
/*
 * This define is a temporary solution for Vim CoC support for AVR programming.
 * The only catch is that a compile warning will be raised for a duplicate
 * define when you compile with `avr-gcc -mmcu=atmega328p`. This serves no
 * purpose for the code itself beyond easing its development.
 */
#define __AVR_ATmega328P__
/******************************************************************************/

#include <avr/io.h>
#include <avr/interrupt.h>


#define USART_BUAD 9600
#define USART_BAUD_PRESCALER 51


// Buffer for the command received over UART.
unsigned char received_command[33];
// Index to keep track of how many bytes have been received over UART.
unsigned char received_command_index;
// Buffer to store the data received from the nRF24L01 during an SPI transfer.
unsigned char received_spi_data[33];
// The expected length of a command to be received.
unsigned char command_data_length = 0;
// The requested number of response bytes to be received (and transmitted) over
// SPI.
unsigned char response_data_length = 0;


/* Initialize the UART interface */
/* Sets the required bits to configure the UART interface for data transmission
 * and reception. See [1] Section 20 */
void usart_init(void);

/* Transmit data over UART */
/* Loops through the array of trasnmit data and transmits one byte at a time. */
void usart_transmit(unsigned char* transmit_data);

/* Initialize the SPI interface */
/* Sets the required bits to configure the SPI interface for data transmission 
 * and reception. See [1] Section 19 */
void spi_init(void);

/* Transfer data over SPI */
/* Simultaneously sends data from the master to the slave, and receives data
 * from the slave to the master. The function returns a pointer to the array of
 * received data. */
unsigned char* spi_transceive(unsigned char* transmit_data);



int main()
{
    usart_init();
    spi_init();
    sei();  // Global interrupt enable.
    while (1);

    return 0;
}



/* Initialize the USART */
void usart_init(void)
{
    // TODO Need to change this later to account for different CPU frequencies.
    // Set the baud prescaler. See Section 20.5 and 20.11.5
    UBRR0H = (unsigned char) (USART_BAUD_PRESCALER >> 8);
    UBRR0L = (unsigned char) USART_BAUD_PRESCALER;
    // Set the frame size of the receiver and transmitter to 8-bits. See
    // Table 20-11
    UCSR0C |= ((1 << UCSZ01) | (1 << UCSZ00));
    // Enable the interrupt for USART Receive Complete. See
    // Section 20.11.3-Bit 7
    UCSR0B |= (1 << RXCIE0);
    // Enable the transmitter and the rceiver. See Section 20.11.3.
    UCSR0B |= ((1 << TXEN0) | (1 << RXEN0));
}

/* Transmit data over UART. */
void usart_transmit(unsigned char* transmit_data)
{
    for (unsigned char i = 0; i < response_data_length; i++)
    {
        // Wait for the data register to empty. See Section 20.11.2 - Bit 5
        while (!(UCSR0A & (1 << UDRE0)));
        // Load the data into the data register to trigger its transmission.
        UDR0 = transmit_data[i];
    }
}


/* Initialize the SPI as master. */
void spi_init(void)
{
    // TODO: also add datasheet documentation for the NRF.
    // Set MOSI pin to be an output. See section 19.2 page 171
    // See Figure 1-1 for pinout
    DDRB |= (1 << DDB3);
    // Set CLK pin to be an output
    DDRB |= (1 << DDB5);
    // choose the slave select pin and set as an output. set the SS pin as an
    // output
    // NOTE: The slave select pin must be set and cleared manually as the spi
    // interface has no automatic control of the SS pin's functionality. See
    // Section 19.2
    DDRB |= (1 << DDB2);
    PORTB |= (1 << PORTB2); // Idle the SS pin high.
    // Set SPI as master
    SPCR |= (1 << MSTR);
    // Set data orded (this is redundant but good for visuals.) MSB -> LSB
    // SPCR &=~ (1 << DORD);
    // Set the clock polarity (redundant) low when idle
    // SPCR &=~ (1 << CPOL);
    // Set the clock phase (redundant) Leading: Sample; Trailing: Setup
    // SPCR &=~ (1 << CPHA);
    // set the clock speed. This doesn't matter a whole lot, but for reference,
    // the maximum speed of the nrf24l01 is 10Mbps See section 8.1 of the nrf,
    // and see table 19-5 of the atmega328p datasheet.
    // SPCR |= ((1 << SPR1) | (1 << SPR0)); // Configures the SPI for f_osc/4.
    // With double speed ^*2
    // SPSR |= (1 << SPI2X);
    // Configure interrupts as needed. NOTE: this may be needed in the future.
    // SPIF triggers when a transmission is completed.
    // SPCR |= (1 << SPIE);
    // Enable the SPI
    SPCR |= (1 << SPE);
}

/* Perform a data exchange over SPI */
unsigned char* spi_transceive(unsigned char* transmit_data)
{
    // Bring the Slave-Select pin LOW to initiate the transaction.
    PORTB &=~ (1 << PORTB2);
    // Send each segment of the command
    // NOTE: Some commands have a transaction length longer than the command
    // itself; tldr command_length <= response_data_length.
    for (unsigned char i = 0; i < response_data_length; i++)
    {
            // Write the segment of data to the transmit buffer to initiate the
            // transmission.
            SPDR = transmit_data[i];
            // Wait for the transmission to complete by waiting for the SPIF
            // (SPI transfer complete interrupt flag) to be set. See
            // [1] Section 19.5.2 Bit 7 (Page 117)
            while (!(SPSR & (1 << SPIF)));
            received_spi_data[i] = SPDR;    // Read from the receive buffer.
    }
    PORTB |= (1 << PORTB2); // Bring the SS pin high to end the transmission.

    return received_spi_data;
}


/* Interrupt service routine for USART_RX_vect */
/* i.e. code to execute on the reception of data over UART */
ISR (USART_RX_vect)
{
    // TODO: Need to add a way to handle the CE pin. The current plan is to add
    // an nRF24L01 control byte to be sent in the UART transmission header.
    // TODO: Need to add a trasnsmission timeout timer in case an issue occurs
    // during transmission.
    // Save the data from the USART receive buffer.
    unsigned char received_usart_data = UDR0;
    // The `0b00111111` bit mask is to ensure that the length data bits in the
    // byte are the only bits which are being examined.
    if (received_command_index == 0)    // Transmit data length header.
    {
        command_data_length = received_usart_data;// & 0b00111111;
        received_command_index++;
    }
    else if (received_command_index == 1)   // Response data length header.
    {
        response_data_length = received_usart_data;// & 0b00111111;
        received_command_index++;
    }
    else if (received_command_index > 1)    // Command data.
    {
        // Save the received command segment.
        received_command[received_command_index - 2] = received_usart_data;
        received_command_index++;
        // Check if the command has been fully received (Compare the number of
        // bytes received to the number of expected bytes).
        if (received_command_index == (command_data_length + 2))
        {
            // Send the command to the nRF24L01 and return its response over
            // UART.
            usart_transmit(spi_transceive(received_command));
            received_command_index = 0;
        }
    }
}
