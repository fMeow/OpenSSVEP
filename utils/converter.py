__author__ = 'Guoli Lv'
__email__ = 'gollyrui@i.smu.edu.cn'

'''
Convert saved raw data of OpenSSVEP protocol to openBCI compatible protocol.
'''
import struct
import argparse

class DataStream():

    """DataStream for BCI"""

    def __init__(self,input_file,output_file='out.txt'):
        #super(self.__init__(self),*args,**kwargs)
        self.read_txt(input_file)

    def read_txt(self, input_file):
        """TODO: Docstring for read_txt

        :inputFile: inputFile
        :returns: list of data in time series
        """
        txt = open(input_file).read()
        txt = txt.split()
        indices = [i for i, x in enumerate(txt) if x == "AA"]
        self.data = list()
        for indice in indices:
            index_start = indice
            try:
                txt[index_start+12]
            except IndexError:
                continue
            if txt[index_start+6] == 'A1' and txt[index_start +12] == 'AA':
                data = txt[index_start:index_start+12]

                #valid0 = data[5] + data[4] + data[3] + data[2]
                valid0 = '%s%s%s%s' % (data[5], data[4] , data[3] , data[2])
                valid_int0 = struct.unpack('>i', bytes.fromhex(valid0))[0]
                self.data.append(valid_int0)

                #valid1 = data[10] + data[9] + data[8] + data[7]
                valid1 = '%s%s%s%s' % (data[10], data[9] , data[8] , data[7])
                valid_int1 = struct.unpack('>i', bytes.fromhex(valid1))[0]
                self.data.append(valid_int1)
        return self.data

    def write_to_txt(self,name='out.txt'):
        with open(name,'w') as fh:
            epoches = [ self.data[m:m+256] for m in range(0,len(self.data),256)]
            for epoch in epoches:
                for index in range(len(epoch)):
                    line = '%f,%f,%f,%f,%f,%f,%f,%f,%f\n' % (index,epoch[index],epoch[index],epoch[index],epoch[index],epoch[index],epoch[index],epoch[index],epoch[index])
                    fh.write(line)
            fh.flush()
            fh.close()

    def write_bytes_to_file(self,bytesOut,name='test.hex'):
        raise Exception('Deprecated')
        fh = open(name,'wb')
        fh.write(bytesOut)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--from', type=str, help='source file path',dest='source')
    parser.add_argument('--to', type=str, help='destination file path', dest='target')
    args = parser.parse_args()

    data_stream = DataStream(args.source)
    data_stream.write_to_txt(args.target)
