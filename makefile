CC=/home/kmarcus2/Tools/toolchain/android/lib/bin/arm-linux-androideabi-gcc
#CC=gcc

objects = power_measurement_log socket_measurement_log event_read_log

all: $(objects)

$(objects): *.c
	$(CC) $@.c -o $@.x

clean:
	rm *.x
