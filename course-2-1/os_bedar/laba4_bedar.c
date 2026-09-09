#include <iostream>
#include <vector>
#include <map>
#include <stdexcept>
#include <cstring> // Для memcpy

class MemoryManager {
private:
    size_t totalMemory;
    size_t usedMemory;
    std::map<void*, size_t> allocatedBlocks; // Адрес блока -> размер блока
    std::vector<std::pair<void*, size_t>> freeBlocks; // Адрес блока -> размер блока

public:
    explicit MemoryManager(size_t memorySize) : totalMemory(memorySize), usedMemory(0) {
        // Изначально вся память свободна
        void* base = malloc(memorySize);
        if (!base) {
            throw std::runtime_error("Ошибка инициализации памяти");
        }
        freeBlocks.emplace_back(base, memorySize);
    }

    ~MemoryManager() {
        // Освобождение всей выделенной памяти
        for (auto& block : freeBlocks) {
            free(block.first);
        }
        for (auto& block : allocatedBlocks) {
            free(block.first);
        }
    }

    // Выделение блока памяти
    void* allocate(size_t size) {
        for (auto it = freeBlocks.begin(); it != freeBlocks.end(); ++it) {
            if (it->second >= size) {
                void* block = it->first;
                size_t remaining = it->second - size;

                // Удаляем текущий свободный блок
                freeBlocks.erase(it);

                // Если осталась свободная память, добавляем её обратно
                if (remaining > 0) {
                    void* remainingBlock = static_cast<char*>(block) + size;
                    freeBlocks.emplace_back(remainingBlock, remaining);
                }

                allocatedBlocks[block] = size;
                usedMemory += size;
                return block;
            }
        }

        throw std::runtime_error("Недостаточно памяти для выделения блока");
    }

    // Удаление блока памяти
    void deallocate(void* block) {
        auto it = allocatedBlocks.find(block);
        if (it == allocatedBlocks.end()) {
            throw std::runtime_error("Блок не найден или не был выделен");
        }

        size_t size = it->second;
        allocatedBlocks.erase(it);
        usedMemory -= size;

        // Добавляем освободившийся блок в список свободных
        freeBlocks.emplace_back(block, size);
    }

    // Запись данных в блок памяти
    void write(void* block, const void* data, size_t size) {
        auto it = allocatedBlocks.find(block);
        if (it == allocatedBlocks.end()) {
            throw std::runtime_error("Блок не найден или не был выделен");
        }

        if (size > it->second) {
            throw std::runtime_error("Размер данных превышает размер блока");
        }

        memcpy(block, data, size);
    }

    // Чтение данных из блока памяти
    void read(void* block, void* buffer, size_t size) {
        auto it = allocatedBlocks.find(block);
        if (it == allocatedBlocks.end()) {
            throw std::runtime_error("Блок не найден или не был выделен");
        }

        if (size > it->second) {
            throw std::runtime_error("Размер данных превышает размер блока");
        }

        memcpy(buffer, block, size);
    }

    // Отображение состояния памяти
    void printStatus() const {
        std::cout << "Общая память: " << totalMemory << " байт\n";
        std::cout << "Используемая память: " << usedMemory << " байт\n";
        std::cout << "Свободные блоки: " << freeBlocks.size() << "\n";
        for (const auto& block : freeBlocks) {
            std::cout << "  Адрес: " << block.first << ", Размер: " << block.second << " байт\n";
        }
        std::cout << "Выделенные блоки: " << allocatedBlocks.size() << "\n";
        for (const auto& block : allocatedBlocks) {
            std::cout << "  Адрес: " << block.first << ", Размер: " << block.second << " байт\n";
        }
    }
};

int main() {
    try {
        MemoryManager manager(1024); // Инициализация с 1024 байтами памяти

        // Выделение блоков
        void* block1 = manager.allocate(128);
        void* block2 = manager.allocate(256);
        // Запись данных
        std::string data = "Пример данных";
        manager.write(block1, data.c_str(), data.size() + 1);

        // Чтение данных
        char buffer[128];
        manager.read(block1, buffer, data.size() + 1);
        std::cout << "Прочитанные данные: " << buffer << "\n";

        // Удаление блока
        manager.deallocate(block1);
        manager.deallocate(block2);

        // Состояние памяти
        manager.printStatus();
    } catch (const std::exception& e) {
        std::cerr << "Ошибка: " << e.what() << "\n";
    }

    return 0;
}
