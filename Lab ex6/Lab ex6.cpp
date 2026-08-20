#include <stdio.h>
#include <ctype.h>
#include <string.h>

int main() {
    char id[50];
    int i;

    printf("Enter Identifier: ");
    scanf("%s", id);

    if (!(isalpha(id[0]) || id[0] == '_')) {
        printf("Invalid Identifier\n");
        return 0;
    }

    for (i = 1; id[i] != '\0'; i++) {
        if (!(isalnum(id[i]) || id[i] == '_')) {
            printf("Invalid Identifier\n");
            return 0;
        }
    }

    printf("Valid Identifier\n");

    return 0;
}
