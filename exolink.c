
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct hosts {
    char* server;
    unsigned int port;
    struct hosts* next_host;
} hosts;


typedef struct commands {
    char* value_name;
    int payload_lenght;
    unsigned char *payload;
    int response_length;
    struct commands* next_command;
} commands;


int main(int argc, char* argv[])
{
    printf("Hello\n");
}
