%{
#include <stdio.h>
int vowels = 0;
int consonants = 0;
%}

%%
[aeiouAEIOU]           { vowels++; }
[a-zA-Z]               { consonants++; }
\n                     { return 0; }
.                      { /* Ignore spaces, numbers, and punctuation */ }
%%

int yywrap() {
return 1;
}

int main() {
printf("Enter a string: ");
yylex();
printf("\nTotal Vowels: %d\n", vowels);
printf("Total Consonants: %d\n", consonants);
return 0;
}
