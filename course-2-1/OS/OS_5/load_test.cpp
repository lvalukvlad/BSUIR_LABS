#include <iostream>
#include <chrono>
#include <cstdlib>
#include <string>
#include <sstream>

void executeCommand(const std::string& command) {
    int result = system(command.c_str());
    if (result != 0) {
        std::cerr << "Command failed: " << command << " (Error code: " << result << ")" << std::endl;
    }
}

void testCreateFiles(int numFiles) {
    auto start = std::chrono::high_resolution_clock::now();
    for (int i = 0; i < numFiles; ++i) {
        std::ostringstream fileName;
        fileName << "file" << i;
        executeCommand("./filesystem create " + fileName.str() + " \"\"");
    }
    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> elapsed = end - start;
    std::cout << "Time to create " << numFiles << " files: " << elapsed.count() << " seconds" << std::endl;
}

void testDeepDirectories(int depth) {
    auto start = std::chrono::high_resolution_clock::now();
    std::string currentPath = ".";
    for (int i = 0; i < depth; ++i) {
        std::ostringstream dirName;
        dirName << "dir" << i;
        currentPath += "/" + dirName.str();
        executeCommand("mkdir " + currentPath);
    }
    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> elapsed = end - start;
    std::cout << "Time to create " << depth << " nested directories: " << elapsed.count() << " seconds" << std::endl;
}

void testLargeFiles(int fileSizeKB) {
    auto start = std::chrono::high_resolution_clock::now();
    std::ostringstream fileName;
    fileName << "large_file";
    std::string command = "dd if=/dev/zero of=" + fileName.str() + " bs=1K count=" + std::to_string(fileSizeKB);
    executeCommand(command);
    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> elapsed = end - start;
    std::cout << "Time to create a file of size " << fileSizeKB << " KB: " << elapsed.count() << " seconds" << std::endl;
}

void deleteFiles(int numFiles) {
    for (int i = 0; i < numFiles; ++i) {
        std::ostringstream fileName;
        fileName << "file" << i;
        executeCommand("rm " + fileName.str());
    }
}

void deleteDirectories(int depth) {
    std::string currentPath = ".";
    for (int i = 0; i < depth; ++i) {
        std::ostringstream dirName;
        dirName << "dir" << i;
        currentPath += "/" + dirName.str();
    }
    for (int i = depth - 1; i >= 0; --i) {
        std::ostringstream dirName;
        dirName << "dir" << i;
        executeCommand("rmdir " + currentPath);
        size_t pos = currentPath.find_last_of('/');
        if (pos != std::string::npos) {
            currentPath = currentPath.substr(0, pos);
        }
    }
}

void deleteLargeFile() {
    executeCommand("rm large_file");
}

int main() {
    std::cout << "Starting load tests..." << std::endl;

    // Тест 1: Создание множества файлов
    testCreateFiles(1000); // Создать 1000 файлов

    // Тест 2: Вложенные директории
    testDeepDirectories(100); // Вложенность 100 уровней

    // Тест 3: Большие файлы
    testLargeFiles(1024); // Создать файл размером 1 MB

    std::cout << "Load tests completed." << std::endl;

    std::cout << "Starting cleanup..." << std::endl;

    // Удаление созданных файлов
    deleteFiles(1000);

    // Удаление созданных директорий
    deleteDirectories(100);

    // Удаление большого файла
    deleteLargeFile();

    std::cout << "Cleanup completed." << std::endl;

    return 0;
}