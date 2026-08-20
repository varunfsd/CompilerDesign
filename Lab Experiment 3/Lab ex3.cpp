#include <stdio.h>
#include <ctype.h>

int main() {
    char str[200];
    int i = 0;

    printf("Enter code: ");
    fgets(str, sizeof(str), stdin);

    while (str[i] != '\0') {
        if (str[i] == ' ' || str[i] == '\t' || str[i] == '\n') {
            i++;
            continue;
        }

        if (str[i] == '/' && str[i+1] == '/') {
            break;
        }

        printf("%c", str[i]);
        i++;
    }

    return 0;
}
