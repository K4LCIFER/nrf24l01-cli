
atmega328p:
	avr-gcc -mmcu=atmega328p ./interface-firmware/src/atmega328p/atmega328p.c \
        -o ./atmega328p-build.out
	avr-objcopy -O ihex ./atmega328p-build.out ./atmega328p-build.hex
	sudo avrdude -c atmelice_isp -p m328p -B 1 -U flash:w:./atmega328p-build.hex

clean:
	rm *.hex *.out
