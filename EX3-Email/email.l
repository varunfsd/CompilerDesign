%{
#include<stdio.h>
%}

%%
^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$   { printf("Valid Email ID\n"); }
.*                                                 { printf("Invalid Email ID\n"); }
%%

int yywrap()
{
    return 1;
}

int main()
{
    printf("Enter Email ID: ");
    yylex();
    return 0;
}
