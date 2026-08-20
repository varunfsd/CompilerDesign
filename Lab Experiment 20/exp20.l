%{
#include<stdio.h>

int macro = 0, header = 0;
%}

DIGIT      [0-9]+(\.[0-9]+)?

%%

^#[ \t]*define.*           { macro++; }

^#[ \t]*include.*          { header++; }

{DIGIT}                    { printf("Constant : %s\n", yytext); }

\"([^\"\n]*)\"             ;

[a-zA-Z_][a-zA-Z0-9_]*      ;

[ \t\n]                    ;

.                           ;

%%

int yywrap()
{
    return 1;
}

int main()
{
    yyin = fopen("sample.c","r");

    if(yyin == NULL)
    {
        printf("Cannot open file\n");
        return 0;
    }

    yylex();

    printf("\nNumber of Macros      : %d\n", macro);
    printf("Number of Header Files: %d\n", header);

    fclose(yyin);

    return 0;
}