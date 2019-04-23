
#include <stdio.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

typedef struct exo_hosts_t {
    char* server;
    unsigned int port;
    char* identifier;
    int client_socket;
    struct sockaddr_in server_addr;
    struct exo_hosts_t* next_host;
} exo_hosts_t;

typedef struct exo_commands {
    char* value_name;
    int payload_length;
    unsigned char *payload;
    int payload_type;
    int response_length;
    struct exo_commands* next_command;
} exo_commands;

#define EXOFLOAT 0
#define EXOSHORT 1

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
//    printf ("%s\n",command->value_name);
//    printf("jdx=%d\n",jdx);

    /* parse command hex payload and length */
    start = jdx+1;
    jdx++;
    while ((conf_buf[jdx] != ',')) {jdx++;}
    end = jdx;
//    printf("jdx=%d\n",jdx);
    for (j=0,i=start ; i<end ; i+=2,j++) {
        tmp_p = (get_nibble(conf_buf[i])&0xF) << 4;
        tmp_payload[j] = tmp_p | (get_nibble(conf_buf[i+1])&0xF);
//        printf("0x%c%c %02x ",conf_buf[i], conf_buf[i+1], tmp_payload[j]);
//        printf("\n");
    }
//    printf("jdx=%d, start-end%d\n",jdx,end-start);
    pl_len = end-start/2;
    command->payload_length = pl_len;
    command->payload = malloc(pl_len);
    memcpy(command->payload, tmp_payload, pl_len);

    /* response type */
    command->payload_type = conf_buf[end+1] - '0';
//    jdx++;
//    while ((conf_buf[jdx] != '\n')) {jdx++;}

    return command;
}

struct exo_hosts_t* parse_host(char* conf_buf) {
    int jdx, end, start, i,j;
    struct exo_hosts_t* host;
    
    host = malloc(sizeof (struct exo_hosts_t));
    host->next_host = NULL;

    /* parse ipaddress starting at offset 4 */
    jdx=4;
    while ((conf_buf[jdx] != ':')) {jdx++;}
    end = jdx-5;
    host->server = strndup(&conf_buf[5],end);
//    printf ("%s\n",host->server);

    /* parsing of port */
    jdx++;
    host->port=atoi(&conf_buf[jdx]);
//    printf ("%d\n",host->port);

    /* Parse identifier */
    while ((conf_buf[jdx] != ',')) {jdx++;}
    start = jdx+1;
    while ((conf_buf[jdx] != '\n')) {jdx++;}
    end = jdx-start;
    host->identifier = strndup(&conf_buf[start],end);
//    printf ("%s\n", host->identifier);

    return host;
}

/* Parse config file */
void parse_config(struct exo_hosts_t** head_hosts, exo_commands** head_command) {
    FILE *file;
    int idx=0;
    int config_size;
    struct exo_commands* next_cmd = NULL;
    struct exo_hosts_t* next_host = NULL;

    file = fopen("exolink.config", "r");

    /* Read complete config file to memory */
    config_size = fread(config_buffer, 1, MAX_CONFIG_SIZE, file);
//    printf("%s\n%d", config_buffer, config_size);

    /* Parse config */
    while ((idx < config_size) && config_buffer[idx]) {
        if (!memcmp(&config_buffer[idx], "comm", 4)) {
//            printf("comm found\n");
            next_cmd = parse_command(&config_buffer[idx]);
            if (*head_command)
                next_cmd->next_command = *head_command;
            *head_command = next_cmd;
        }
        if (!memcmp(&config_buffer[idx], "host", 4)) {
//            printf("host found\n");
            next_host = parse_host(&config_buffer[idx]);
            if (*head_hosts)
                next_host->next_host = *head_hosts;
            *head_hosts = next_host;
        }
//        printf("%c", config_buffer[idx]);
        /* Sync idx pointer to start of next line */
        while ((config_buffer[idx] != '\n')) {idx++;}
        idx++;
    }
//    printf("%d\n", idx);
}

void print_config_command(exo_commands** head_command) {
    struct exo_commands* command = NULL;
    command = *head_command;

    while (command) {
        printf("%s: %d\n",command->value_name,command->payload_type);
        command = command->next_command;
    }
}

void print_config_hosts(exo_hosts_t** head_host) {
    struct exo_hosts_t* host = NULL;
    host = *head_host;

    while (host) {
        printf("%s:%d - %s\n",host->server, host->port, host->identifier);
        host = host->next_host;
    }
}

void init_hosts(exo_hosts_t** head_host) {
    struct exo_hosts_t* host = NULL;
    host = *head_host;

    while (host) {
        printf("Connecting to host %s:%d - %s\n",host->server, host->port, host->identifier);

        host->client_socket = socket(PF_INET, SOCK_STREAM, 0);
        host->server_addr.sin_family = AF_INET;
        host->server_addr.sin_port = htons(host->port);
        host->server_addr.sin_addr.s_addr = inet_addr(host->server);
        memset(host->server_addr.sin_zero, '\0', sizeof host->server_addr.sin_zero);
        connect(host->client_socket, (struct sockaddr *) &(host->server_addr), sizeof host->server_addr);

        host = host->next_host;

    }
}


void transmit_commands(struct exo_hosts_t** head_hosts, exo_commands** head_command) {
    struct exo_hosts_t* host = NULL;
    host = *head_hosts;
}


int main(int argc, char* argv[]) {
    struct exo_hosts_t* head_hosts = NULL;
    struct exo_commands* head_command = NULL;
    parse_config(&head_hosts, &head_command);
 //   print_config_hosts(&head_hosts);
 //   print_config_command(&head_command);

    init_hosts(&head_hosts);

    transmit_commands(&head_hosts, &head_command);
}
