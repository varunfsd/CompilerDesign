%{
#include<stdio.h>
int line=1;
%}

%%
.*      { printf("%d\t%s\n",line++,yytext); }
%%

int yywrap()
{
    return 1;
}

int main()
{
    yylex();
    return 0;
}