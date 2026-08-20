#include <stdio.h>
#include <ctype.h>
#include <string.h>

int main() {
    char str[100];
    int i = 0;

    printf("Enter a statement: ");
    fgets(str, sizeof(str), stdin);

    while (str[i] != '\0') {
        if (isalpha(str[i]) || str[i] == '_') {
            printf("%c : Identifier\n", str[i]);
        }
        else if (isdigit(str[i])) {
            printf("%c : Constant\n", str[i]);
        }
        else if (strchr("+-*/=%", str[i])) {
            printf("%c : Operator\n", str[i]);
        }
        i++;
    }

    return 0;
}
