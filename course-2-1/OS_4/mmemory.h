#ifndef MMEMORY_H
#define MMEMORY_H

#include <stdlib.h>
#include <stdbool.h>
#include <string.h>

// Структура для блока памяти
typedef struct Block {
    size_t size;            // Размер блока
    bool is_free;           // Статус: свободен или занят
    struct Block *next;     // Указатель на следующий блок
    void *ptr;              // Указатель на начало блока памяти
} Block;

// Структура менеджера памяти
typedef struct MemoryManager {
    Block *head;            // Голова списка блоков памяти
} MemoryManager;

// Функции менеджера памяти
void mm_init(MemoryManager *manager);
void *mm_malloc(MemoryManager *manager, size_t size);
void mm_free(MemoryManager *manager, void *ptr);
void mm_write(MemoryManager *manager, void *ptr, size_t offset, void *data, size_t len);
void mm_read(MemoryManager *manager, void *ptr, size_t offset, void *buffer, size_t len);

#endif // MMEMORY_H
