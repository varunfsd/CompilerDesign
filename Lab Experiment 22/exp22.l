%{
#include <stdio.h>
%}

%%
\<[^>]*\>     { printf("%s\n", yytext); }

.|\n          ;
%%

int yywrap()
{
    return 1;
}

int main()
{
    yyin = fopen("sample.html", "r");

    if(yyin == NULL)
    {
        printf("Cannot open file\n");
        return 0;
    }

    yylex();

    fclose(yyin);
    return 0;
}