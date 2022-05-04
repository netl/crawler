#include <Servo.h>
#include <string.h>

Servo accelerator;
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

        if(message == 0xD || commandCounter == 10){
            //set last character to null byte
            command[commandCounter] = 0;

            //parse command and value
            String parsedCommand = strtok(command, " ");
            int parsedValue = atoi(strtok(NULL, " "));

            //try to handle command
            if(parsedCommand != NULL){
                //echo succesfull command
                Serial.print(parsedCommand);
                Serial.print(":");
                Serial.println(parsedValue);

                //just check for velocity and set it for now
                if(parsedCommand == "spd")
                    accelerator.write(parsedValue);

            //failed command
            }else{
                //return command as hex for readability over serial port
                Serial.print("bad command :");
                for (int n = 0 ; n < 11; n++)
                    Serial.print(command[n], HEX);
                Serial.println();
            }

            //clear command buffer and counter
            memset(command, 0, 11);
            commandCounter = 0;
        }
    }
}
