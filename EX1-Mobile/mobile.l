%{
#include <stdio.h>
#include <stdlib.h>
%}

%%
^[0-9]{10}$     { printf("Valid 10-digit Mobile Number\n"); exit(0); }
\n              { /* Ignore the newline completely */ }
.               { printf("Invalid Mobile Number\n"); exit(0); }
%%


int yywrap()
{
return 1;
}

int main()
{
printf("Enter a mobile number: ");
yylex();
return 0;
}


