"""
Created on November 25, 2011

@author: sbobovyc
"""
"""   
    Copyright (C) 2011 Stanislav Bobovych

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import struct
import math
import Image

#TODO Add support to magick number 6 RGB4444
#TODO Add support to magick number 6 RGB565
#TODO Add support to magick number 5 RGB4444
#TODO Add support to magick number 5 RGB565
#TODO Add support to magick number 1 RGB565
#TODO Add support to magick number 1 RGB4444

RSB_debug = False
RSB_Magick1 = 1
RSB_Magick4 = 4
RSB_Magick5 = 5
RSB_Magick6 = 6
RSB_Magick9 = 9
RSB_Formats = {4444:"RGB4444", "RGB4444":4444,
               5650:"RGB565", "RGB565":5650, 
               8888:"RGB8888", "RGB8888":8888,
               8880:"RGB8880", "RGB8880":8880,
               655364444:"RGB655364444", "RGB655364444":655364444}               

RSB_Magic = {4444:RSB_Magick4, "RGB4444":RSB_Magick4,
             5650:RSB_Magick5, "RGB565":RSB_Magick5, 
             8888:RSB_Magick6, "RGB8888":RSB_Magick6,
             8880:RSB_Magick6, "RGB8880":RSB_Magick6,
             655364444:RSB_Magick9, "RGB655364444":RSB_Magick9}

RSB_Header_Offset = 0x1C

def int2bcd(integer):    
    a3 = integer/1000
    a2 = (integer - 1000*a3)/100
    a1 = (integer - 1000*a3 - 100* a2) / 10
    a0 = (integer - 1000*a3 - 100* a2 - 10*a1)
    
    return a3, a2, a1, a0

def float2int(flt):
    return int(math.ceil(flt))

class RSB_File:    
    
    #TODO make the constructor figure out if this is an image
    def __init__(self, filepath=None, peek=False, width=None, height=None, RSB_Format=None, PIL_buffer=None):
        self.filepath = filepath    
        self.width = width
        self.height = height
        self.RSB_Format = RSB_Format
        self.buffer = PIL_buffer
        self.magicNumber = None
        
        if self.filepath != None:
            self.open(self.filepath, peek)
        
    def new(self):
        pass
    
    def open(self, filepath=None, peek=False):
        if filepath == None and self.filepath == None:
            print "Filepath is empty"
            return
        if filepath == None:
            filepath = self.filepath
            
        with open(filepath, "rb") as f:
            f = f.read()
            self.magicNumber, = struct.unpack('<I',f[0:4])
            
            if self.magicNumber == RSB_Magick9:
                self.filepath = filepath
                self.width, = struct.unpack('<I',f[0x4:0x8])
                self.height, = struct.unpack('<I',f[0x8:0xC])                
                a4,a3,a2,a1,a0 = struct.unpack('<IIIII',f[0x0F:0x23])
                self.RSB_Format = int(str(a4) + str(a3) + str(a2) + str(a1) + str(a0))                
                
                if peek:                    
                    return
                
                #Convert RSB RGB4444 to PIL RGBA                                
                if RSB_Formats[self.RSB_Format] == RSB_Formats[655364444]:
                    self.buffer = Image.new("RGBA", (self.width, self.height))
                    pixels = self.buffer.load()
                    
                    for y in range(0, self.height):
                        for x in range(0, self.width):
                            index = 0x2B+self.width*y*2+x*2
                            if RSB_debug:
                                print hex(index), x,y
                            color, = struct.unpack('<H', f[index:index+2])
                            
                            alpha = float2int( ((color & 0xF000) >> 12) / 15.0 * 255.0 )
                            red = float2int( ((color & 0x0F00) >> 8) / 15.0 * 255.0 )
                            green = float2int( ((color & 0x00F0) >> 4) / 15.0 * 255.0 )
                            blue = float2int( (color & 0x000F) / 15.0 *255.0)
                            
                            print alpha,red,green,blue
                            pixels[x,y] = (red,green,blue,alpha)    

            elif self.magicNumber == RSB_Magick1 or self.magicNumber == RSB_Magick4 or self.magicNumber == RSB_Magick5 or self.magicNumber == RSB_Magick6:                
                self.filepath = filepath
                self.width, = struct.unpack('<I',f[0x4:0x8])
                self.height, = struct.unpack('<I',f[0x8:0xC])
                a3,a2,a1,a0 = struct.unpack('<IIII',f[0xC:0x1C])
                self.RSB_Format = int(str(a3) + str(a2) + str(a1) + str(a0))                
                
                if peek:
                    return
                # Convert from RGB565 to PIL RGB
                if RSB_Formats[self.RSB_Format] == RSB_Formats[5650]:
                    self.buffer = Image.new("RGB", (self.width, self.height))
                    pixels = self.buffer.load()
                    
                    for y in range(0, self.height):
                        for x in range(0, self.width):
                            index = RSB_Header_Offset+self.width*y*2+x*2
                            if RSB_debug:
                                print hex(index), x,y
                            color, = struct.unpack('<H', f[index:index+2])
                            #quick version
#                            red = (color & 0xF800) >> 7
#                            green = (color & 0x07E0) >> 2
#                            blue = (color & 0x001F) << 4                            
                            red = float2int( ((color & 0xF800) >> 11) / 31.0 * 255.0)
                            green = float2int( ((color & 0x07E0) >> 4) / 127.0 * 255.0)
                            blue = float2int( ((color & 0x001F))  / 31.0 * 255.0)
                                                        
                            #print red,green,blueh
                            pixels[x,y] = (red,green,blue)
                            
                #Convert RSB RGB8888 to PIL RGBA
                elif RSB_Formats[self.RSB_Format] == RSB_Formats[8888]:
                    self.buffer = Image.new("RGBA", (self.width, self.height))
                    pixels = self.buffer.load()
                    
                    for y in range(0, self.height):
                        for x in range(0, self.width):
                            index = RSB_Header_Offset+self.width*y*4+x*4
                            if RSB_debug:
                                print hex(index), x,y
                            color, = struct.unpack('<I', f[index:index+4])
                            
                            alpha = color & 0x000000FF 
                            red = (color & 0x0000FF00) >> 8
                            green = (color & 0x00FF0000) >> 16                        
                            blue = (color & 0xFF000000) >> 24                                                        
                            
                            #print red,green,blueh
                            pixels[x,y] = (red,green,blue,alpha)
                            
                #Convert RSB RGB8880 to PIL RGB
                elif RSB_Formats[self.RSB_Format] == RSB_Formats[8880]:
                    self.buffer = Image.new("RGB", (self.width, self.height))
                    pixels = self.buffer.load()
                    
                    for y in range(0, self.height):
                        for x in range(0, self.width):
                            index = RSB_Header_Offset+self.width*y*3+x*3                            
                            if RSB_debug:
                                print hex(index), x,y
                            red, = struct.unpack('<B', f[index])
                            green, = struct.unpack('<B', f[index+1])
                            blue, = struct.unpack('<B', f[index+2])                                                                                 
                            
                            #print red,green,blue
                            pixels[x,y] = (red,green,blue)
                                                        
                #Convert RSB RGB4444 to PIL RGBA
                elif RSB_Formats[self.RSB_Format] == RSB_Formats[4444]:
                    self.buffer = Image.new("RGBA", (self.width, self.height))
                    pixels = self.buffer.load()
                    
                    for y in range(0, self.height):
                        for x in range(0, self.width):
                            index = RSB_Header_Offset+self.width*y*2+x*2
                            if RSB_debug:
                                print hex(index), x,y
                            color, = struct.unpack('<H', f[index:index+2])
                            
                            alpha = float2int( ((color & 0xF000) >> 12) / 15.0 * 255.0 )
                            red = float2int( ((color & 0x0F00) >> 8) / 15.0 * 255.0 )
                            green = float2int( ((color & 0x00F0) >> 4) / 15.0 * 255.0 )
                            blue = float2int( (color & 0x000F) / 15.0 *255.0)
                            
                            pixels[x,y] = (red,green,blue,alpha)                                                                           
                else:
                    print "RSB type is not supported"                    
                    return
                    
            else:
                print "File is not of type RSB."
                return
    
    def rsb2img(self, filepath):
        self.open(self.filepath)
        
        # Handle the case where an image with an alpha channel needs to be saved to a
        # RSB_Format that does not have an alpha channel.
        try:            
            self.buffer.save(filepath)
            
        except:            
            new_buffer = self.buffer.convert("RGB")
            new_buffer.save(filepath)
            
    def img2rsb(self, RSB_Format, filepath_image, filepath_rsb):            
        self.buffer = Image.open(filepath_image)
        self.width,self.height = self.buffer.size
        self.save(RSB_Format, filepath_rsb)
        
    def is_format_supported(self, RSB_Format):
        return RSB_Formats.has_key(RSB_Format) 
    
    def save(self, RSB_Format, filepath):        
        if RSB_Format.isdigit():
            RSB_Format = int(RSB_Format)
                         
        if not self.is_format_supported(RSB_Format):            
            print "Unsupported RSB format."
            return
        
        if type(RSB_Format)== str:
            RSB_Format = RSB_Formats[RSB_Format]     
                       
        if RSB_Format <= 8888:
            a3,a2,a1,a0 = int2bcd(RSB_Format)
            self.magicNumber = RSB_Magic[RSB_Format] 
            header = (self.magicNumber, self.width, self.height, a3, a2, a1, a0)
            header_struct = struct.Struct('<IIIIIII')
        else:
            self.magicNumber = RSB_Magick9
            header = (self.magicNumber, self.width, self.height, 65536, 0x04, 0x04, 0x04, 0x04, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF)
            header_struct = struct.Struct('<IIIxxxIIIIIBBBBBBBB')
        header_packed = header_struct.pack(*header)

        print 'Header         :', header
        #print 'Format string  :', header_struct.RSB_Format
        #print 'Uses           :', header_struct.size, 'bytes'
        #print 'Packed Value   :', binascii.hexlify(header_packed) 
        
        data_struct = None      
        footer = ""
        
        if self.magicNumber == RSB_Magick6 and RSB_Format == 8880:
            for i in range(0, 0xF):
                footer += "%c" % 0x00
            footer += "%c%c%c%c%c" %(0x02, 0x00, 0x00, 0x00, 0x03)
            for i in range(0, 0x29):
                footer += "%c" % 0x00
            footer += "%c%c%c%c" % (0xFF, 0xFF, 0xFF, 0xFF)            
        elif self.magicNumber != RSB_Magick1 and self.magicNumber != RSB_Magick4 and self.magicNumber != RSB_Magick9:
            for i in range(0, 0xB):
                footer += "%c" % 0x00
            footer += "%c%c%c%c%c" %(0x02, 0x00, 0x00, 0x00, 0x03)
            for i in range(0, 0x29):
                footer += "%c" % 0x00
            footer += "%c%c%c%c" % (0xFF, 0xFF, 0xFF, 0xFF)
            
        elif self.magicNumber == RSB_Magick9:
            for i in range(0, 0x4):
                footer += "%c" % 0x00
            footer += "%c" % 0x1
            for i in range(0, 0xB):
                footer += "%c" % 0x00
            footer += "%c%c%c%c%c" %(0x02, 0x00, 0x00, 0x00, 0x03)
            for i in range(0, 0x29):
                footer += "%c" % 0x00
            footer += "%c%c%c%c" % (0xFF, 0xFF, 0xFF, 0xFF)
                    
        data = []
        # Convert from buffer to RGB565
        if RSB_Formats[RSB_Format] == RSB_Formats[5650]:
            pixels = self.buffer.load()
            
            for y in range(0, self.height):
                for x in range(0, self.width):
                    color = pixels[x,y]                                        
                    
                    red = color[0]
                    green = color[1]
                    blue = color[2]
                    #ignore alpha channel if it exists
                    
                    red5 = int((red / 255.0) * 31.0) << 11                                 
                    green6 = int((green / 255.0) * 127.0) << 4
                    blue5 = int((blue / 255.0) * 31.0)  
                    
                    color = red5 | green6 | blue5
                    data.append(color)
                    
            data_struct = struct.Struct("<%iH" % len(data))
        
        # Convert from PIL to RGB8888
        elif RSB_Formats[RSB_Format] == RSB_Formats[8888]:           
            pixels = self.buffer.load()
            
            for y in range(0, self.height):
                for x in range(0, self.width):                      
                    color = pixels[x,y]         
                    
                    alpha = color[3] if len(color) > 3 else 255                           
                    red = color[0]
                    green = color[1]
                    blue = color[2]
                    
                    data.append(alpha)
                    data.append(red)                    
                    data.append(green)
                    data.append(blue)
                                                                            
            data_struct = struct.Struct("<%iB" % len(data))
            
        # Convert from PIL to RGB8880
        elif RSB_Formats[RSB_Format] == RSB_Formats[8880]:           
            pixels = self.buffer.load()
            
            for y in range(0, self.height):
                for x in range(0, self.width):                      
                    color = pixels[x,y]         
                                             
                    red = color[0]
                    green = color[1]
                    blue = color[2]
                    
                    #print red,green,blue
                    data.append(red)                    
                    data.append(green)
                    data.append(blue)
                                                                            
            data_struct = struct.Struct("<%iB" % len(data))
            
        # Convert from buffer to RGB4444
        elif RSB_Formats[RSB_Format] == RSB_Formats[4444]:
            pixels = self.buffer.load()
            
            for y in range(0, self.height):
                for x in range(0, self.width):
                    color = pixels[x,y]

                    alpha = color[3] if len(color) > 3 else 255                           
                    red = color[0]
                    green = color[1]
                    blue = color[2]
                    
                    alpha = int((alpha / 255.0) * 15.0) << 12
                    red = int((red / 255.0) * 15.0) << 8                          
                    green = int((green / 255.0) * 15.0) << 4
                    blue = int((blue / 255.0) * 15.0) 
                                        
                    color = alpha | red | green | blue 
                    data.append(color)
                    
            data_struct = struct.Struct("<%iH" % len(data))
            
        elif RSB_Formats[RSB_Format] == RSB_Formats[655364444]:
            pixels = self.buffer.load()
            
            for y in range(0, self.height):
                for x in range(0, self.width):
                    color = pixels[x,y]

                    alpha = color[3] if len(color) > 3 else 255                           
                    red = color[0]
                    green = color[1]
                    blue = color[2]
                    
                    alpha = int((alpha / 255.0) * 15.0) << 12
                    red = int((red / 255.0) * 15.0) << 8                          
                    green = int((green / 255.0) * 15.0) << 4
                    blue = int((blue / 255.0) * 15.0) 
                                        
                    color = alpha | red | green | blue
                    print "alpha",hex(alpha) 
                    print "red", hex(red)
                    print "green", hex(green)
                    print hex(color)
                    data.append(color)
                    
            data_struct = struct.Struct("<%iH" % len(data))                    
        else:
            print "File is not of type RSB."
            return

     
        data_packed = data_struct.pack(*data)            
        #print 'Data RSB_Format string  :', data_struct.RSB_Format
        print 'Data uses      :', data_struct.size, 'bytes'            
        print 
                               
        with open(filepath, "wb") as f:        
            f.write(header_packed)
            f.write(data_packed)            
            f.write(footer)
    
    #TODO optimize so that the function can just look at the f header intead of
    # fully opening the f
    def info(self):
        try:
            return "File: %s\nRSB Magick: %i, Format: %s, Width: %i, Height: %i" % (self.filepath, self.magicNumber, RSB_Formats[self.RSB_Format], self.width, self.height)
        except:
            return "File is not formatted correctly or is not supported"
        
    def __str__(self):
        return self.info()



