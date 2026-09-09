#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <assert.h>
#include <time.h>

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

// Функция для инициализации менеджера памяти
void mm_init(MemoryManager *manager) {
    manager->head = NULL;
}

// Функция выделения памяти
void *mm_malloc(MemoryManager *manager, size_t size) {
    Block *current = manager->head;
    Block *prev = NULL;

    // Ищем первый свободный блок подходящего размера
    while (current != NULL) {
        if (current->is_free && current->size >= size) {
            current->is_free = false;  // Занимаем этот блок
            return current->ptr;
        }
        prev = current;
        current = current->next;
    }

    // Если не нашли подходящего блока, создаем новый
    Block *new_block = (Block *)malloc(sizeof(Block) + size);
    new_block->size = size;
    new_block->is_free = false;
    new_block->next = NULL;
    new_block->ptr = (void *)(new_block + 1);  // Указатель на начало данных после структуры блока

    if (prev == NULL) {
        manager->head = new_block;
    } else {
        prev->next = new_block;
    }

    return new_block->ptr;
}

// Функция освобождения памяти
void mm_free(MemoryManager *manager, void *ptr) {
    Block *current = manager->head;

    // Ищем блок по указателю
    while (current != NULL) {
        if (current->ptr == ptr) {
            current->is_free = true;  // Освобождаем блок
            return;
        }
        current = current->next;
    }

    printf("Ошибка: указатель не найден в менеджере памяти\n");
}

// Функция записи данных в блок памяти
void mm_write(MemoryManager *manager, void *ptr, size_t offset, void *data, size_t len) {
    Block *current = manager->head;

    // Ищем блок по указателю
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

// Функция чтения данных из блока памяти
void mm_read(MemoryManager *manager, void *ptr, size_t offset, void *buffer, size_t len) {
    Block *current = manager->head;

    // Ищем блок по указателю
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

// Юнит-тесты

void test_mm_malloc_free() {
    MemoryManager manager;
    mm_init(&manager);

    // Выделяем блок памяти
    void *ptr = mm_malloc(&manager, 100);
    assert(ptr != NULL);  // Проверяем, что память выделена

    // Освобождаем блок памяти
    mm_free(&manager, ptr);
}

void test_mm_read_write() {
    MemoryManager manager;
    mm_init(&manager);

    // Выделяем блок памяти
    void *ptr = mm_malloc(&manager, 100);

    // Записываем данные в память
    int data = 42;
    mm_write(&manager, ptr, 0, &data, sizeof(data));

    // Читаем данные из памяти
    int read_data = 0;
    mm_read(&manager, ptr, 0, &read_data, sizeof(read_data));

    // Проверяем, что данные совпадают
    assert(read_data == data);

    // Освобождаем память
    mm_free(&manager, ptr);
}

// Эксперимент для измерения производительности

void experiment() {
    MemoryManager manager;
    mm_init(&manager);

    size_t block_size = 1024;  // 1 KB
    size_t num_blocks = 1000;  // 1000 блоков

    clock_t start, end;

    // Измеряем время выделения памяти
    start = clock();
    for (size_t i = 0; i < num_blocks; i++) {
        mm_malloc(&manager, block_size);
    }
    end = clock();
    printf("Время выделения %zu блоков памяти: %lf секунд\n", num_blocks, ((double)(end - start)) / CLOCKS_PER_SEC);

    // Измеряем время освобождения памяти
    start = clock();
    Block *current = manager.head;
    while (current != NULL) {
        mm_free(&manager, current->ptr);
        current = current->next;
    }
    end = clock();
    printf("Время освобождения %zu блоков памяти: %lf секунд\n", num_blocks, ((double)(end - start)) / CLOCKS_PER_SEC);
}

// Главная функция
int main() {
    // Юнит-тесты
    test_mm_malloc_free();
    test_mm_read_write();
    printf("Тесты пройдены успешно.\n");

    // Эксперимент
    experiment();

    return 0;
}
