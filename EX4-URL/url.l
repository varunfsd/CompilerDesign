%{
#include<stdio.h>
%}

%%
^(https?:\/\/)?(www\.)?[A-Za-z0-9-]+\.[A-Za-z]{2,}(\/.*)?$   { printf("Valid URL\n"); }
.*                                                           { printf("Invalid URL\n"); }
%%

int yywrap()
{
    return 1;
}

int main()
{
    printf("Enter URL: ");
    yylex();
    return 0;
}
