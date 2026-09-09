#include <iostream>
#include <string>
#include <unordered_map>
#include <vector>
#include <fstream>
#include <sstream>
#include <stdexcept>
#include <functional>
#include <memory>

// Отладочный модуль
namespace Debug {
    bool enabled = true; // Включение/выключение отладочного вывода

    void log(const std::string& message) {
        if (enabled) {
            std::cerr << "[DEBUG]: " << message << std::endl;
        }
    }
}

struct File {
    std::string name;
    std::vector<int> blocks;
    std::string content;
};

struct Directory {
    std::string name;
    std::unordered_map<std::string, File> files;
    std::string path;
    std::unordered_map<std::string, std::unique_ptr<Directory>> subdirectories;
};

class FileSystem {
private:
    Directory root;
    Directory* currentDirectory;
    int blockSize;
    int totalBlocks;
    std::vector<bool> blockAvailability;

    int allocateBlock() {
        for (int i = 0; i < totalBlocks; ++i) {
            if (!blockAvailability[i]) {
                blockAvailability[i] = true;
                Debug::log("Block allocated: " + std::to_string(i));
                return i;
            }
        }
        throw std::runtime_error("No available blocks!");
    }

    void releaseBlock(int block) {
        if (block >= 0 && block < totalBlocks) {
            blockAvailability[block] = false;
            Debug::log("Block released: " + std::to_string(block));
        }
    }

    std::string getFilePath(const std::string& fileName) {
        std::string directoryPath = "."; // Используем текущую директорию
        std::string fullPath = directoryPath + "/" + fileName;
        Debug::log("Computed file path: " + fullPath);
        return fullPath;
    }

public:
    FileSystem(int totalBlocks, int blockSize)
        : totalBlocks(totalBlocks), blockSize(blockSize), currentDirectory(&root) {
        root.name = "/";
        root.path = ".";
        blockAvailability.resize(totalBlocks, false);
    }

void createFile(const std::string& fileName, const std::string& content) {
    Debug::log("Attempting to create file: " + fileName);
    if (currentDirectory->files.count(fileName)) {
        throw std::runtime_error("File already exists!");
    }

    File newFile;
    newFile.name = fileName;
    newFile.content = content;

    int requiredBlocks = (content.size() + blockSize - 1) / blockSize;
    for (int i = 0; i < requiredBlocks; ++i) {
        newFile.blocks.push_back(allocateBlock());
    }

    std::string filePath = getFilePath(fileName);
    std::ofstream fileStream(filePath);
    if (!fileStream.is_open()) {
        throw std::runtime_error("Failed to create file on disk! Path: " + filePath);
    }
    fileStream << content;
    fileStream.close();
    Debug::log("File created on disk: " + filePath);

    currentDirectory->files[fileName] = newFile; // Добавляем файл в текущую директорию
    Debug::log("File added to current directory: " + fileName);
}
void readFile(const std::string& fileName) {
    Debug::log("Attempting to read file: " + fileName);
    auto it = currentDirectory->files.find(fileName);
    if (it == currentDirectory->files.end()) {
        throw std::runtime_error("File not found in current directory!");
    }

    std::string filePath = getFilePath(fileName);
    std::ifstream fileStream(filePath);
    if (!fileStream.is_open()) {
        throw std::runtime_error("Failed to open file for reading! Path: " + filePath);
    }

    std::stringstream buffer;
    buffer << fileStream.rdbuf();
    std::cout << buffer.str() << std::endl;
    fileStream.close();
}
    void writeFile(const std::string& fileName, const std::string& content) {
        Debug::log("Attempting to write to file: " + fileName);
        auto it = currentDirectory->files.find(fileName);
        if (it == currentDirectory->files.end()) {
            throw std::runtime_error("File not found!");
        }

        it->second.content = content;
        std::string filePath = getFilePath(fileName);
        std::ofstream fileStream(filePath);
        if (!fileStream.is_open()) {
            throw std::runtime_error("Failed to open file for writing! Path: " + filePath);
        }
        fileStream << content;
        fileStream.close();
        Debug::log("File written: " + fileName);
    }

    void copyFile(const std::string& source, const std::string& destination) {
        Debug::log("Attempting to copy file: " + source + " to " + destination);
        auto it = currentDirectory->files.find(source);
        if (it == currentDirectory->files.end()) {
            throw std::runtime_error("Source file not found!");
        }

        if (currentDirectory->files.count(destination)) {
            throw std::runtime_error("Destination file already exists!");
        }

        createFile(destination, it->second.content);
        Debug::log("File copied: " + source + " to " + destination);
    }

    void moveFile(const std::string& fileName, const std::string& targetDirectoryName) {
        Debug::log("Attempting to move file: " + fileName + " to " + targetDirectoryName);
        auto fileIt = currentDirectory->files.find(fileName);
        if (fileIt == currentDirectory->files.end()) {
            throw std::runtime_error("File not found!");
        }

        auto dirIt = currentDirectory->subdirectories.find(targetDirectoryName);
        if (dirIt == currentDirectory->subdirectories.end()) {
            throw std::runtime_error("Target directory not found!");
        }

        dirIt->second->files[fileName] = std::move(fileIt->second);
        currentDirectory->files.erase(fileIt);
        Debug::log("File moved: " + fileName + " to " + targetDirectoryName);
    }

    void dumpFileSystem(const std::string& filename) {
        Debug::log("Attempting to dump file system to: " + filename);
        std::ofstream dumpFile(filename);
        if (!dumpFile.is_open()) {
            throw std::runtime_error("Failed to open dump file! Path: " + filename);
        }

        std::function<void(const Directory&, int)> dumpDirectory = [&](const Directory& dir, int indent) {
            for (const auto& subdir : dir.subdirectories) {
                dumpFile << std::string(indent, ' ') << "Directory: " << subdir.first << std::endl;
                dumpDirectory(*subdir.second, indent + 2);
            }
            for (const auto& file : dir.files) {
                dumpFile << std::string(indent, ' ') << "File: " << file.first << std::endl;
            }
        };

        dumpDirectory(root, 0);
        dumpFile.close();
        Debug::log("File system dumped to: " + filename);
    }

    void createDirectory(const std::string& dirName) {
        Debug::log("Attempting to create directory: " + dirName);
        if (currentDirectory->subdirectories.count(dirName)) {
            throw std::runtime_error("Directory already exists!");
        }

        auto newDir = std::make_unique<Directory>();
        newDir->name = dirName;
        newDir->path = currentDirectory->path + "/" + dirName;
        currentDirectory->subdirectories[dirName] = std::move(newDir);
        Debug::log("Directory '" + dirName + "' created successfully.");
    }

    void listDirectory() const {
        std::cout << "Current directory: " << currentDirectory->path << std::endl;
        std::cout << "Directories:" << std::endl;
        for (const auto& subdir : currentDirectory->subdirectories) {
            std::cout << "  " << subdir.first << std::endl;
        }
        std::cout << "Files:" << std::endl;
        for (const auto& file : currentDirectory->files) {
            std::cout << "  " << file.first << std::endl;
        }
    }
};

int main(int argc, char* argv[]) {
    Debug::enabled = true; // Включаем отладочный вывод
    FileSystem fs(100, 1024); // 100 блоков, каждый размером 1 KB

    if (argc < 2) {
        std::cerr << "Usage: ./filesystem <command> [args]" << std::endl;
        return 1;
    }

    std::string command = argv[1];
    try {
        if (command == "create") {
            if (argc != 4) {
                std::cerr << "Usage: ./filesystem create <filename> <content>" << std::endl;
                return 1;
            }
            fs.createFile(argv[2], argv[3]);
        } else if (command == "delete") {
            if (argc != 3) {
                std::cerr << "Usage: ./filesystem delete <filename>" << std::endl;
                return 1;
            }
            fs.deleteFile(argv[2]);
        } else if (command == "read") {
            if (argc != 3) {
                std::cerr << "Usage: ./filesystem read <filename>" << std::endl;
                return 1;
            }
            fs.readFile(argv[2]);
        } else if (command == "write") {
            if (argc != 4) {
                std::cerr << "Usage: ./filesystem write <filename> <content>" << std::endl;
                return 1;
            }
            fs.writeFile(argv[2], argv[3]);
        } else if (command == "copy") {
            if (argc != 4) {
                std::cerr << "Usage: ./filesystem copy <source> <destination>" << std::endl;
                return 1;
            }
            fs.copyFile(argv[2], argv[3]);
        } else if (command == "move") {
            if (argc != 4) {
                std::cerr << "Usage: ./filesystem move <filename> <target_directory>" << std::endl;
                return 1;
            }
            fs.moveFile(argv[2], argv[3]);
        } else if (command == "dump") {
            if (argc != 3) {
                std::cerr << "Usage: ./filesystem dump <filename>" << std::endl;
                return 1;
            }
            fs.dumpFileSystem(argv[2]);
        } else if (command == "mkdir") {
            if (argc != 3) {
                std::cerr << "Usage: ./filesystem mkdir <directory_name>" << std::endl;
                return 1;
            }
            fs.createDirectory(argv[2]);
        } else if (command == "ls") {
            fs.listDirectory();
        } else {
            std::cerr << "Unknown command: " << command << std::endl;
            return 1;
        }
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }

    return 0;
}