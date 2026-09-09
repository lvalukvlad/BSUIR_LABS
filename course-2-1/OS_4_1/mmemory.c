#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <assert.h>
#include <time.h>
#include "mmemory.h"

void mm_init(MemoryManager *manager) {
    manager->head = NULL;
}

void *mm_malloc(MemoryManager *manager, size_t size) {
    Block *current = manager->head;
    Block *prev = NULL;

    while (current != NULL) {
        if (current->is_free && current->size >= size) {
            current->is_free = false;
            return current->ptr;
        }
        prev = current;
        current = current->next;
    }

    Block *new_block = (Block *)malloc(sizeof(Block) + size);
    new_block->size = size;
    new_block->is_free = false;
    new_block->next = NULL;
    new_block->ptr = (void *)(new_block + 1);

    if (prev == NULL) {
        manager->head = new_block;
    } else {
        prev->next = new_block;
    }

    return new_block->ptr;
}

void mm_free(MemoryManager *manager, void *ptr) {
    Block *current = manager->head;

    while (current != NULL) {
        if (current->ptr == ptr) {
            current->is_free = true;
            return;
        }
        current = current->next;
    }

    printf("Ошибка: указатель не найден в менеджере памяти\n");
}

void mm_write(MemoryManager *manager, void *ptr, size_t offset, void *data, size_t len) {
    Block *current = manager->head;

    while (current != NULL) {
        if (current->ptr == ptr) {
            if (offset + len <= current->size) {
                memcpy((char *)current->ptr + offset, data, len);
                return;
            } else {
                printf("Ошибка: выход за пределы блока памяти\n");
                return;
            }
        }
        current = current->next;
    }

    printf("Ошибка: указатель не найден в менеджере памяти\n");
}

void mm_read(MemoryManager *manager, void *ptr, size_t offset, void *buffer, size_t len) {
    Block *current = manager->head;

    while (current != NULL) {
        if (current->ptr == ptr) {
            if (offset + len <= current->size) {
                memcpy(buffer, (char *)current->ptr + offset, len);
                return;
            } else {
                printf("Ошибка: выход за пределы блока памяти\n");
                return;
            }
        }
        current = current->next;
    }

    printf("Ошибка: указатель не найден в менеджере памяти\n");
}


void test_mm_malloc_free() {
    MemoryManager manager;
    mm_init(&manager);

    void *ptr = mm_malloc(&manager, 100);
    assert(ptr != NULL);

    mm_free(&manager, ptr);
}

void test_mm_read_write() {
    MemoryManager manager;
    mm_init(&manager);

    void *ptr = mm_malloc(&manager, 100);

    int data = 42;
    mm_write(&manager, ptr, 0, &data, sizeof(data));

    int read_data = 0;
    mm_read(&manager, ptr, 0, &read_data, sizeof(read_data));

    assert(read_data == data);

    mm_free(&manager, ptr);
}

void experiment_fragmentation() {
    MemoryManager manager;
    mm_init(&manager);

    size_t block_size = 1024;
    size_t num_blocks = 1000;

    for (size_t i = 0; i < num_blocks; i++) {
        mm_malloc(&manager, block_size);
    }

    srand(time(NULL));
    for (size_t i = 0; i < num_blocks / 2; i++) {
        size_t block_to_free = rand() % num_blocks;
        Block *current = manager.head;
        size_t count = 0;
        while (current != NULL && count < block_to_free) {
            current = current->next;
            count++;
        }
        mm_free(&manager, current->ptr);
    }

    clock_t start, end;
    start = clock();
    for (size_t i = 0; i < num_blocks / 2; i++) {
        mm_malloc(&manager, block_size);
    }
    end = clock();
    double allocation_time = ((double)(end - start)) / CLOCKS_PER_SEC;

    FILE *file = fopen("fragmentation_results.txt", "a");
    fprintf(file, "%lf\n", allocation_time);
    fclose(file);

    printf("Время выделения памяти после фрагментации: %lf секунд\n", allocation_time);
}

void test_repeated_allocations() {
    MemoryManager manager;
    mm_init(&manager);

    size_t block_size = 512;
    size_t num_blocks = 1000;

    clock_t start, end;
    double allocation_time = 0.0;
    double free_time = 0.0;

    for (size_t iteration = 0; iteration < 10; iteration++) {
        start = clock();
        for (size_t i = 0; i < num_blocks; i++) {
            mm_malloc(&manager, block_size);
        }
        end = clock();
        allocation_time += ((double)(end - start)) / CLOCKS_PER_SEC;

        start = clock();
        Block *current = manager.head;
        while (current != NULL) {
            mm_free(&manager, current->ptr);
            current = current->next;
        }
        end = clock();
        free_time += ((double)(end - start)) / CLOCKS_PER_SEC;
    }

    FILE *file = fopen("repeated_allocations_results.txt", "a");
    fprintf(file, "Среднее время выделения: %lf секунд\n", allocation_time / 10);
    fprintf(file, "Среднее время освобождения: %lf секунд\n", free_time / 10);
    fclose(file);

    printf("Многократное выделение/освобождение (10 итераций):\n");
    printf("Среднее время выделения: %lf секунд\n", allocation_time / 10);
    printf("Среднее время освобождения: %lf секунд\n", free_time / 10);
}

void test_various_block_sizes() {
    MemoryManager manager;
    mm_init(&manager);

    size_t block_sizes[] = {128, 256, 512, 1024, 2048, 4096};
    size_t num_blocks = 500;

    printf("=== Результаты тестирования различных размеров блоков ===\n");

    FILE *file = fopen("various_block_sizes_results.txt", "a");

    for (size_t i = 0; i < sizeof(block_sizes) / sizeof(block_sizes[0]); i++) {
        size_t block_size = block_sizes[i];

        clock_t start, end;
        start = clock();
        for (size_t j = 0; j < num_blocks; j++) {
            mm_malloc(&manager, block_size);
        }
        end = clock();
        double allocation_time = ((double)(end - start)) / CLOCKS_PER_SEC;

        printf("Размер блока: %-5zu | Время выделения: %-10.6lf сек\n", block_size, allocation_time);
        fprintf(file, "Размер блока: %-5zu | Время выделения: %-10.6lf сек\n", block_size, allocation_time);
    }

    fclose(file);
    printf("=========================================================\n");
}

int main() {
    test_mm_malloc_free();
    test_mm_read_write();
    printf("Тесты пройдены успешно.\n");

    experiment_fragmentation();
    test_repeated_allocations();
    test_various_block_sizes();

    return 0;
}