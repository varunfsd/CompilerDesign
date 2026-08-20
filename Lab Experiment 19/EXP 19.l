%{
#include<stdio.h>

int chars = 0, words = 0, lines = 0;
%}

%%
"//".*                                  ;
"/*"([^*]|\*+[^*/])*\*+"/"              ;

\n              { lines++; chars++; }

[ \t]+          { chars += yyleng; }

[^ \t\n]+       {
                    words++;
                    chars += yyleng;
                }

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

    printf("\nCharacters = %d\n", chars);
    printf("Words      = %d\n", words);
    printf("Lines      = %d\n", lines);

    fclose(yyin);

    return 0;
}