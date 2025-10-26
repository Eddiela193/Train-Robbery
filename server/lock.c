#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>

#define PORT 106
#define BUFFER_SIZE 512
#define TOTAL_KEYS 5
#define REQUIRED_KEYS 3

int main() {
    int server_fd, client_fd;
    struct sockaddr_in address;
    int addrlen = sizeof(address);
    char buffer[BUFFER_SIZE];

    int keys[TOTAL_KEYS] = {2168, 202, 303, 404, 505}; // predefined keys

    // Create socket
    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) == 0) {
        perror("Socket failed");
        exit(EXIT_FAILURE);
    }

    // Bind
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(PORT);

    int opt = 1;
    if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt)) < 0) {
        perror("setsockopt");
        close(server_fd);
        exit(EXIT_FAILURE);
    }

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

        // Send greeting and available keys
        snprintf(buffer, sizeof(buffer), "Welcome to the Vault. enter your keys in any order to unlock.\n");
        send(client_fd, buffer, strlen(buffer), 0);

        ssize_t valread = read(client_fd, buffer, sizeof(buffer)-1);
        if (valread <= 0) {
            close(client_fd);
            continue;
        }
        buffer[valread] = '\0';

        int inputKeys[REQUIRED_KEYS];
        int valid = 1;

        // Parse three integers from the input
        if (sscanf(buffer, "%d %d %d", &inputKeys[0], &inputKeys[1], &inputKeys[2]) != REQUIRED_KEYS) {
            valid = 0;
        }

        // Check that all keys exist in the predefined list
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

        // Check that all keys are distinct
        for (int i = 0; i < REQUIRED_KEYS && valid; i++) {
            for (int j = i+1; j < REQUIRED_KEYS; j++) {
                if (inputKeys[i] == inputKeys[j]) {
                    valid = 0;
                }
            }
        }

        // Respond to client
        if (valid) {
            snprintf(buffer, sizeof(buffer), "Congratulations! GOLD GOLD GOLD GOLD GOLD GOLD GOLD GOLD GOLD GOLD!\n");
        } else {
            snprintf(buffer, sizeof(buffer), "Invalid selection. Keys must exist and be distinct.\n");
        }
        send(client_fd, buffer, strlen(buffer), 0);

        close(client_fd);
    }

    close(server_fd);
    return 0;
}
