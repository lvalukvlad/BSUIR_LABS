#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/ipc.h>
#include <sys/shm.h>
#include <sys/sem.h>
#include <unistd.h>
#include <sys/wait.h>
#include <errno.h>

#define SHM_SIZE 1024 // Размер общей памяти
#define SEM_READ 0    // Семафор для чтения
#define SEM_WRITE 1   // Семафор для записи

// Функция для работы с семафорами
void sem_op(int semid, int semnum, int op) {
    struct sembuf sb;
    sb.sem_num = semnum;
    sb.sem_op = op;
    sb.sem_flg = 0;
    if (semop(semid, &sb, 1) == -1) {
        perror("semop");
        exit(1);
    }
}

int main(int argc, char *argv[]) {
    if (argc != 3) {
        fprintf(stderr, "Usage: %s <source_file> <dest_file>\n", argv[0]);
        exit(1);
    }

    const char *source_file = argv[1];
    const char *dest_file = argv[2];

    // Создание общей памяти
    int shmid = shmget(IPC_PRIVATE, SHM_SIZE, IPC_CREAT | 0666);
    if (shmid == -1) {
        perror("shmget");
        exit(1);
    }

    // Подключение к общей памяти
    char *shm_addr = (char *)shmat(shmid, NULL, 0);
    if (shm_addr == (char *)-1) {
        perror("shmat");
        exit(1);
    }

    // Создание семафоров
    int semid = semget(IPC_PRIVATE, 2, IPC_CREAT | 0666);
    if (semid == -1) {
        perror("semget");
        exit(1);
    }

    // Инициализация семафоров
    semctl(semid, SEM_READ, SETVAL, 0);  // Блокируем чтение
    semctl(semid, SEM_WRITE, SETVAL, 1); // Разрешаем запись

    // Создание дочерних процессов
    pid_t reader_pid = fork();
    if (reader_pid == -1) {
        perror("fork");
        exit(1);
    }

    if (reader_pid == 0) { // Читающий процесс
        FILE *source = fopen(source_file, "r");
        if (!source) {
            perror("fopen (reader)");
            exit(1);
        }

        while (1) {
            sem_op(semid, SEM_WRITE, -1); // Ждем разрешения на запись

            // Чтение данных из файла
            size_t bytes_read = fread(shm_addr, 1, SHM_SIZE, source);
            if (bytes_read == 0) { 
                if (ferror(source)) { // Проверка на ошибку чтения
                    perror("fread");
                    fclose(source);
                    exit(1);
                }
                shm_addr[0] = '\0'; // Помечаем конец данных
                sem_op(semid, SEM_READ, 1); // Разрешаем чтение
                break;
            }

            sem_op(semid, SEM_READ, 1); // Разрешаем чтение
        }

        fclose(source);
        exit(0);
    }

    pid_t writer_pid = fork();
    if (writer_pid == -1) {
        perror("fork");
        exit(1);
    }

    if (writer_pid == 0) { // Записывающий процесс
        FILE *dest = fopen(dest_file, "w");
        if (!dest) {
            perror("fopen (writer)");
            exit(1);
        }

        while (1) {
            sem_op(semid, SEM_READ, -1); // Ждем разрешения на чтение

            if (shm_addr[0] == '\0') { // Конец данных
                sem_op(semid, SEM_WRITE, 1); // Разрешаем запись
                break;
            }

            // Запись данных в файл
            if (fwrite(shm_addr, 1, strlen(shm_addr), dest) < strlen(shm_addr)) {
                perror("fwrite");
                fclose(dest);
                exit(1);
            }

            sem_op(semid, SEM_WRITE, 1); // Разрешаем запись
        }

        fclose(dest);
        exit(0);
    }

    // Родительский процесс
    int status;
    waitpid(reader_pid, &status, 0); // Ждем завершения читающего процесса
    if (WIFEXITED(status) && WEXITSTATUS(status) != 0) {
        fprintf(stderr, "Reader process failed\n");
        kill(writer_pid, SIGKILL); // Завершаем пишущий процесс
        exit(1);
    }

    waitpid(writer_pid, &status, 0); // Ждем завершения пишущего процесса
    if (WIFEXITED(status) && WEXITSTATUS(status) != 0) {
        fprintf(stderr, "Writer process failed\n");
        exit(1);
    }

    // Освобождение ресурсов
    shmdt(shm_addr);
    shmctl(shmid, IPC_RMID, NULL);
    semctl(semid, 0, IPC_RMID);

    printf("File copied successfully.\n");
    return 0;
}
