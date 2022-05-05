#include <Servo.h>
#include <string.h>

Servo accelerator;
Servo steering;
void setup() {
    Serial.begin(115200);
    while(!Serial);
    accelerator.attach(3);
    Serial.println("ready");
}

//buffer for command and a variable to keep track of location
char command[11];
int commandCounter = 0;

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

        //just check for velocity and set it for now
        if( strcmp( parsedCommand, "spd") == 0)
            accelerator.write(parsedValue);

        //clear command buffer and counter
        memset(command, 0, 11);
        commandCounter = 0;
    }
}
