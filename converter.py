__author__ = 'Guoli Lv'
__email__ = 'gollyrui@i.smu.edu.cn'

class DataStream():

    """DataStream for BCI"""

    def __init__(self):
        """TODO: """
        #super(self.__init__(self),*args,**kwargs)
        pass



    def str2hex(self,string):

        return int(string,16)

    def read_txt(self, path):
        """TODO: Docstring for read_txt

        :path: TODO
        :returns: TODO

        """
        txt = open(path).read()
        txt = txt.split()
        indices = [i for i, x in enumerate(txt) if x == "AA"]
        datas = ''
        index = -1
        for indice in indices:
            index = index + 1
            if index == 255:
                index = -1
            indexStart = indice
            try:
                txt[indexStart+12]
            except IndexError:
                continue
            if txt[indexStart+6] == 'A1' and txt[indexStart +12] == 'AA':
                data = txt[indexStart:indexStart+12]

                #valid0 = data[5] + data[4] + data[3] + data[2]
                valid0 = '%s %s %s' % (data[4] , data[3] , data[2])
                #valid1 = data[10] + data[9] + data[8] + data[7]
                valid1 = '%s %s %s' % (data[9] , data[8] , data[7])

                sampleNumber = hex(index)[-2:]
                if sampleNumber[0] == 'x':
                    sampleNumber = '0' + sampleNumber[1]

                dataBytes = 'A0 %s %s %s %s %s %s %s %s %s 00 00 00 00 00 00 C2 '%(sampleNumber,valid0,valid0,valid0,valid0,valid0,valid0,valid0,valid0)
                datas = datas + dataBytes

        datas = datas.split()
        datas = [int(data,16) for data in datas]
        return bytes(datas)

    def write_bytes_to_file(self,bytesOut,name='test.hex'):
        fh = open(name,'wb')
        fh.write(bytesOut)


