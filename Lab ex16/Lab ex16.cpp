#include <stdio.h>

int main()
{
    char lhs, op1, op2, opr;

    printf("Enter expression (Example: a=b+c): ");
    scanf(" %c=%c%c%c", &lhs, &op1, &opr, &op2);

    printf("\nGenerated Target Code:\n");

    printf("MOV R0, %c\n", op1);

    switch(opr)
    {
        case '+':
            printf("ADD R0, %c\n", op2);
            break;

        case '-':
            printf("SUB R0, %c\n", op2);
            break;

        case '*':
            printf("MUL R0, %c\n", op2);
            break;

        case '/':
            printf("DIV R0, %c\n", op2);
            break;

        default:
            printf("Invalid Operator\n");
            return 0;
    }

    printf("MOV %c, R0\n", lhs);

    return 0;
}
