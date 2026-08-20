#include<stdio.h>
#include<string.h>

int main()
{
    char exp[20];
    char op1,op2,op;
    
    printf("Enter Expression (a+b): ");
    scanf("%s",exp);

    op1=exp[0];
    op=exp[1];
    op2=exp[2];

    printf("t1=%c%c%c\n",op1,op,op2);
    
    return 0;
}
