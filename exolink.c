
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct exo_hosts_t {
    char* server;
    unsigned int port;
    struct exo_hosts_t* next_host;
} exo_hosts_t;


typedef struct exo_commands {
    char* value_name;
    int payload_length;
    unsigned char *payload;
    int response_length;
    struct exo_commands* next_command;
} exo_commands;


#define MAX_CONFIG_SIZE 16384
char config_buffer[MAX_CONFIG_SIZE];

unsigned char get_nibble(unsigned char nibble) {
   unsigned char ret = 0;
   if(nibble >= '0' && nibble <= '9')
       ret = nibble - '0';
   else
       ret = nibble - 'a' + 10;
   return ret;
}

struct exo_commands* parse_command(char* conf_buf) {
    int jdx, end, start, i,j, pl_len;
    unsigned char tmp_p;
    unsigned char tmp_payload[20] = {0};
    struct exo_commands* command;
    command = malloc(sizeof (struct exo_commands));
    command->next_command = NULL;

    /* parse command config line starting at offset 4 */
    jdx=4;
    while ((conf_buf[jdx] != ',')) {jdx++;}
    end = jdx-5;
    command->value_name = strndup(&conf_buf[5],end);
    printf ("%s\n",command->value_name);
    printf("jdx=%d\n",jdx);

    /* parse command hex payload and length */
    start = jdx+1;
    jdx++;
    while ((conf_buf[jdx] != ',')) {jdx++;}
    end = jdx;
    printf("jdx=%d\n",jdx);
    for (j=0,i=start ; i<end ; i+=2,j++) {
        tmp_p = (get_nibble(conf_buf[i])&0xF) << 4;
        tmp_payload[j] = tmp_p | (get_nibble(conf_buf[i+1])&0xF);
        printf("0x%c%c %02x ",conf_buf[i], conf_buf[i+1], tmp_payload[j]);
        printf("\n");
    }
    printf("jdx=%d, start-end%d\n",jdx,end-start);
    pl_len = end-start/2;
    command->payload_length = pl_len;
    command->payload = malloc(pl_len);
    memcpy(command->payload, tmp_payload, pl_len);

    /* response length */
    

    return command;
}

/* Parse config file */
void parse_config(struct exo_hosts_t* hosts_list, exo_commands** head_command) {
    FILE *file;
    int idx=0;
    int config_size;
    struct exo_commands* next_cmd = NULL;

    file = fopen("exolink.config", "r");

    /* Read complete config file to memory */
    config_size = fread(config_buffer, 1, MAX_CONFIG_SIZE, file);
//    printf("%s\n%d", config_buffer, config_size);

    /* Parse config */
    while ((idx < config_size) && config_buffer[idx]) {
        if (!memcmp(&config_buffer[idx], "comm", 4)) {
            printf("comm found\n");
            next_cmd = parse_command(&config_buffer[idx]);
            if (*head_command)
                next_cmd->next_command = *head_command;
            *head_command = next_cmd;
        }
        if (!memcmp(&config_buffer[idx], "host", 4)) {
            printf("host found\n");
        }
//        printf("%c", config_buffer[idx]);
        /* Sync idx pointer to start of next line */
        while ((config_buffer[idx] != '\n')) {idx++;}
        idx++;
    }
    printf("%d\n", idx);
}

void print_config(exo_commands** head_command) {
    struct exo_commands* command = NULL;
    command = *head_command;
    printf("List:%x\n",head_command);
    while (command) {
        printf("%s\n",command->value_name);
        command = command->next_command;
    }
}

int main(int argc, char* argv[])
{
    struct exo_hosts_t* hosts_list = NULL;
    struct exo_commands* head_command = NULL;
    parse_config(hosts_list, &head_command);
    print_config(&head_command);
    printf("Hello\n");
}
