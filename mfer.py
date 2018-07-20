import struct
import numpy as np

MFER_TAG = {
    "endian": 0x01,
    "time": 0x85,
    "sampling_rate": 0x0B,
    "sampling_resolution": 0x0C,
    "type": 0x0A,
    "len_block": 0x04,
    "num_channel": 0x05,
    "num_sequence": 0x06,
    "ch_attribute": 0x3F,
    "waveform": 0x1E,
}

def int_format(length, signed=False):
    if signed:
        if length == 1: return 'b'
        if length == 2: return 'h'
        if length == 4: return 'i'
    else:
        if length == 1: return 'B'
        if length == 2: return 'H'
        if length == 4: return 'I'
    return None

class mfer(object):
    
    def __init__(self, path):
        self.path = path
        self.param = {}
        
        data = open(path, "rb").read()
        self.data = data
        
        pos = 0
        
        # Parse header info
        while True:

            tag = struct.unpack_from('B', data, pos)[0]
            pos+=1

            if tag == MFER_TAG['ch_attribute']:
                _tag = struct.unpack_from('B', data, pos)[0]
                pos+=1
                tag = tag*0x100+_tag

            if tag == MFER_TAG['waveform']: 
                pos -= 1
                break

            length = struct.unpack_from('B', data, pos)[0]
            pos+=1

            if length >= 0x80:
                byte_length = length - 0x80
                length = 0
                for _ in range(byte_length):
                    length *= 0x100
                    length += struct.unpack_from('B', data, pos)[0]
                    pos+=1

            #print("{:4X}:{:4X}".format(tag, length))
            
            for key,  t in MFER_TAG.items():
                if t == tag:
                    value = None

                    # parse value
                    if key == 'sampling_rate':
                        unit = struct.unpack_from('B', data, pos)[0]
                        pos += 1
                        exp = struct.unpack_from('b', data, pos)[0]
                        pos += 1
                        mnt = struct.unpack_from(int_format(length-2, signed=False), data, pos)[0]
                        if unit == 1:
                            value = 1./ (mnt*(10**exp))
                        pos -= 2

                    elif key == 'sampling_resolution':
                        unit = struct.unpack_from('B', data, pos)[0]
                        pos += 1
                        exp = struct.unpack_from('b', data, pos)[0]
                        pos += 1
                        mnt = struct.unpack_from(int_format(length-2, signed=False), data, pos)[0]
                        value = (10**exp) * mnt
                        pos -= 2

                    elif key == 'time':
                        assert length == 11
                        year = struct.unpack_from('H', data, pos)[0]
                        pos += 2
                        month = struct.unpack_from('B', data, pos)[0]
                        pos += 1
                        day = struct.unpack_from('B', data, pos)[0]
                        pos += 1
                        hour = struct.unpack_from('B', data, pos)[0]
                        pos += 1
                        minuite = struct.unpack_from('B', data, pos)[0]
                        pos += 1
                        second = struct.unpack_from('B', data, pos)[0]
                        pos += 1
                        millisecond = struct.unpack_from('H', data, pos)[0]
                        pos += 2
                        microsecond = struct.unpack_from('H', data, pos)[0]
                        pos += 2
                        value = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
                            year, month, day, hour, minuite, second
                        )
                        pos -= 11

                    elif key in ['endian','type']:
                        value = struct.unpack_from('B', data, pos)[0]

                    else:
                        value = struct.unpack_from('I', data, pos)[0]

                    print("{:}:{:}".format(key, value))
                    self.param[key] = value

            pos += length
            if(pos >= len(data)) : break
        
        print("... param load done")

        # Parse waveform data
        self.data = np.zeros( (1, self.param['num_channel']), dtype=np.int16)
        while True:
            
            tag = struct.unpack_from('B', data, pos)[0]
            pos+=1
            if tag != MFER_TAG['waveform']:
                pos -=1
                break
            
            length = struct.unpack_from('B', data, pos)[0]
            pos+=1
            if length >= 0x80:
                byte_length = length - 0x80
                length = 0
                for _ in range(byte_length):
                    length *= 0x100
                    length += struct.unpack_from('B', data, pos)[0]
                    pos+=1
            
            arr = np.zeros( (self.param['len_block'], self.param['num_channel']), dtype=np.int16)
            for c in range(self.param['num_channel']):
                for i in range(self.param['len_block']):
                    arr[i,c] = struct.unpack_from('h', data, pos)[0]
                    pos+=2
            self.data = np.concatenate((self.data, arr), axis=0)
                    
            if pos >= len(data): break
                
        self.data = self.data[1:,:]
        print("... waveform load done")
