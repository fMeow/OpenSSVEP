#include "delay.h"
#define u8  uint8_t  
#define u16 uint16_t 
#define u32 uint32_t 
//static u8  fac_us=0;							//us延时倍乘数			   
//static u16 fac_ms=0;							//ms延时倍乘数,在ucos下,代表每个节拍的ms数
			   
//初始化延迟函数
//当使用OS的时候,此函数会初始化OS的时钟节拍
//SYSTICK的时钟固定为HCLK时钟的1/8
//SYSCLK:系统时钟
//void delay_init(void){
//	fac_us=SystemCoreClock/1000000;				//为系统时钟  
//	fac_ms=(u16)fac_us*1000;							//非OS下,代表每个ms需要的systick时钟数   
//}						
//延时nus
//nus为要延时的us数.		    								   
void delay_us(uint32_t nus)   {     
	uint32_t ticks;     
	uint32_t told,tnow,tcnt=0;     
	uint32_t reload=SysTick->LOAD;	//LOAD的值     
	ticks=nus*64;//需要的节拍数     
	tcnt=0;     
	told=SysTick->VAL;//刚进入时的计数器值     
	while(1){         
		tnow=SysTick->VAL;         
		if(tnow!=told){             
			if(tnow<told)
				tcnt+=told-tnow;        //这里注意一下SYSTICK是一个递减的计数器就可以了.            
			else 
				tcnt+=reload-tnow+told;             
			told=tnow;             
			if(tcnt>=ticks)break;			//超过/等于要延迟的时间,则退出.           
			}       
	};  
} 
//延时nms
//注意nms的范围
//SysTick->LOAD为24位寄存器,所以,最大延时为:
//nms<=0xffffff*8*1000/SYSCLK
//SYSCLK单位为Hz,nms单位为ms
//对72M条件下,nms<=1864 
void delay_ms(u16 nms)
{	 		  	  
	uint32_t ticks;     
	uint32_t told,tnow,tcnt=0;     
	uint32_t reload=SysTick->LOAD;	//LOAD的值     
	ticks=nms*64000;//需要的节拍数     
	tcnt=0;     
	told=SysTick->VAL;//刚进入时的计数器值     
	while(1){         
		tnow=SysTick->VAL;         
		if(tnow!=told){             
			if(tnow<told)
				tcnt+=told-tnow;        //这里注意一下SYSTICK是一个递减的计数器就可以了.            
			else 
				tcnt+=reload-tnow+told;             
			told=tnow;             
			if(tcnt>=ticks)break;			//超过/等于要延迟的时间,则退出.           
			}       
	};  	    
} 


/*
void delay_us(uint32_t nus){		
	uint32_t i;
	uint16_t time = 2;
	for(i=0;i<nus;i++){
		while(time--);
	}
}

void delay_ms(uint32_t nms){		
	uint32_t i;
	uint16_t time = 11900;
	for(i=0;i<nms;i++){
		while(time--);
	}
}*/
