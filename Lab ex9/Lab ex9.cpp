#include <stdio.h>

int main()
{
    char nt;

    printf("Given Grammar:\n");
    printf("S -> (L) | a\n");
    printf("L -> L,S | S\n");

    printf("\nLeft Recursive Production:\n");
    printf("L -> L,S | S\n");

    printf("\nHere,\n");
    printf("L -> La | ß\n");
    printf("a = ,S\n");
    printf("ß = S\n");

    printf("\nAfter Eliminating Left Recursion:\n");
    printf("L  -> SL'\n");
    printf("L' -> ,SL' | e\n");

    printf("\nFinal Grammar:\n");
    printf("S  -> (L) | a\n");
    printf("L  -> SL'\n");
    printf("L' -> ,SL' | e\n");

    return 0;
}
