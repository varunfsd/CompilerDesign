#include <stdio.h>
#include <string.h>

int main() {
    char str[200];

    printf("Enter a line: ");
    fgets(str, sizeof(str), stdin);

    if (strncmp(str, "//", 2) == 0)
        printf("Single Line Comment\n");
    else if (strncmp(str, "/*", 2) == 0 &&
             strstr(str, "*/") != NULL)
        printf("Multi Line Comment\n");
    else
        printf("Not a Comment\n");

    return 0;
}
