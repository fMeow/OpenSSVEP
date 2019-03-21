#include "datascope.h"
#include "math.h"
//uint8_t test[12];
packet data[PACK];
uint8_t data_send[12];
uint8_t data_format[3] = { 0xAA, 0xA1, 0 };
uint8_t send = 0;
extern uint8_t BCI_Data[9];
uint8_t res = 0;
uint8_t sig = 0;

void data_formatconfig_Start(uint8_t data[], uint8_t num) {

  data[0] = data_format[0];
  data[1] = num & 0x3f;
  //data[5] = 0x00;
  data[6] = data_format[1];
  //data[10] = 0x00;
}
void data_formatconfig_End(uint8_t data[]) {
  uint8_t cnt;
    int sum = 0;
//  sum = 0;
  for (cnt = 0; cnt < 11; cnt++) {
    sum += data[cnt];
  }
  res = sum % 256;
  data_format[2] = res;
  data[11] = data_format[2];
}

void dataproccess10(packet * pack, uint8_t num) {
  long tmp;
  ADS1292_RxData(BCI_Data);
  ADS1292_DataProcess(BCI_Data);
  pack->data[0] = data_format[0];
  pack->data[1] = num & 0x3f;
  pack->data[5] = data_format[1];

  tmp = ADS_CH1;
  tmp = tmp & 0x00ffffff;

  if (pack->state == 0) {
    pack->data[2] = (tmp);
    pack->data[3] = (tmp >> 8);
    pack->data[4] = (tmp >> 16);

    pack->state++;
  } else if (pack->state == 1) {
    pack->data[6] = tmp;
    pack->data[7] = tmp >> 8;
    pack->data[8] = tmp >> 16;
    pack->state++;

    uint8_t sum = 0;
    for (uint8_t cnt = 0; cnt < 9; cnt++) {
      sum += pack->data[cnt];
    }
    res = sum % 256;
    data_format[2] = res;
    pack->data[9] = data_format[2];
  }
}

void dataproccess(packet * pack, uint8_t num) {
  long tmp;
  ADS1292_RxData(BCI_Data);
  ADS1292_DataProcess(BCI_Data);
  data_formatconfig_Start(pack->data, num);
  tmp = ADS_CH1;
  tmp = tmp & 0x00ffffff;
//    if(tmp >> 23) {
//      tmp = ~tmp;   
//      tmp += 1;      
//      sig = 1; 
//    }
//    else{
//      sig = 0;
//    }

  if (pack->state == 0) {
    pack->data[3] = (tmp);
    pack->data[4] = (tmp >> 8);
    pack->data[5] = (tmp >> 16);
    pack->data[2] = 0;
//        if(sig)
//          data[5] = 0x80;
//        else
//          data[5] = 0x00;
    pack->state++;

//      pack[2] = data[2];
//      pack[3] = data[3];
//      pack[4] = data[4];
//      pack[5] = data[5];

  } else if (pack->state == 1) {
    pack->data[8] = tmp;
    pack->data[9] = tmp >> 8;
    pack->data[10] = tmp >> 16;
    pack->data[7] = 0;
//        if(sig)
//          data[10] = 0x80;
//        else
//          data[10] = 0x00;
    pack->state++;
//      test[0] = data[0];
//      test[1] = data[1];
//      test[6] = data[6];
//      
//      test[7] = data[7];
//      test[8] = data[8];
//      test[9] = data[9];
//      test[10] = data[10];
    data_formatconfig_End(pack->data);
//      test[11] = data[11];
  }
}
