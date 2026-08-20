%{
#include <stdio.h>
#include <stdlib.h>
%}

%%
[0-9]      { printf("It is a Digit\n"); exit(0); }
.*         {printf("Not a Digit\n"); exit(0); }
\n         { /* Ignore newlines */ }
%%

int yywrap()
{
return 1;
}

int main()
{

     printf("Enter: ");
     yylex();
     return 0;
 }
