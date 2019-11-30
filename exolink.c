
#include <stdio.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <time.h>

typedef struct exo_hosts_t {
    char* server;
    unsigned int port;
    char* identifier;
    int client_socket;
    int active;
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

char* unit_status[] = { "Stopped", "Starting", "Starting", "Starting", "Starting", "Running", NULL , NULL, NULL, NULL, NULL, "Stopping", "Fire alarm", NULL, NULL};

#define MAX_CONFIG_SIZE 16384
#define ANS_BUFFER_SIZE 1024
char config_buffer[MAX_CONFIG_SIZE];

unsigned char get_nibble(unsigned char nibble) {
   unsigned char ret = 0;
   if(nibble >= '0' && nibble <= '9')
       ret = nibble - '0';
   else
       ret = nibble - 'a' + 10;
   return ret;
}

unsigned char* gen_packet(unsigned char* pl_buf, int pl_buf_len, int* payload_length) {
    int i, xorlen;
    unsigned char x = 0;
    unsigned char* pl;
    int end_pos = 0;

    xorlen = pl_buf_len;
    if (pl_buf[xorlen-1] == 0xe4) xorlen--;

    /* calculate xor sum over payload */
    for (i=0 ; i<xorlen ; i++)
        x^=pl_buf[i];

//    printf("%02x\n",x);
    /* Check if escape is needed */
    if (x==0x1b) {
        *payload_length = pl_buf_len+4;
        pl = malloc(pl_buf_len+4);
        memcpy(&pl[1], pl_buf, pl_buf_len);
        pl_buf_len++;
        pl[pl_buf_len] = x;
//        printf("%02x %02x\n",x, pl[pl_buf_len]);
        pl[pl_buf_len+1] = 0xe4;
    } else {
        *payload_length = pl_buf_len+3;
        pl = malloc(pl_buf_len+3);
        memcpy(&pl[1], pl_buf, pl_buf_len);
        pl[pl_buf_len+1] = x;
    }

    /* add start/stop marker */
    pl[0] = 0x3c;
    pl[pl_buf_len+2] = 0x3e;

    return pl;
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
    pl_len = (end-start)/2;
//    command->payload_length = pl_len + 3;
    command->payload = gen_packet(tmp_payload, pl_len, &command->payload_length);
//    command->payload = malloc(pl_len);
//    memcpy(command->payload, tmp_payload, pl_len);

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
    start = jdx+2;
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
    int i;
    struct exo_commands* command = NULL;
    command = *head_command;

    while (command) {
        printf("%s: %d\n",command->value_name,command->payload_type);
        for (i=0 ; i<command->payload_length ; i++) {
            printf(" %02x", command->payload[i]);
        }
        printf("\n");
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
    int res;
    struct exo_hosts_t* host = NULL;
    host = *head_host;

    while (host) {
//        printf("Connecting to host %s:%d - %s\n",host->server, host->port, host->identifier);

        host->client_socket = socket(PF_INET, SOCK_STREAM, 0);
        host->server_addr.sin_family = AF_INET;
        host->server_addr.sin_port = htons(host->port);
        host->server_addr.sin_addr.s_addr = inet_addr(host->server);
        memset(host->server_addr.sin_zero, '\0', sizeof host->server_addr.sin_zero);
        res = connect(host->client_socket, (struct sockaddr *) &(host->server_addr), sizeof host->server_addr);

        if (!res)
            host->active = 1;

        host = host->next_host;

    }
}

void parse_response(struct exo_hosts_t* host, exo_commands* cmd, unsigned char* ans_buf, int ans_buf_len) {
    int i, xorpos, shift;
    unsigned char x = 0;
    float val;
    unsigned int raw;
    int pl_off;

    /* Validate payload, start and end */
    if (ans_buf[0] != 0x3d) goto start_e;
    if (ans_buf[ans_buf_len-1] != 0x3e) goto end_e;

    /* Parse escape values (in place) if 0x1b is detected
     * invert next value
     */
    i=1;
    shift = 0;
    while (i<ans_buf_len-2) {
        if (shift)
            ans_buf[i] = ans_buf[i+shift];
        if (ans_buf[i] == 0x1b) {
            shift++;
            ans_buf[i] = ~ans_buf[i+shift];
        }
        i++;
    }
    /* reduce the payload length with the amount of escape values found */
    ans_buf_len -=shift;

    /* calculate xor sum over complete payload */
    for (i=1 ; i<ans_buf_len-2 ; i++)
        x^=ans_buf[i];

    /* validate xor sum  */
    xorpos = ans_buf_len-2;
    if (ans_buf[xorpos] != x) goto xor_end;

    /* parse payload, look for escape */
    pl_off = 3;

//    printf("%s ",host->identifier);
    switch (cmd->payload_type) {
        case EXOFLOAT:
            raw = ((ans_buf[pl_off+3] <<24) | (ans_buf[pl_off+2] << 16) | (ans_buf[pl_off+1] << 8) | ans_buf[pl_off]);
            val = *((float*)&raw);
            /* filter out bogus values */
            if ((val > -100.0 ) && (val < 500.0)) {
                printf(", \"Temperature Type\" : \"%s\" ",cmd->value_name);
                printf(", \"temperature_c\" : \"%f\" ", val);
            } else {
                 printf("val error = %f, %s, 0x%x\n", val, cmd->value_name, raw);
            }

            break;
        case EXOSHORT:
            pl_off = ans_buf_len-3;
            printf(", \"%s\" : \"%s\" ",cmd->value_name, unit_status[ans_buf[pl_off]]);
            printf(", \"%s_value\" : %d ",cmd->value_name, ans_buf[pl_off]);
            break;
        default:
            break;
    }

end:
    return;
start_e:
end_e:
    printf("start/end error\n");
    return;
xor_end:
    printf("xorsum error\n");
    return;
}

void transmit_commands(struct exo_hosts_t** head_hosts, exo_commands** head_command, int repeat) {
    int rb, sb, j;
    struct tm tm_info;
    time_t etime;
    char formatted_time[40];
    struct exo_hosts_t* host = NULL;
    struct exo_commands* command = NULL;
    unsigned char tmp_payload[100] = {0};
    unsigned char ans_buffer[ANS_BUFFER_SIZE];
    command = *head_command;
loop:
    host = *head_hosts;
    while (host) {
        if (host->active) {
            while (command) {
        //             printf("%s: %d\n",command->value_name, command->payload_length);
        //             for (j=0 ; j<command->payload_length ; j++)
        //                 printf("%02x ", command->payload[j]);
        //             printf("\n");


                sb = send(host->client_socket, command->payload, command->payload_length, 0);
                rb = recv(host->client_socket, ans_buffer, ANS_BUFFER_SIZE, 0);

                /* Build json message */

                time(&etime);
                localtime_r(&etime, &tm_info);
                strftime(formatted_time, 40, "%Y-%m-%d %H:%M:%S", &tm_info);

                printf("{\"time\" : \"%s\", ", formatted_time);
                printf(" \"brand\" : \"Regin\", ");
                printf(" \"model\" : \"Corrigo\", ");
                printf(" \"id\" : \"%s\"", host->identifier);
                parse_response(host, command, ans_buffer, rb);
                printf("}\n");
//                 for (j=0 ; j<rb ; j++)
//                     printf("%02x ",ans_buffer[j]);
//                 printf("\n");
 
                /* Flush to make sure the transmission gets out */
                fflush(stdout);

                command = command->next_command;
                usleep(500000);
                //memset(ans_buffer, 0, ANS_BUFFER_SIZE);
            }
        }
//        printf("\n");
        command = *head_command;
        host = host->next_host;
    }
    repeat--;
    if (repeat) goto loop;
}


int main(int argc, char* argv[]) {
    struct exo_hosts_t* head_hosts = NULL;
    struct exo_commands* head_command = NULL;
    parse_config(&head_hosts, &head_command);
//    print_config_command(&head_command);

    init_hosts(&head_hosts);
//    print_config_hosts(&head_hosts);

    transmit_commands(&head_hosts, &head_command, 10);
}
