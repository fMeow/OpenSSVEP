__author__ = 'Guoli Lv'
__email__ = 'gollyrui@i.smu.edu.cn'
import struct

class DataStream():

    """DataStream for BCI"""

    def __init__(self,inputFile,outputFile='out.txt'):
        """TODO: """
        #super(self.__init__(self),*args,**kwargs)
        data = self.read_txt(inputFile)
        self.write_to_txt(data,outputFile)

    def read_txt(self, inputFile):
        """TODO: Docstring for read_txt

        :inputFile: inputFile
        :returns: list of data in time series
        """
        txt = open(inputFile).read()
        txt = txt.split()
        indices = [i for i, x in enumerate(txt) if x == "AA"]
        datas = list()
        for indice in indices:
            indexStart = indice
            try:
                txt[indexStart+12]
            except IndexError:
                continue
            if txt[indexStart+6] == 'A1' and txt[indexStart +12] == 'AA':
                data = txt[indexStart:indexStart+12]

                #valid0 = data[5] + data[4] + data[3] + data[2]
                valid0 = '%s%s%s%s' % (data[5], data[4] , data[3] , data[2])
                validInt0 = struct.unpack('>i', bytes.fromhex(valid0))[0]
                datas.append(validInt0)

                #valid1 = data[10] + data[9] + data[8] + data[7]
                valid1 = '%s%s%s%s' % (data[10], data[9] , data[8] , data[7])
                validInt1 = struct.unpack('>i', bytes.fromhex(valid1))[0]
                datas.append(validInt1)
        return datas

    def write_to_txt(self,data,name='out.txt'):
        with open(name,'w') as fh:
            epoches = [ data[m:m+256] for m in range(0,len(data),256)]
            for epoch in epoches:
                for index in range(len(epoch)):
                    line = '%f,%f,%f,%f,%f,%f,%f,%f,%f\n' % (index,epoch[index],epoch[index],epoch[index],epoch[index],epoch[index],epoch[index],epoch[index],epoch[index])
                    fh.write(line)
            fh.close()

    def write_bytes_to_file(self,bytesOut,name='test.hex'):
        raise Exception('Deprecated')
        fh = open(name,'wb')
        fh.write(bytesOut)


if __name__ == '__main__':
    dataStream = DataStream('./EEG1.txt')

