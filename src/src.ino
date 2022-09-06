#include <Servo.h>
#include <string.h>

Servo accelerator;
Servo steering;
#define PITCH_PIN 4
Servo pitch;
#define YAW_PIN 5
Servo yaw;
const int batIPin = A0;
const int batVPin = A1;

void setup() {
    Serial.begin(115200);
    while(!Serial);

    //setup servos
    accelerator.attach(3);
    accelerator.write(90);
    steering.attach(2);
    steering.write(90);
    pitch.attach(PITCH_PIN);
    pitch.write(90);
    yaw.attach(YAW_PIN);
    yaw.write(90);

    pinMode(batIPin, INPUT);
    pinMode(batVPin, INPUT);

    Serial.println("ready");
}

//buffer for command and a variable to keep track of location
char command[11];
int commandCounter = 0;
char knownVariables[][6] = {"dir", "spd", "pitch", "yaw", ""}; //list of known knownVariables

//timer for stopping motors
unsigned long nextStop = 0;

unsigned long nextUpdate = 0;

void loop() {

    unsigned long t = millis();

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

        //compare command to known variables
        int n;
        for( n = 0; n < 4; n++)
            if( strcmp( parsedCommand, knownVariables[n]) == 0){
                break;
            }

        //set matching variable
        switch (n){
            case 0:
                steering.write(parsedValue+90);
                break;
            case 1:
                accelerator.write(parsedValue+90);
                nextStop = t + 300;
                break;
            case 2:
                pitch.write(parsedValue+90);
                break;
            case 3:
                yaw.write(parsedValue+90);
                break;
        }

        //clear command buffer and counter
        memset(command, 0, 11);
        commandCounter = 0;
    }

    //stop if motors have been running without updates
    if(nextStop < t)
        accelerator.write(90);

    //output all known variables periodically
    if(nextUpdate < t){
        Serial.print("dir ");
        Serial.println(steering.read()-90, DEC);

        Serial.print("spd ");
        Serial.println(accelerator.read()-90, DEC);

        Serial.print("pitch ");
        Serial.println(pitch.read()-90, DEC);

        Serial.print("yaw ");
        Serial.println(yaw.read()-90, DEC);

        Serial.print("batI ");
        Serial.println(( (uint16_t) analogRead(batIPin)-60)*202/(88-60), DEC);

        Serial.print("batV ");
        Serial.println(float(analogRead(batVPin))*8.35/853., 2);
        nextUpdate = t + 300;
    }

}
