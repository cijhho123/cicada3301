#!/usr/bin/env python3

###############################################################################
# Search and extract jpegs from a data file. All imput files are tested for   #
# JPG begin and end (ffd8 and ffd9) in normal and byte-reversed order. All    #
# jpgs that are found are saved. All bytes not in any of the jpgs are also    #
# reported.                                                                   #
###############################################################################

import imghdr
import argparse

JPEG_START = bytearray([int('ff',16),int('d8',16)])
JPEG_END   = bytearray([int('ff',16),int('d9',16)])
INVERT     = bytearray([int('ff',16)])[0]

class DetectJPG:
    def __init__(self,fname,bytemask=None):
        """fname must be a binary data file"""
        print()
        print('--------------------------------------------------------')
        print('DETECT_JPG: SEARCHING FOR JPGS IN BINARY DATA')
        print('--------------------------------------------------------')
        print()
        self.makeNames(fname)
        self.readBinaryData(fname)
        if bytemask != None:
            print(' --- inverting all bytes ---')
            self.maskBytes(bytemask)
        print()
        print(' --- scanning data ---')
        print()
        self.scanData()
        print()
        print(' --- reversing byte order ---')
        self.reverseByteOrder()
        print()
        print(' --- scanning data ---')
        print()
        self.scanData()
        print()
        print(' --- looking for bytes not used in jpegs ---')
        print()
        self.reverseByteOrder()
        self.saveRemainder()
        print()
        print(' --- Done ---')
        
        
    def makeNames(self,fname):
        """Make names for output jpgs and remaining bytes"""
        pos = fname.rfind('.')
        ending = fname[pos:]
        self.imagename = fname.replace(ending,'.image{0:02d}.jpg')
        self.restname = fname.replace(ending,'.remainder{0:02d}.bin')
        self.imgnumber = 0
        self.restnumber = 0
    
    def readBinaryData(self,fname):
        fd = open(fname,'rb')
        self.data = fd.read()
        fd.close()
        self.mask = [0 for i in range(len(self.data))]
        self.byteorder = 1
        print('Read {0} with {1:d} bytes'.format(fname,len(self.data)))
        
    def writeBinary(self,fname,data):
        fd = open(fname,'wb')
        fd.write(data)
        fd.close()
    
    def maskBytes(self,bytemask):
        masked_data = bytearray()
        for d in self.data:
            masked_data.append(d ^ bytemask)
        self.data = masked_data
        
    def reverseByteOrder(self):
        rev_data = bytearray()
        for i in range(len(self.data)-1,-1,-1):
            rev_data.append(self.data[i])
        self.data = rev_data
        self.byteorder *= -1
    
    def findJPG(self,offset=0):
        pos1 = self.data.find(JPEG_START,offset)
        pos2 = -1
        if pos1 != -1:
            pos2 = self.data.find(JPEG_END,pos1)
        if 0 <= pos1 < pos2:
            pic = imghdr.test_jpeg(self.data[pos1:pos2+len(JPEG_END)],None)
            if pic != 'jpeg':
                return [False,-1,-1]
            return [True,pos1,pos2+len(JPEG_END)]
        else:
            return [False,-1,-1]
     
    def scanData(self):
        offset = 0
        while True:
            img = self.findJPG(offset)
            if img[0] == False:
                break
            else:
                self.saveJPG(img)
                self.updateMask(img)
                offset = img[2]
                
    def saveJPG(self,img):
        """ Report and save detected jpg """
        imgname = self.imagename.format(self.imgnumber)
        self.imgnumber += 1
        print('Detected jpg. Begin: {0} End {1}'.format(img[1],img[2]))
        print('Saving as {0}'.format(imgname))
        self.writeBinary(imgname,self.data[img[1]:img[2]])
        
    def updateMask(self,img):
        """ Update mask of bytes used in legitimate JPGs """
        if self.byteorder == 1: # forward
            self.mask[img[1]:img[2]] = [1 for i in range(img[1],img[2])]
        else: # reversed byteorder
            self.mask[len(self.mask)-img[2]:len(self.mask)-img[1]] = \
                [1 for i in range(img[1],img[2])]
    
    def saveRemainder(self):
        offset = 0
        while True:
            rest = self.findUnusedBytes(offset)
            if rest[0] == False:
                break
            else:
                self.saveUnusedBytes(rest)
                offset = rest[2] + 1
                
    def saveUnusedBytes(self,rest):
        restname = self.restname.format(self.restnumber)
        self.restnumber += 1
        print('Bytes not used in jpgs. Begin: {0} End: {1}'.format(rest[1],rest[2]))
        print('Saving as {0}'.format(restname))
        self.writeBinary(restname,self.data[rest[1]:rest[2]])
                

    def findUnusedBytes(self,offset=0):
        try:
            pos1 = self.mask.index(0,offset)
        except ValueError:
            return [False,-1,-1]
        try:
            pos2 = self.mask.index(1,pos1)
        except ValueError:
            pos2 = len(self.mask) + 1
        return [True,pos1,pos2-1]
        
                
#==============================================================================

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Search binary data file for jpgs")
    parser.add_argument("-i","--infile",help="Input file. Will be searched for jpgs")
    parser.add_argument("--invert",help="Bytes in input file will be inverted before search",\
        action="store_true")
    args = parser.parse_args()

    if args.invert:
        bytemask = INVERT
    else:
        bytemask = None
    DetectJPG(args.infile,bytemask)