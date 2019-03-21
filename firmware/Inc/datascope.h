/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef __DATASCOPE_H
#define __DATASCOPE_H
#ifdef __cplusplus
 extern "C" {
#endif
   
#include "stm32f1xx_hal.h"
#include "main.h"
#include "ADS1292.h"
#include "usart.h"     

#define PACK 3
typedef struct {
    uint8_t state;
    uint8_t data[12];
} packet;
extern packet data[PACK];
extern uint8_t data_format[3];
extern uint8_t send;
     
void data_formatconfig_Start(uint8_t data[], uint8_t num);
void data_formatconfig_End(uint8_t data[]);
void dataproccess(packet * data, uint8_t num);
void dataproccess10(packet * data, uint8_t num);
void datasend(packet * pack);
     
#ifdef __cplusplus
}
#endif
#endif 
