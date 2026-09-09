# Makefile для компиляции программы Memory Manager

# Переменные
CC = gcc
CFLAGS = -Wall -Wextra -std=c99
TARGET = memory_manager

# Источники и объектные файлы
SOURCES = mmemory.c
OBJECTS = $(SOURCES:.c=.o)

# Правила
all: $(TARGET)

# Линковка исполнимого файла
$(TARGET): $(OBJECTS)
	$(CC) $(CFLAGS) -o $(TARGET) $(OBJECTS)

# Компиляция исходных файлов в объектные файлы
%.o: %.c mmemory.h
	$(CC) $(CFLAGS) -c $< -o $@

# Удаление временных файлов
clean:
	rm -f $(TARGET) $(OBJECTS)

# Запуск программы
run: $(TARGET)
	./$(TARGET)
