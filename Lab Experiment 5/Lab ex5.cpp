#include <stdio.h>

int main() {
    char str[500];
    int spaces = 0, newlines = 0, tabs = 0, i;

    printf("Enter text (Ctrl+Z to stop):\n");

    while ((i = getchar()) != EOF) {
        if (i == ' ')
            spaces++;
        else if (i == '\n')
            newlines++;
        else if (i == '\t')
            tabs++;
    }

    printf("Spaces = %d\n", spaces);
    printf("Tabs = %d\n", tabs);
    printf("New Lines = %d\n", newlines);

    return 0;
}
