#include "ads1292.h"
#include "datascope.h"
#define BYTE0(Temp)       ( *( (char *)(&Temp)	  ) )
#define BYTE1(Temp)       ( *( (char *)(&Temp) + 1) )
#define BYTE2(Temp)       ( *( (char *)(&Temp) + 2) )
#define BYTE3(Temp)       ( *( (char *)(&Temp) + 3) )


uint8_t ADS_TEST;
uint8_t LOFF_STA;
uint8_t ADS_GPIO;
long ADS_CH1;
long ADS_CH2;
extern uint8_t BCI_Data[9];
uint8_t ADS1292_Data[16];
uint8_t buffer[PACK * 12];

uint8_t seq = 0;

uint8_t SPI1_STA;
//uint8_t ADS_STA;

uint8_t ADS1292_Default_Register_Settings[16] = {
//Device ID read Ony  0x53
    0x00,
    //CONFIG1 125SPS
    0x00,
    //CONFIG2
    0x98,
    //LOFF
    0x10,
    //CH1SET (PGA gain = 12)
    0x60,
    //CH2SET (PGA gain = 12)
    0x60,
    //RLD_SENS (default)
    0x00,
    //LOFF_SENS (default)
    0x00,
    //LOFF_STAT
    0x1f,
    //RESP1
    0x03,
    //RESP2
    0x07,
    //GPIO
    0x0C };
/**********************************************************************
 * USERS Function
 * 2 Setup ADS1292
 *********************************************************************/
void ADS1292_Init(void) {

  ADS1292_CONGPIO_Init();
  ADS1292_DRDYGPIO_Init();
  ADS1292_DRDYEXTI_DISABLE();
  MX_SPI1_Init();

  ADS1292_START_H;
  ADS1292_CS_H;

  ADS1292_RESET_H;
  delay_ms(1);
  ADS1292_RESET_L;
  delay_ms(1);
  ADS1292_RESET_H;
  delay_ms(7);
  delay_ms(1000);
  delay_ms(24);

  ADS1292_Clock_Select(1);
  delay_ms(500);
  ADS1292_START_L;
  delay_ms(7);
  ADS1292_START_H;
  delay_ms(7);

  ADS1292_START_L;
  delay_ms(14);
  delay_ms(1000);
  Start_Data_Conv_Command();
  Soft_Stop_ADS1292();
  delay_ms(5);

  Stop_Read_Data_Continuous();
  delay_ms(30);

  ADS1292_Reg_Write(ADS1x9x_REG_CONFIG1, 0x01);  // 0x00 125 SPS; 0x01 250Hz; 0x02 500Hz;
  ADS1292_Reg_Write(ADS1x9x_REG_CONFIG2, 0xB0);  //  4.033-V reference
  ADS1292_Reg_Write(ADS1x9x_REG_LOFF, 0x10);  //  Default
  ADS1292_Reg_Write(ADS1x9x_REG_CH1SET, 0x60);  //  Normal operation,PGA Gain=12
  ADS1292_Reg_Write(ADS1x9x_REG_CH2SET, 0x81); //  CH2 Power Down & Input Shorted
  ADS1292_Reg_Write(ADS1x9x_REG_RLD_SENS, 0x40);  //  All Reserved or Default
  ADS1292_Reg_Write(ADS1x9x_REG_LOFF_SENS, 0x00);  //  All Disable
  ADS1292_Reg_Write(ADS1x9x_REG_RESP1, 0x02);  //  Internal clock
  ADS1292_Reg_Write(ADS1x9x_REG_RESP2, 0x03);  //  For ADS1292R
  ADS1292_Reg_Write(ADS1x9x_REG_GPIO, 0x0C);  //  All Input
  delay_ms(100);
  printf(
      "\r\n============================================================\r\n");
  ADS1292_Read_All_Regs(ADS1292_Data);
  while (ADS1292_Data[0] != 0x53) {
    printf("\t\tADS1292 is Offline,  ERROR_CODE: %x\r\n", ADS1292_Data[0]);
    printf(
        "\r\n============================================================\r\n");
    ADS1292_Data[0] = ADS1292_Reg_Read(0x00);
    delay_ms(200);
  }
  ADS1292_Read_All_Regs(ADS1292_Data);
  delay_ms(100);
  printf("ADS1292 is Online,    TRUE_CODE: %X\r\n", ADS1292_Data[0]);
  printf("ADS1x9x_REG_CONFIG1,  TURE_CODE: 0%X\r\n", ADS1292_Data[1]);
  printf("ADS1x9x_REG_CONFIG2,  TURE_CODE: %X\r\n", ADS1292_Data[2]);
  printf("ADS1x9x_REG_LOFF   ,  TURE_CODE: %X\r\n", ADS1292_Data[3]);
  printf("ADS1x9x_REG_CH1SET ,  TURE_CODE: %X\r\n", ADS1292_Data[4]);
  printf("ADS1x9x_REG_CH2SET ,  TURE_CODE: %X\r\n", ADS1292_Data[5]);
  printf("ADS1x9x_REG_RLD_SENS, TURE_CODE: %X\r\n", ADS1292_Data[6]);
  printf("ADS1x9x_REG_LOFF_SENS,TURE_CODE: 0%X\r\n", ADS1292_Data[7]);
  printf("ADS1x9x_REG_LOFFSTAT ,TURE_CODE: 0%X\r\n", ADS1292_Data[8]);
  printf("ADS1x9x_REG_RESP1  ,  TURE_CODE: 0%X\r\n", ADS1292_Data[9]);
  printf("ADS1x9x_REG_RESP2  ,  TURE_CODE: 0%X\r\n", ADS1292_Data[10]);
  printf("ADS1x9x_REG_GPIO   ,  TURE_CODE: 0%X\r\n", ADS1292_Data[11]);
  printf(
      "\r\n============================================================\r\n");
}

/**********************************************************************
 * CONTROL        PINS DEFINATION
 * DRDY           PINS DEFINATION
 * INTERRPUT      MODE DEFINATION
 *********************************************************************/
void ADS1292_CONGPIO_Init(void) {

  GPIO_InitTypeDef GPIO_InitStruct;

  __HAL_RCC_GPIOA_CLK_ENABLE()
  ;
  __HAL_RCC_GPIOB_CLK_ENABLE()
  ;

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(ADS1292_CS_GPIO_Port, ADS1292_CS_PIN, GPIO_PIN_RESET);

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(GPIOB,
  ADS1292_CLKSEL_PIN | ADS1292_START_PIN | ADS_1292_RESET_PIN, GPIO_PIN_RESET);

  /*Configure GPIO pin : PtPin */
  GPIO_InitStruct.Pin = ADS1292_CS_PIN;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(ADS1292_CS_GPIO_Port, &GPIO_InitStruct);

  /*Configure GPIO pins : PBPin PBPin PBPin */
  GPIO_InitStruct.Pin = ADS1292_CLKSEL_PIN | ADS1292_START_PIN
      | ADS_1292_RESET_PIN;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOB, &GPIO_InitStruct);

}

void ADS1292_DRDYGPIO_Init(void) {

  GPIO_InitTypeDef GPIO_InitStruct;

  __HAL_RCC_GPIOB_CLK_ENABLE()
  ;

  /*Configure GPIO pin : PtPin */
  GPIO_InitStruct.Pin = ADS1292_DRDY_PIN;
  GPIO_InitStruct.Mode = GPIO_MODE_IT_FALLING;
  GPIO_InitStruct.Pull = GPIO_PULLUP;
  HAL_GPIO_Init(ADS1292_DRDY_GPIO_Port, &GPIO_InitStruct);
}

void ADS1292_DRDYEXTI_ENABLE(void) {
  HAL_GPIO_WritePin(ADS1292_DRDY_GPIO_Port, ADS1292_DRDY_PIN, GPIO_PIN_SET);

  HAL_NVIC_SetPriority(ADS1292_DRDY_EXTI_IRQn, 1, 1);
  HAL_NVIC_EnableIRQ(ADS1292_DRDY_EXTI_IRQn);
}

void ADS1292_DRDYEXTI_DISABLE(void) {
  HAL_NVIC_DisableIRQ(ADS1292_DRDY_EXTI_IRQn);
}

/**********************************************************************
 * SEND     FUNCTION    DEFINATION
 * RECEIVE  FUNCTION    DEFINATION
 * DMA      FUNCTION    DEFINATION
 *********************************************************************/
// success: rdata; fail: rdata=0xff;
uint8_t ADS1292_TRxAByte(uint8_t ch) {

  uint8_t rdata, tdata = ch;
  Set_ADS1292_Chip_Enable();
  delay_us(10);
  Clear_ADS1292_Chip_Enable();
  Set_ADS1292_Chip_Enable();

  if (HAL_SPI_TransmitReceive(&ADS1292_SPI, &tdata, &rdata, 1, 0xff)
      != HAL_OK) {
    rdata = 0xff;
  }
  return rdata;
}

// success: rdata; fail: rdata=0xff;
uint8_t ADS1292_RxAByte(void) {

  uint8_t rdata;
  if (HAL_SPI_Receive(&ADS1292_SPI, &rdata, 1, 0xff) != HAL_OK) {
    rdata = 0xff;
  }
  return rdata;
}
// success: sta=0; fail: sta=0xff;
uint8_t ADS1292_TxAByte(uint8_t ch) {

  uint8_t sta, tdata = ch;
  if (HAL_SPI_Transmit_DMA(&ADS1292_SPI, &tdata, 1) != HAL_OK) {
    sta = 0xff;
  }
  return sta;
}

/**********************************************************************
 * RESIGER  FUNCTION    DEFINATION
 * COMMAND  FUNCTION    DEFINATION
 *********************************************************************/
uint8_t ADS1292_SPI_Command(uint8_t ch) {
  uint8_t rx;

  Set_ADS1292_Chip_Enable();
  delay_ms(2);
  if (HAL_SPI_TransmitReceive(&ADS1292_SPI, &ch, &rx, 1, 0XFF) != HAL_OK) {
    rx = 0xff;
  }
  delay_ms(2);
  Clear_ADS1292_Chip_Enable();
  return rx;
}

uint8_t ADS1292_REG(uint8_t data, uint8_t command) {

  uint8_t i;
  for (i = 0; i < 45; i++)
    ;
  ADS1292_SPI_Command(command);
  for (i = 0; i < 45; i++)
    ;
  ADS1292_SPI_Command(0x00);
  for (i = 0; i < 45; i++)
    ;
  if ((command & 0x20) == 0x20) {
    ADS1292_SPI_Command(0x00);
    for (i = 0; i < 45; i++)
      ;
  }
  return (ADS1292_SPI_Command(data));
}

void ADS1292_RxData(uint8_t databuf[]) {

  uint8_t i, tmp = 0;

  Set_ADS1292_Chip_Enable();
  for (i = 0; i < 9; i++) {
    HAL_SPI_TransmitReceive(&ADS1292_SPI, &tmp, &databuf[i], 1, 10);
  }
  Clear_ADS1292_Chip_Enable();
}

void ADS1292_DataProcess(uint8_t databuf[]) {
  long tmp1, tmp2;
//  long tmp3,tmp4;
//  ADS_TEST  = (databuf[0] & 0xf0) >> 4;
//  LOFF_STA  = ((databuf[0] & 0x0f) << 1) | ((databuf[1] & 0x80) >> 7);
//  ADS_GPIO  = (databuf[1] & 0x60) >> 5;
  tmp1 = (long) databuf[3];
  tmp2 = (long) databuf[4];
//  tmp3 = (long) databuf[6];
//  tmp4 = (long) databuf[7];
//  ADS_CH1   = (((long) (tmp1 << 16) | (tmp2 << 8) | databuf[5]) & 0xffffff) << 8;
//  ADS_CH2   = (((long) (tmp3 << 16) | (tmp4 << 8) | databuf[8]) & 0xffffff) << 8;
  ADS_CH1 = (((long) (tmp1 << 16) | (tmp2 << 8) | databuf[5]) & 0xffffff);
//  ADS_CH2   = (((long) (tmp3 << 16) | (tmp4 << 8) | databuf[8]) & 0xffffff) ;
}

/**********************************************************************
 * CONTROL  FUNCTION    DEFINATION
 *********************************************************************/
void Set_ADS1292_Chip_Enable(void) {
  ADS1292_CS_L;
}
void Clear_ADS1292_Chip_Enable(void) {
  ADS1292_CS_H;
}
//////////////////////////////////////////////////////////////////////
void ADS1292_Disable_Start(void) {
  ADS1292_START_L;  	// Set to LOW
  delay_ms(7);        // Small Delay to settle   
}
void ADS1292_Enable_Start(void) {
  ADS1292_START_H;		// Set to High
  delay_ms(10);        // Small Delay to settle   
}
//////////////////////////////////////////////////////////////////////
void ADS1292_PowerDown_Enable(void) {
  ADS1292_RESET_L;	 // Set to low
  delay_ms(10);
}

void ADS1292_PowerDown_Disable(void) {
  ADS1292_RESET_H;	 // Set High
  delay_ms(10);
}
//////////////////////////////////////////////////////////////////////
void ADS1292_Reset(void) {
  ADS1292_RESET_H;		// Set High
  /* Provide suficient dealy*/
  delay_ms(1);				// Wait 1 mSec
  ADS1292_RESET_L;	  // Set to low
  delay_ms(1);			  // Wait 1 mSec
  ADS1292_RESET_H;		// Set High
  delay_ms(7);
}
// Send 0x06 to the ADS1x9x
void Soft_Reset_ADS1292(void) {
  ADS1292_SPI_Command(RESET);
}
//////////////////////////////////////////////////////////////////////
// Send 0x02 to the ADS1x9x 
void Wake_Up_ADS1292(void) {
  ADS1292_SPI_Command(WAKEUP);
}
// Send 0x04 to the ADS1x9x
void Put_ADS1x9x_In_Sleep(void) {
  ADS1292_SPI_Command(STANDBY);
}
//////////////////////////////////////////////////////////////////////
// Send 0x08 to the ADS1x9x
void Soft_Start_ReStart_ADS1292(void) {
  ADS1292_SPI_Command(START_);
  //Clear_ADS1292_Chip_Enable ();
}

void Hard_Start_ReStart_ADS1292(void) {
  ADS1292_START_H;			// Set Start pin to High
}
//////////////////////////////////////////////////////////////////////
void Soft_Start_ADS1292(void) {
  ADS1292_SPI_Command(START_);                   // Send 0x0A to the ADS1x9x
}

void Soft_Stop_ADS1292(void) {
  ADS1292_SPI_Command(STOP);                   // Send 0x0A to the ADS1x9x
}
void Hard_Stop_ADS1292(void) {
  ADS1292_START_L;		// Set Start pin to Low
  delay_ms(10);
}
//////////////////////////////////////////////////////////////////////
// Choose internal clock input : 1
void ADS1292_Clock_Select(uint8_t clock_in) {
  if (clock_in == 1) {
    ADS1292_CLKSEL_H;	// Choose internal clock input
  } else {
    ADS1292_CLKSEL_L;	// Choose external clock input
  }
}
//////////////////////////////////////////////////////////////////////
void Init_ADS1292(void) {
  ADS1292_Reset();
  ADS1292_Disable_Start();
  ADS1292_Enable_Start();
}
// Send 0x11 to the ADS1x9x
void Stop_Read_Data_Continuous(void) {
  ADS1292_SPI_Command(SDATAC);
}
// Send 0x10 to the ADS1x9x
void Start_Read_Data_Continuous(void) {
  ADS1292_SPI_Command(RDATAC);
}
// Send 0x08 to the ADS1x9x
void Start_Data_Conv_Command(void) {
  ADS1292_SPI_Command(START_);
}
void enable_ADS1292_Conversion(void) {
  Start_Read_Data_Continuous();		//RDATAC command
  Hard_Start_ReStart_ADS1292();
}
//////////////////////////////////////////////////////////////////////
void ADS1292_Read_All_Regs(uint8_t ADS1292_buf[]) {
  uint8_t Regs_i;
  Set_ADS1292_Chip_Enable();
  delay_ms(10);
  Clear_ADS1292_Chip_Enable();
  for (Regs_i = 0; Regs_i < 12; Regs_i++) {
    ADS1292_buf[Regs_i] = ADS1292_Reg_Read(Regs_i);
  }
}
//////////////////////////////////////////////////////////////////////
void ADS1292_Default_Reg_Init(void) {

  uint8_t Reg_Init_i;
  Set_ADS1292_Chip_Enable();
  delay_ms(10);
  Clear_ADS1292_Chip_Enable();

  for (Reg_Init_i = 1; Reg_Init_i < 12; Reg_Init_i++) {
    ADS1292_Reg_Write(Reg_Init_i,
        ADS1292_Default_Register_Settings[Reg_Init_i]);
  }
}
//////////////////////////////////////////////////////////////////////
uint8_t ADS1292_Reg_Read(uint8_t Reg_address) {

  uint8_t retVal;
  uint8_t SPI_Tx_buf[3];
  SPI_Tx_buf[0] = Reg_address | RREG;
  SPI_Tx_buf[1] = 0x00;							    // Read number of bytes - 1
  SPI_Tx_buf[2] = 0;

//	Set_ADS1292_Chip_Enable();					// Set chip select to low
//  delay_ms(5);
//  Clear_ADS1292_Chip_Enable();				// Disable chip select
  Set_ADS1292_Chip_Enable();					// Set chip select to low
  delay_ms(5);
//  while(hspi1.State != 0x01);
  if (HAL_SPI_TransmitReceive(&ADS1292_SPI, &SPI_Tx_buf[0], &retVal, 1, 0xff)
      != HAL_OK) {
    retVal = 0xf1;
    return retVal;
  }
  //delay_us(100);
//  while(HAL_DMA_GetState(&hdma_spi1_rx) != HAL_DMA_STATE_READY);
//  while(hspi1.State != 0x01);
  if (HAL_SPI_TransmitReceive(&ADS1292_SPI, &SPI_Tx_buf[1], &retVal, 1, 0xff)
      != HAL_OK) {
    retVal = 0xf2;
    return retVal;
  }
  //delay_us(100);
//  while(HAL_DMA_GetState(&hdma_spi1_rx) != HAL_DMA_STATE_READY);
//  while(hspi1.State != 0x01);
  if (HAL_SPI_TransmitReceive(&ADS1292_SPI, &SPI_Tx_buf[2], &retVal, 1, 0xff)
      != HAL_OK) {
    retVal = 0xf3;
    return retVal;
  }
  delay_ms(1);
//  while(HAL_DMA_GetState(&hdma_spi1_rx) != HAL_DMA_STATE_READY);
  Clear_ADS1292_Chip_Enable();				// Disable chip select
  return retVal;
}
//////////////////////////////////////////////////////////////////////
void ADS1292_Reg_Write(uint8_t READ_WRITE_ADDRESS, uint8_t DATA) {
  uint8_t i;
  uint8_t SPI_Tx_buf[3];
  switch (READ_WRITE_ADDRESS) {
  case 1:
    DATA = DATA & 0x87;
    break;
  case 2:
    DATA = DATA & 0xFB;
    DATA |= 0x80;
    break;
  case 3:
    DATA = DATA & 0xFD;
    DATA |= 0x10;
    break;
  case 7:
    DATA = DATA & 0x3F;
    break;
  case 8:
    DATA = DATA & 0x5F;
    break;
  case 9:
    DATA |= 0x02;
    break;
  case 10:
    DATA = DATA & 0x87;
    DATA |= 0x01;
    break;
  case 11:
    DATA = DATA & 0x0F;
    break;

  default:
    break;
  }
  SPI_Tx_buf[0] = READ_WRITE_ADDRESS | WREG;
  SPI_Tx_buf[1] = 0x00;						// Write Single byte
  SPI_Tx_buf[2] = DATA;					  // Write Single byte
  Set_ADS1292_Chip_Enable();

  delay_ms(10);

  if (HAL_SPI_TransmitReceive(&ADS1292_SPI, &SPI_Tx_buf[0], &i, 1, 0xff)
      != HAL_OK) {
    i = 0xf4;
    printf("%c", i);
  }
  delay_ms(2);
  if (HAL_SPI_TransmitReceive(&ADS1292_SPI, &SPI_Tx_buf[1], &i, 1, 0xff)
      != HAL_OK) {
    i = 0xf5;
    printf("%c", i);
  }
  delay_ms(2);
  if (HAL_SPI_TransmitReceive(&ADS1292_SPI, &SPI_Tx_buf[2], &i, 1, 0xff)
      != HAL_OK) {
    i = 0xf6;
    printf("%c", i);
  }
  delay_ms(2);

}
//////////////////////////////////////////////////////////////////////
void ADS1292_StreamData(void) {
  ADS1292_Disable_Start();			  //set ADC_START pin to LOW

  Clear_ADS1292_Chip_Enable();		//set SPI_CS pin to High
  delay_ms(300);
  Set_ADS1292_Chip_Enable();			//set SPI_CS pin to LOW
  delay_ms(10);
  Start_Read_Data_Continuous();		//RDATAC command
  delay_ms(30);
  ADS1292_DRDYEXTI_ENABLE();	            // Enable DRDY interrupt
  Clear_ADS1292_Chip_Enable();
  ADS1292_Enable_Start();				  //Set ADC_START pin to High
  delay_ms(50);
}

/**********************************************************************
 * SPI_RxCallback  FUNCTION    DEFINATION
 *********************************************************************/
void HAL_SPI_TxRxCpltCallback(SPI_HandleTypeDef *hspi) {

  if (hspi->Instance == SPI1) {
    SPI1_STA = HAL_OK;
    //printf("OK\r\n");
  }
}
void HAL_SPI_ErrorCallback(SPI_HandleTypeDef *hspi) {
  SPI1_STA = HAL_ERROR;
  printf("EORROR\r\n");
}

void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin) {
//  float ADS_CH1_F = 4.00642554;
  if (GPIO_Pin == GPIO_PIN_0) {
    __HAL_GPIO_EXTI_CLEAR_IT(GPIO_PIN_0);
//    ADS_STA = 1;

    dataproccess(&data[seq], 0);
//    ADS_CH1_F =  (float)(ADS_CH1 * ADS_CH1_F) / 100000000;
//    printf("\r\nCH1 = %.5f mV\t",ADS_CH1_F);
//    printf("CH1 = %ld \r\n", ADS_CH1);
    if (data[seq].state == 2) {
      data[seq].state = 0;
      seq++;
    }
    if (seq == PACK) {
      for (uint8_t i = 0; i < PACK; i++) {
        memcpy(buffer + (i) * 12, data[i].data, 12);
      }
      HAL_UART_Transmit_IT(&huart1, buffer, PACK *12);
      seq = 0;
    }
  }
}
