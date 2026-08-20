%{
#include<stdio.h>
%}

%%

[A-Z][a-zA-Z]*    { printf("Starts with a Capital Letter\n"); return 0; }

[a-z][a-zA-Z]*    { printf("Does Not Start with a Capital Letter\n"); return 0; }

\n                { return 0; }

%%

int yywrap()
{
    return 1;
}

int main()
{
    printf("Enter a word: ");
    yylex();
    return 0;
}
