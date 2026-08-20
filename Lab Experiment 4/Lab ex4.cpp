#include <stdio.h>

int main() {
    char ch;

    printf("Enter operator: ");
    scanf("%c", &ch);

    switch(ch) {
        case '+':
        case '-':
        case '*':
        case '/':
            printf("Valid Arithmetic Operator\n");
            break;

        default:
            printf("Invalid Operator\n");
    }

    return 0;
}
