import struct
import numpy as np
def test(raw):
    def rawData2Voltage(rawData,gainCoefficient=12):
        """Translate rawData to exact voltage

        :rawData: a list of rawData
        :returns: tranlated voltage tupple

        """
        raw = np.array(rawData)
        # 2.42 is the referrence voltage of BCI device, 24 is the sampling resolution
        dataVol = 2.42 / 2**24 / gainCoefficient * raw
        return tuple(dataVol)
    data = []
    start = b'\xaa'
    middle = b'\xa1'
    # find possible index by search raw data for which is the same with bytes indicating start
    possibleIndex = [i for i in range(len(raw)) if raw[i] == start ]
    lastIndex = 0
    # To validate possibleIndex, we should check whether the byte indicating middle comflies.
    for index in possibleIndex :
        middleIndex = index + 6
        try:
            raw[middleIndex]
        except Exception as e:
            continue
        if raw[middleIndex] == middle:
            # middle byte does comply, so extract the pack
            rawDataPack = raw[index:index+12]
            # TODO given check code is smaller than protocol
            checkCode = sum([ord(byte) for byte in rawDataPack[0:-1]])%256
            if ord(rawDataPack[-1]) == checkCode:
                # All validation steps passed
                # Translate hex to int
                dataHex = rawDataPack[2:6] # first data
                data.append(struct.unpack('<i', dataHex)[0])

                dataHex = rawDataPack[7:11] # second dats
                data.append(struct.unpack('<i', dataHex)[0])
                lastIndex = index+12
    remained = raw[lastIndex:]
    return  data,rawData2Voltage(data),remained
