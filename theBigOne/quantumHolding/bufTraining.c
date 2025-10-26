#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>

#define PORT 61
#define BUFFER_SIZE 256

int main() {
    int server_fd, client_fd;
    struct sockaddr_in address;
    int addrlen = sizeof(address);
    char buffer[BUFFER_SIZE + 1]; // +1 for null terminator

    // Create socket
    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
        perror("socket failed");
        exit(EXIT_FAILURE);
    }

    int opt = 1;
    setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(PORT);

    if (bind(server_fd, (struct sockaddr*)&address, sizeof(address)) < 0) {
        perror("bind failed");
        exit(EXIT_FAILURE);
    }

    if (listen(server_fd, 3) < 0) {
        perror("listen failed");
        exit(EXIT_FAILURE);
    }

    printf("Server listening on port %d...\n", PORT);

    while (1) {
        printf("Waiting for client...\n");
        client_fd = accept(server_fd, (struct sockaddr*)&address, (socklen_t*)&addrlen);
        if (client_fd < 0) {
            perror("accept");
            continue;
        }

        printf("Client connected!\n");

        int valread = read(client_fd, buffer, BUFFER_SIZE);
        if (valread <= 0) {
            close(client_fd);
            continue;
        }

        if (valread == BUFFER_SIZE) {
            const char *tooMuch = "Too many items!\n";
            send(client_fd, tooMuch, strlen(tooMuch), 0);

            // drain remaining bytes
            char temp[512];
            while (read(client_fd, temp, sizeof(temp)) > 0) {}
            close(client_fd);
            continue;
        }

        buffer[valread] = '\0';
        printf("Received: %s\n", buffer);

        int f1, f2, f4;
        unsigned int f3;
        int parsed = sscanf(buffer, "%d,%d,%x,%d", &f1, &f2, &f3, &f4);

        char response[BUFFER_SIZE];
        response[0] = '\0';  // initialize empty response
        int flag = 1;

        if (parsed == 4) {
            // Build response for 4-field CSV
            if (f1 < 208) {
                strncat(response, "Too few bytes!\n", sizeof(response)-strlen(response)-1);
                flag = 0;
            }
            if (f2 < 4) {
                strncat(response, "Too few return addresses, return address not overwritten\n", sizeof(response)-strlen(response)-1);
                flag = 0;
            }
            if (f3 != 0xffffe000) {
                strncat(response, "Wrong stack base address!\n", sizeof(response)-strlen(response)-1);
                flag = 0;
            }
            if ((f4 > 2000) || (f4 < 200)) {
                strncat(response, "Try a different offset!\n", sizeof(response)-strlen(response)-1);
                flag = 0;
            }
            if (flag == 1){
                snprintf(response, sizeof(response), "You cracked it!\n");
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
