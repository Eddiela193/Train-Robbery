/* server_with_quant_once.c */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <errno.h>

#define PORT 101
#define BUFFER_SIZE 380

/* Helper: capture entire stdout of "python3 quant.py" into heap buffer.
 * Returns pointer to buffer (NUL-terminated) and sets out_size if non-NULL.
 * Caller must free() the returned buffer. On error returns NULL.
 */
char *capture_quant_output(const char *cmd, size_t *out_size) {
    FILE *fp = popen(cmd, "r");
    if (!fp) {
        perror("popen");
        return NULL;
    }

    size_t cap = 4096;
    size_t len = 0;
    char *buf = malloc(cap);
    if (!buf) {
        pclose(fp);
        return NULL;
    }

    char tmp[1024];
    while (1) {
        size_t r = fread(tmp, 1, sizeof(tmp), fp);
        if (r > 0) {
            if (len + r + 1 > cap) {
                size_t newcap = cap * 2;
                while (len + r + 1 > newcap) newcap *= 2;
                char *nb = realloc(buf, newcap);
                if (!nb) { free(buf); pclose(fp); return NULL; }
                buf = nb;
                cap = newcap;
            }
            memcpy(buf + len, tmp, r);
            len += r;
        }
        if (r < sizeof(tmp)) {
            if (feof(fp)) break;
            if (ferror(fp)) {
                perror("fread");
                free(buf);
                pclose(fp);
                return NULL;
            }
        }
    }

    buf[len] = '\0';
    if (out_size) *out_size = len;
    pclose(fp);
    return buf;
}

int main(void) {
    int server_fd = -1, client_fd = -1;
    struct sockaddr_in address;
    socklen_t addrlen = sizeof(address);
    char buffer[BUFFER_SIZE];

    /* 1) Run quant.py once and capture its output */
    size_t quant_len = 0;
    char *quant_output = capture_quant_output("python3 quant.py", &quant_len);
    if (!quant_output) {
        fprintf(stderr, "Warning: could not capture quant.py output; continuing without it.\n");
        quant_output = strdup(""); /* make non-NULL so sends are safe */
        quant_len = 0;
    } else {
        fprintf(stderr, "Captured %zu bytes from quant.py\n", quant_len);
    }

    /* 2) Create & bind socket as before */
    server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd < 0) { perror("socket"); free(quant_output); exit(1); }

    int opt = 1;
    setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    memset(&address, 0, sizeof(address));
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(PORT);

    if (bind(server_fd, (struct sockaddr *)&address, sizeof(address)) < 0) {
        perror("bind");
        free(quant_output);
        close(server_fd);
        exit(1);
    }

    if (listen(server_fd, 5) < 0) {
        perror("listen");
        free(quant_output);
        close(server_fd);
        exit(1);
    }

    printf("Listening on port %d...\n", PORT);

    while (1) {
        printf("Waiting for client...\n");
        client_fd = accept(server_fd, (struct sockaddr*)&address, &addrlen);
        if (client_fd < 0) {
            if (errno == EINTR) continue;
            perror("accept");
            break;
        }

        printf("Client connected!\n");

        /* 3) Send the quant.py output immediately to the client */
        ssize_t to_send = (ssize_t)quant_len;
        ssize_t sent_total = 0;
        while (sent_total < to_send) {
            ssize_t s = send(client_fd, quant_output + sent_total, (size_t)(to_send - sent_total), 0);
            if (s < 0) {
                if (errno == EINTR) continue;
                perror("send quant");
                break;
            }
            sent_total += s;
        }

        /* Now proceed to read client input (the original behavior) */
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
                strncat(response, "Stack out of bounds...unrecognized address\n", sizeof(response)-strlen(response)-1);
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
                close(client_fd);
                return 0;
            }
        } else {
            // single string field
            snprintf(response, sizeof(response), "You stored: %s\n", buffer);
        }

        send(client_fd, response, strlen(response), 0);

        close(client_fd);
        /* if you really want to only accept a single client and exit after:
           break;
         */
    }

    /* cleanup */
    free(quant_output);
    close(server_fd);
    return 0;
}
