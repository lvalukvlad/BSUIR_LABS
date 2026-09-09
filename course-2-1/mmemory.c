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

void experiment_num_blocks() {
    MemoryManager manager;
    mm_init(&manager);

    size_t block_size = 1024;  // 1 KB
    size_t num_blocks_start = 100;  // Начальное количество блоков
    size_t num_blocks_end = 10000;  // Конечное количество блоков
    size_t step = 100;  // Шаг увеличения числа блоков

    // Измеряем время выделения
    printf("Эксперимент 1: Влияние числа блоков на время выделения и освобождения памяти\n");
    printf("Количество блоков | Время выделения (сек) | Время освобождения (сек)\n");

    for (size_t num_blocks = num_blocks_start; num_blocks <= num_blocks_end; num_blocks += step) {
        clock_t start, end;

        // Время выделения памяти
        start = clock();
        for (size_t i = 0; i < num_blocks; i++) {
            mm_malloc(&manager, block_size);
        }
        end = clock();
        double allocation_time = ((double)(end - start)) / CLOCKS_PER_SEC;

        // Время освобождения памяти
        start = clock();
        Block *current = manager.head;
        while (current != NULL) {
            mm_free(&manager, current->ptr);
            current = current->next;
        }
        end = clock();
        double free_time = ((double)(end - start)) / CLOCKS_PER_SEC;

        // Выводим данные для каждого 100-го блока и для первого и последнего значения
        if (num_blocks == num_blocks_start || num_blocks == num_blocks_end || num_blocks % 100 == 0) {
            printf("%zu | %lf | %lf\n", num_blocks, allocation_time, free_time);
        }
    }
}

void experiment_block_size() {
    MemoryManager manager;
    mm_init(&manager);

    size_t num_blocks = 1000;  // Количество блоков
    size_t block_size_start = 128;  // Начальный размер блока
    size_t block_size_end = 10240;  // Конечный размер блока (10 КБ)
    size_t step = 128;  // Шаг увеличения размера блока

    // Измеряем время выделения
    printf("Эксперимент 2: Влияние размера блока на время выделения и освобождения памяти\n");
    printf("Размер блока | Время выделения (сек) | Время освобождения (сек)\n");

    for (size_t block_size = block_size_start; block_size <= block_size_end; block_size += step) {
        clock_t start, end;

        // Время выделения памяти
        start = clock();
        for (size_t i = 0; i < num_blocks; i++) {
            mm_malloc(&manager, block_size);
        }
        end = clock();
        double allocation_time = ((double)(end - start)) / CLOCKS_PER_SEC;

        // Время освобождения памяти
        start = clock();
        Block *current = manager.head;
        while (current != NULL) {
            mm_free(&manager, current->ptr);
            current = current->next;
        }
        end = clock();
        double free_time = ((double)(end - start)) / CLOCKS_PER_SEC;

        // Выводим данные для каждого 128-го блока и для первого и последнего значения
        if (block_size == block_size_start || block_size == block_size_end || block_size % 128 == 0) {
            printf("%zu | %lf | %lf\n", block_size, allocation_time, free_time);
        }
    }
}


void experiment_fragmentation() {
    MemoryManager manager;
    mm_init(&manager);

    size_t block_size = 1024;  // 1 KB
    size_t num_blocks = 1000;  // Количество блоков

    // Выделяем память
    for (size_t i = 0; i < num_blocks; i++) {
        mm_malloc(&manager, block_size);
    }

    // Освобождаем блоки случайным образом
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

    // Измеряем время выделения после фрагментации
    clock_t start, end;
    start = clock();
    for (size_t i = 0; i < num_blocks / 2; i++) {
        mm_malloc(&manager, block_size);
    }
    end = clock();
    double allocation_time = ((double)(end - start)) / CLOCKS_PER_SEC;

    printf("Время выделения памяти после фрагментации: %lf секунд\n", allocation_time);
}


void test_repeated_allocations() {
    MemoryManager manager;
    mm_init(&manager);

    size_t block_size = 512;  // 512 байт
    size_t num_blocks = 1000;  // Количество блоков

    clock_t start, end;
    double allocation_time = 0.0;
    double free_time = 0.0;

    // Многократное выделение и освобождение
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

    printf("Многократное выделение/освобождение (10 итераций):\n");
    printf("Среднее время выделения: %lf секунд\n", allocation_time / 10);
    printf("Среднее время освобождения: %lf секунд\n", free_time / 10);
}

void test_various_block_sizes() {
    MemoryManager manager;
    mm_init(&manager);

    size_t block_sizes[] = {128, 256, 512, 1024, 2048, 4096};
    size_t num_blocks = 500;

    for (size_t i = 0; i < sizeof(block_sizes) / sizeof(block_sizes[0]); i++) {
        size_t block_size = block_sizes[i];

        clock_t start, end;
        start = clock();
        for (size_t j = 0; j < num_blocks; j++) {
            mm_malloc(&manager, block_size);
        }
        end = clock();
        double allocation_time = ((double)(end - start)) / CLOCKS_PER_SEC;

        printf("Время выделения для блока размером %zu: %lf секунд\n", block_size, allocation_time);
    }
}

// Главная функция
int main() {
    // Юнит-тесты
    test_mm_malloc_free();
    test_mm_read_write();
    printf("Тесты пройдены успешно.\n");

    // Эксперимент
    experiment_num_blocks();
    experiment_fragmentation();
    experiment_block_size();
    test_repeated_allocations();
    test_various_block_sizes();
    

    return 0;
}

