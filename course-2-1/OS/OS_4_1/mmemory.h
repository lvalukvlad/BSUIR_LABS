#ifndef MMEMORY_H
#define MMEMORY_H

#include <stdlib.h>
#include <stdbool.h>
#include <string.h>

typedef struct Block {
    size_t size;
    bool is_free;
    struct Block *next;
    void *ptr;
} Block;

typedef struct MemoryManager {
    Block *head;
} MemoryManager;

void mm_init(MemoryManager *manager);
void *mm_malloc(MemoryManager *manager, size_t size);
void mm_free(MemoryManager *manager, void *ptr);
void mm_write(MemoryManager *manager, void *ptr, size_t offset, void *data, size_t len);
void mm_read(MemoryManager *manager, void *ptr, size_t offset, void *buffer, size_t len);

#endif // MMEMORY_H
