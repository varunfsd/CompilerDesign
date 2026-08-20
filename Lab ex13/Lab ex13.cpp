#include <stdio.h>
#include <string.h>

char str[50];
int i = 0;

int S()
{
    if(str[i] == 'a')
    {
        i++;

        if(str[i] == 'b')
        {
            i++;
            return 1;
        }

        if(S())
        {
            if(str[i] == 'b')
            {
                i++;
                return 1;
            }
        }
    }
    return 0;
}

int main()
{
    printf("Grammar: S -> aSb | ab\n");

    printf("Enter the string: ");
    scanf("%s", str);

    if(S() && str[i] == '\0')
        printf("String Accepted\n");
    else
        printf("String Rejected\n");

    return 0;
}
