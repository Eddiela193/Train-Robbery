#include <stdio.h>
#include <stdlib.h>

int main(int argc, char *argv[]) {
    if (argc != 5) {
        printf("Usage: %s <field1> <field2> <field3_hex> <field4>\n", argv[0]);
        return 1;
    }

    int field1 = atoi(argv[1]);
    int field2 = atoi(argv[2]);
    unsigned int field3;
    int field4 = atoi(argv[4]);

    // Parse hex field
    if (sscanf(argv[3], "%x", &field3) != 1) {
        printf("Invalid hex value for field3: %s\n", argv[3]);
        return 1;
    }

    printf("%d,%d,%X,%d\n", field1, field2, field3, field4);

    return 0;
}
