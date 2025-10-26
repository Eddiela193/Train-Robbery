#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <fcntl.h>
#include <errno.h>

#define PORT 103
#define BUFFER_SIZE 512
#define TOTAL_KEYS 5
#define REQUIRED_KEYS 3

int main() {
    int server_fd, client_fd;
    struct sockaddr_in address;
    int addrlen = sizeof(address);
    char buffer[BUFFER_SIZE];

    int keys[TOTAL_KEYS] = {2168, 7018, 303, 404, 505};

    // Create socket
    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) == 0) {
        perror("Socket failed");
        exit(EXIT_FAILURE);
    }

    int opt = 1;
    setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(PORT);

    if (bind(server_fd, (struct sockaddr *)&address, sizeof(address)) < 0) {
        perror("Bind failed");
        close(server_fd);
        exit(EXIT_FAILURE);
    }

    if (listen(server_fd, 3) < 0) {
        perror("Listen failed");
        close(server_fd);
        exit(EXIT_FAILURE);
    }

    printf("Listening on port %d...\n", PORT);

    while (1) {
        printf("Waiting for client...\n");
        client_fd = accept(server_fd, (struct sockaddr*)&address, (socklen_t*)&addrlen);
        if (client_fd < 0) {
            perror("accept");
            continue;
        }
        printf("Client connected!\n");

        snprintf(buffer, sizeof(buffer), 
            "Welcome to the Vault! Enter 3 keys separated by spaces:\n");
        send(client_fd, buffer, strlen(buffer), 0);

        ssize_t valread = read(client_fd, buffer, sizeof(buffer)-1);
        if (valread <= 0) {
            close(client_fd);
            continue;
        }
        buffer[valread] = '\0';

        int inputKeys[REQUIRED_KEYS];
        int valid = 1;

        if (sscanf(buffer, "%d %d %d", &inputKeys[0], &inputKeys[1], &inputKeys[2]) != REQUIRED_KEYS)
            valid = 0;

        // verify keys exist
        for (int i = 0; i < REQUIRED_KEYS && valid; i++) {
            int found = 0;
            for (int j = 0; j < TOTAL_KEYS; j++) {
                if (inputKeys[i] == keys[j]) {
                    found = 1;
                    break;
                }
            }
            if (!found) valid = 0;
        }

        // ensure distinct
        for (int i = 0; i < REQUIRED_KEYS && valid; i++) {
            for (int j = i+1; j < REQUIRED_KEYS; j++) {
                if (inputKeys[i] == inputKeys[j])
                    valid = 0;
            }
        }

        if (valid) {
            snprintf(buffer, sizeof(buffer), "Congratulations! Unlocking GOLD...\n");
            send(client_fd, buffer, strlen(buffer), 0);

            // ---- Run gold.py and stream its output ----
            int pipefd[2];
            if (pipe(pipefd) == 0) {
                pid_t pid = fork();
                if (pid == 0) {
                    // Child: redirect stdout -> pipe write end
                    close(pipefd[0]);
                    dup2(pipefd[1], STDOUT_FILENO);
                    dup2(pipefd[1], STDERR_FILENO);
                    close(pipefd[1]);
                    execlp("python3", "python3", "gold.py", (char *)NULL);
                    perror("execlp");
                    _exit(127);
                } else if (pid > 0) {
                    close(pipefd[1]);
                    char buf[1024];
                    ssize_t r;
                    while ((r = read(pipefd[0], buf, sizeof(buf))) > 0) {
                        send(client_fd, buf, r, 0);
                    }
                    close(pipefd[0]);
                    waitpid(pid, NULL, 0);
                }
            } else {
                perror("pipe");
            }

        } else {
            snprintf(buffer, sizeof(buffer), 
                "Invalid selection. Keys must exist and be distinct.\n");
            send(client_fd, buffer, strlen(buffer), 0);
        }

        close(client_fd);
        break; // optional: stop after one client
    }

    close(server_fd);
    return 0;
}
