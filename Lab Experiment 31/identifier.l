%{
#include<stdio.h>
#include<stdlib.h>
%}

%%

[a-zA-Z_][a-zA-Z0-9_]* {
    printf("Valid Identifier\n");
    exit(0);
}

.+ {
    printf("Invalid Identifier\n");
    exit(0);
}

%%

int yywrap()
{
    return 1;
}

int main()
{
    printf("Enter Identifier: ");
    yylex();
    return 0;
}
