/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef __DELAY_H
#define __DELAY_H
#ifdef __cplusplus
 extern "C" {
#endif
   
#include "stm32f1xx_hal.h"
#include "main.h"
//void delay_init(void);
void delay_us(uint32_t nus);
void delay_ms(uint16_t nms);
	 
#ifdef __cplusplus
}
#endif
#endif /*__ pinoutConfig_H */
