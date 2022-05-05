# Specification  

* Convert a regular rc car into a remote operated vehicle  
* Provide all required electronics required for basic functionality  
* Allow going into a low power state   
* Use simple interfaces in order to provide good upgradeability  


# Electrical signals  

Below are listed all the signals that are needed for proper operation  

|GPIO|I/O|A/D| purpose         |
|----|---|---|-----------------|
| 2  | O | D | direction       |
| 3  | O | D | speed           |
| A0 | I | A | battery current |
| A1 | I | A | battery voltage |
|    | I | D | battery charging|
|    | I | D | wake up         |
|    | O | D | external power  |


# Firmware  

All communication should be done in the following format:  
```
<variable> <value>\n
```
Any singals that provide risk (eg, speed) should be set to a safe value if not 
updated regularly. All variables should be output at least once per second 
when external power is on.  

|variable| set |  scale  | description          |
|--------|-----|---------|----------------------|
| spd    | yes | PWM-125 | speed                |
| dir    | yes | PWM-125 | direction            |
| pOff   | yes | minutes | go to sleep timer    |
| pOn    | yes | minutes | wake up timer        |
| batV   | no  | mV      | battery voltage      |
| batI   | no  | mA      | battery current      |
| batF   | no  | mAh     | battery fuel estimate|
| chg    | no  | 1/0     | battery charging     |
