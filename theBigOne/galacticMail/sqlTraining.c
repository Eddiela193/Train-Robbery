// auth_server.c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <errno.h>

#define PORT 62          /* privileged port; use >=1024 for non-root testing */
#define BUFFER_SIZE 512

/* read a line (up to buf_size-1 bytes) from fd into buf, stopping at '\n'.
 * Returns number of bytes placed in buf (not including the terminating NUL),
 * or -1 on error, or 0 on EOF/peer closed.
 */
ssize_t read_line(int fd, char *buf, size_t buf_size) {
    if (buf_size == 0) return -1;
    size_t idx = 0;
    while (idx + 1 < buf_size) {
        ssize_t r = recv(fd, buf + idx, 1, 0);
        if (r == 0) { // peer closed
            break;
        } else if (r < 0) {
            if (errno == EINTR) continue;
            return -1;
        }
        /* r == 1 */
        if (buf[idx] == '\n') {
            idx++;
            break;
        }
        idx++;
    }
    /* Trim any trailing CR/LF from the buffer for convenience */
    while (idx > 0 && (buf[idx-1] == '\n' || buf[idx-1] == '\r')) {
        idx--;
    }
    buf[idx] = '\0';
    return (ssize_t)idx;
}

/* send a nul-terminated string (s) to fd; returns 0 on success, -1 on error */
int send_str(int fd, const char *s) {
    size_t len = strlen(s);
    ssize_t sent = 0;
    while ((size_t)sent < len) {
        ssize_t r = send(fd, s + sent, len - sent, 0);
        if (r < 0) {
            if (errno == EINTR) continue;
            return -1;
        }
        sent += r;
    }
    return 0;
}

int main(void) {
    int server_fd = -1, client_fd = -1;
    struct sockaddr_in addr;
    socklen_t addrlen = sizeof(addr);
    char buf[BUFFER_SIZE];

    server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd < 0) {
        perror("socket failed");
        exit(EXIT_FAILURE);
    }

    int opt = 1;
    if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt)) < 0) {
        perror("setsockopt");
        close(server_fd);
        exit(EXIT_FAILURE);
    }

    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = INADDR_ANY;
    addr.sin_port = htons(PORT);

    if (bind(server_fd, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        fprintf(stderr, "bind failed: %s\n", strerror(errno));
        close(server_fd);
        exit(EXIT_FAILURE);
    }

    if (listen(server_fd, 5) < 0) {
        perror("listen failed");
        close(server_fd);
        exit(EXIT_FAILURE);
    }

    printf("Server listening on port %d...\n", PORT);

    int shutdown_requested = 0;

    while (!shutdown_requested) {
        printf("Waiting for client...\n");
        client_fd = accept(server_fd, (struct sockaddr *)&addr, &addrlen);
        if (client_fd < 0) {
            if (errno == EINTR) continue;
            perror("accept");
            break;
        }

        char peer[INET_ADDRSTRLEN] = "unknown";
        inet_ntop(AF_INET, &addr.sin_addr, peer, sizeof(peer));
        printf("Client connected from %s:%u\n", peer, ntohs(addr.sin_port));

        /* Prompt for username */
        if (send_str(client_fd, "Username: ") < 0) {
            close(client_fd);
            continue;
        }
        ssize_t n = read_line(client_fd, buf, sizeof(buf));
        if (n <= 0) {
            close(client_fd);
            continue;
        }
        char username[BUFFER_SIZE];
        strncpy(username, buf, sizeof(username));
        username[sizeof(username)-1] = '\0';
        printf("Received username: '%s'\n", username);

        /* Prompt for password */
        if (send_str(client_fd, "Password: ") < 0) {
            close(client_fd);
            continue;
        }
        n = read_line(client_fd, buf, sizeof(buf));
        if (n < 0) {
            close(client_fd);
            continue;
        }
        char password[BUFFER_SIZE];
        strncpy(password, buf, sizeof(password));
        password[sizeof(password)-1] = '\0';
        printf("Received password: '%s'\n", password);

        /* Logic: garry -> say hi; admin+letsGetCracking -> send msg and shutdown */
        if (strcmp(username, "1=1") == 0) {
            send_str(client_fd, "superuser:1234\n");
        }

        if (strcmp(username, "superuser") == 0 && strcmp(password, "1234") == 0) {
            send_str(client_fd, "Authorized.Don't hurt me too much!\n");
            close(client_fd);
            shutdown_requested = 1;
            break;
        }

        

        /* Default response (if neither condition matched) */
        if (shutdown_requested == 0) {
            send_str(client_fd, "Not quite, try giving a statement that is always true, like 2+2=4\nThink of the easiest number to use\n");
        }

        close(client_fd);
    }

    /* cleanup and exit */
    if (server_fd >= 0) close(server_fd);
    printf("Server exiting.\n");
    return 0;
}
