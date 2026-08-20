%{
#include<stdio.h>
#include<stdlib.h>
%}

%%

([0-2][0-9]|3[0-1])\/(0[1-9]|1[0-2])\/[0-9]{4}
{
    printf("Valid DOB\n");
    exit(0);
}

\n ;

%%

int yywrap()
{
    return 1;
}

int main()
{
    printf("Enter DOB (DD/MM/YYYY): ");
    yylex();
    printf("Invalid DOB\n");
    return 0;
}
