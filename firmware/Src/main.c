/**
 ******************************************************************************
 * File Name          : main.c
 * Description        : Main program body
 ******************************************************************************
 ** This notice applies to any and all portions of this file
 * that are not between comment pairs USER CODE BEGIN and
 * USER CODE END. Other portions of this file, whether
 * inserted by the user or by software development tools
 * are owned by their respective copyright owners.
 *
 * COPYRIGHT(c) 2017 STMicroelectronics
 *
 * Redistribution and use in source and binary forms, with or without modification,
 * are permitted provided that the following conditions are met:
 *   1. Redistributions of source code must retain the above copyright notice,
 *      this list of conditions and the following disclaimer.
 *   2. Redistributions in binary form must reproduce the above copyright notice,
 *      this list of conditions and the following disclaimer in the documentation
 *      and/or other materials provided with the distribution.
 *   3. Neither the name of STMicroelectronics nor the names of its contributors
 *      may be used to endorse or promote products derived from this software
 *      without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
 * FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 * DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
 * SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
 * CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
 * OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 ******************************************************************************
 */
/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "stm32f1xx_hal.h"
#include "spi.h"
#include "usart.h"
#include "gpio.h"

/* USER CODE BEGIN Includes */
#include "ads1292.h"
#include "delay.h"
#include "datascope.h"
/* USER CODE END Includes */

/* Private variables ---------------------------------------------------------*/

/* USER CODE BEGIN PV */
/* Private variables ---------------------------------------------------------*/
uint8_t BCI_Data[9];
uint8_t send_num = 0;

/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
static void MX_NVIC_Init(void);

/* USER CODE BEGIN PFP */
/* Private function prototypes -----------------------------------------------*/

/* USER CODE END PFP */

/* USER CODE BEGIN 0 */

/* USER CODE END 0 */


int main(void) {

  /* USER CODE BEGIN 1 */

  /* USER CODE END 1 */

  /* MCU Configuration----------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* USER CODE BEGIN Init */

  /* USER CODE END Init */

  /* Configure the system clock */
  SystemClock_Config();

  /* USER CODE BEGIN SysInit */

  /* USER CODE END SysInit */

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_USART1_UART_Init();
  MX_SPI1_Init();

  /* Initialize interrupts */
  MX_NVIC_Init();

  /* USER CODE BEGIN 2 */
  // +++退出透传模式，如果为软重启，上次TCP连接尚未断开，则这一步很关键
  char * data = "+++";
  HAL_UART_Transmit(&huart1, data, strlen(data), 100);
  delay_ms(49);
  data = "AT+CIPCLOSE\r\n";
  HAL_UART_Transmit(&huart1, data, strlen(data), 100);
  delay_ms(49);
  data = "AT+RST\r\n";
  HAL_UART_Transmit(&huart1, data, strlen(data), 100);
  ADS1292_Init();

  // WIfi Init
  char rBuf[128] = { 0 };
  int connected = 0;
  data = "AT+CIPSTATUS\r\n";
  while (!connected) {
    HAL_UART_Transmit(&huart1, data, strlen(data), 100);
    HAL_UART_Receive(&huart1, rBuf, 128, 100);
    // 判断是否连接上WiFi
    if (strcmp(rBuf, "AT+CIPSTATUS\r\r\nSTATUS:2\r\n\r\nOK\r\n") == 0) {
      connected = 1;
    }
    memset(rBuf, 0, sizeof(rBuf));
  }

  data = "AT+CIPSTART=\"TCP\",\"172.16.159.1\",23333\r\n";

  connected = 0;
  while (!connected) {
    HAL_UART_Transmit(&huart1, data, strlen(data), 100);
    HAL_UART_Receive(&huart1, rBuf, 128, 100);
    //判断是否连接上TCP服务器
    if (strcmp(rBuf,
        "AT+CIPSTART=\"TCP\",\"172.16.159.1\",23333\r\r\nCONNECT\r\n\r\nOK\r\n")
        == 0) {
      connected = 1;
    }
    memset(rBuf, 0, sizeof(rBuf));
  }
  data = "AT+CIPMODE=1\r\n";
  HAL_UART_Transmit(&huart1, data, strlen(data), 100);
  delay_ms(49);
  data = "AT+CIPSEND\r\n";
  HAL_UART_Transmit(&huart1, data, strlen(data), 100);

  ADS1292_DRDYEXTI_ENABLE();	            // Enable DRDY interrupt
  ADS1292_StreamData();

  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
//  uint8_t text[36] = "miaomiao!!!\tmiaomiao!!!\tmiaomiao!!\r\n";
  while (1) {
    /* USER CODE END WHILE */

    /* USER CODE BEGIN 3 */
//    if(ADS_STA){
//        ADS_STA = 0;
//    }
//   HAL_UART_Transmit_IT(&huart1,text ,36);
//   HAL_Delay(47);
    delay_ms(1999);
    LED_TOGGLE;
  }
  /* USER CODE END 3 */

}

/** System Clock Configuration
 */
void SystemClock_Config(void) {

  RCC_OscInitTypeDef RCC_OscInitStruct;
  RCC_ClkInitTypeDef RCC_ClkInitStruct;

  /**Initializes the CPU, AHB and APB busses clocks
   */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSE;
  RCC_OscInitStruct.HSEState = RCC_HSE_ON;
  RCC_OscInitStruct.HSEPredivValue = RCC_HSE_PREDIV_DIV1;
  RCC_OscInitStruct.HSIState = RCC_HSI_ON;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSE;
  RCC_OscInitStruct.PLL.PLLMUL = RCC_PLL_MUL8;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK) {
    _Error_Handler(__FILE__, __LINE__);
  }

  /**Initializes the CPU, AHB and APB busses clocks
   */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK | RCC_CLOCKTYPE_SYSCLK
      | RCC_CLOCKTYPE_PCLK1 | RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV2;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_2) != HAL_OK) {
    _Error_Handler(__FILE__, __LINE__);
  }

  /**Configure the Systick interrupt time
   */
  HAL_SYSTICK_Config(HAL_RCC_GetHCLKFreq() / 1000);

  /**Configure the Systick
   */
  HAL_SYSTICK_CLKSourceConfig(SYSTICK_CLKSOURCE_HCLK);

  /* SysTick_IRQn interrupt configuration */
  HAL_NVIC_SetPriority(SysTick_IRQn, 0, 0);
}

/** NVIC Configuration
 */
static void MX_NVIC_Init(void) {
  /* SPI1_IRQn interrupt configuration */
  HAL_NVIC_SetPriority(SPI1_IRQn, 1, 1);
  HAL_NVIC_EnableIRQ(SPI1_IRQn);
  /* EXTI0_IRQn interrupt configuration */
  HAL_NVIC_SetPriority(EXTI0_IRQn, 1, 0);
  HAL_NVIC_EnableIRQ(EXTI0_IRQn);
}

/* USER CODE BEGIN 4 */

/* USER CODE END 4 */

/**
 * @brief  This function is executed in case of error occurrence.
 * @param  None
 * @retval None
 */
void _Error_Handler(char * file, int line) {
  /* USER CODE BEGIN Error_Handler_Debug */
  /* User can add his own implementation to report the HAL error return state */
  while (1) {
  }
  /* USER CODE END Error_Handler_Debug */
}

#ifdef USE_FULL_ASSERT

/**
 * @brief Reports the name of the source file and the source line number
 * where the assert_param error has occurred.
 * @param file: pointer to the source file name
 * @param line: assert_param error line source number
 * @retval None
 */
void assert_failed(uint8_t* file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
   ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */

}

#endif

/**
 * @}
 */

/**
 * @}
 */

/************************ (C) COPYRIGHT STMicroelectronics *****END OF FILE****/
