#include <stdio.h>
#include <stdlib.h>

float cam1_position_x, cam1_position_y = 0;
float cam2_position_x, cam2_position_y = 0;

void get_positions() { // Retrieves positions from Guider Module Python via pipeline and updates global position variables
    char command[256];
    snprintf(command, sizeof(command), "Guider_Test.py");

    FILE *fp = popen("Guider_Test.py", "r");
    if (fp == NULL) {
        perror("Failed to run Python script");
        exit(1);
    }

    char output[1024];
    if (fgets(output, sizeof(output), fp) != NULL) {
        int scanned = sscanf(output, "%f %f %f %f", 
                              &cam1_position_x, &cam1_position_y, 
                              &cam2_position_x, &cam2_position_y);
        if (scanned == 4) {
            printf("Success");
        } else {
            printf("Failed to parse output.\n");
        }
    }

    fclose(fp);
}

int main () {
    get_positions();
    exit(0);
}