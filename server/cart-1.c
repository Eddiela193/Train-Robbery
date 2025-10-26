#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>

#define PORT 101
#define BUFFER_SIZE 380

int main() {
    int server_fd, client_fd;
    struct sockaddr_in address;
    int addrlen = sizeof(address);
    char buffer[BUFFER_SIZE];

    // Create socket
    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) == 0) {
        perror("Socket failed");
        exit(EXIT_FAILURE);
    }

    // Bind to port 100
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

    // Listen for connections
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

        ssize_t valread = read(client_fd, buffer, BUFFER_SIZE);
        if (valread <= 0) {
            close(client_fd);
            continue;
        }

        if (valread == BUFFER_SIZE) {
            const char *tooMuch = "Segmentation Fault\n";
            send(client_fd, tooMuch, strlen(tooMuch), 0);

            // drain remaining bytes
            char temp[512];
            while (read(client_fd, temp, sizeof(temp)) > 0) {}
            close(client_fd);
            continue;
        }

        /* safe: valread < BUFFER_SIZE here */
        buffer[valread] = '\0';
        printf("Received: %s\n", buffer);

        int f1 = 0, f2 = 0, f4 = 0;
        unsigned int f3 = 0;
        int parsed = sscanf(buffer, "%d,%d,%x,%d", &f1, &f2, &f3, &f4);

        char response[BUFFER_SIZE];
        response[0] = '\0';  // initialize empty response
        int flag = 1;

        if (parsed == 4) {
            // Build response for 4-field CSV
            if (f1 != 332 && f1 != 328) {
                strncat(response, "Item \\x90 not recognized!\n", sizeof(response)-strlen(response)-1);
                flag = 0;
            }
            if (f2 < 8) {
                strncat(response, "Completing ledger\n", sizeof(response)-strlen(response)-1);
                flag = 0;
            }
            if (f3 != 0xFFFFE000u) {
                strncat(response, "Unrecognized return\n", sizeof(response)-strlen(response)-1);
                flag = 0;
            }
            if (f4 > 10000) {
                strncat(response, "Stack out of bounds...address too high\n", sizeof(response)-strlen(response)-1);
                flag = 0;
            }
            if (f4 < 8000) {
                strncat(response, "Stack out of bounds...unmapped address space\n", sizeof(response)-strlen(response)-1);
                flag = 0;
            }
            if (flag == 1) {
                /* place formatted text into response buffer */
                snprintf(response, sizeof(response), "You got it!\n");
                close(server_fd);
                return 0;
            }
        } else {
            // single string field
            snprintf(response, sizeof(response), "You sent: %s\n", buffer);
        }

        send(client_fd, response, strlen(response), 0);
        close(client_fd);
    }
    
    close(server_fd);
    return 0;
}

