# Makefile для компиляции программы Memory Manager

CC = gcc
CFLAGS = -Wall -Wextra -std=c99
TARGET = memory_manager

SOURCES = mmemory.c
OBJECTS = $(SOURCES:.c=.o)

all: $(TARGET)

$(TARGET): $(OBJECTS)
	$(CC) $(CFLAGS) -o $(TARGET) $(OBJECTS)

%.o: %.c mmemory.h
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(TARGET) $(OBJECTS) fragmentation_results.txt repeated_allocations_results.txt various_block_sizes_results.txt

run: $(TARGET)
	./$(TARGET)