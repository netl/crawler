#include <Servo.h>
#include <string.h>

Servo accelerator;
Servo steering;
void setup() {
    Serial.begin(115200);
    while(!Serial);

    //setup servos
    accelerator.attach(3);
    accelerator.write(90);
    steering.attach(2);
    steering.write(90);

    Serial.println("ready");
}

//buffer for command and a variable to keep track of location
char command[11];
int commandCounter = 0;
char knownVariables[][5] = {"dir", "spd"}; //list of known knownVariables

void loop() {

    //process commands from serial port
    while(Serial.available()){
        char message = Serial.read();

        command[commandCounter] = message;
        commandCounter ++;

        if(message != '\r' && commandCounter < 10)
            continue;

        //set last character to null byte
        command[commandCounter] = 0;

        //parse command and value
        char *parsedCommand = strtok(command, " ");
        int parsedValue = atoi(strtok(NULL, " "));

        //echo processed command
        Serial.print(parsedCommand);
        Serial.print(" ");
        Serial.println(parsedValue);

        //compare command to known variables
        int n;
        for( n = 0; n < 2; n++)
            if( strcmp( parsedCommand, knownVariables[n]) == 0){
                break;
            }

        //set matching variable
        switch (n){
            case 0:
                steering.write(parsedValue);
                break;
            case 1:
                accelerator.write(parsedValue);
                break;
        }

        //clear command buffer and counter
        memset(command, 0, 11);
        commandCounter = 0;
    }
}
