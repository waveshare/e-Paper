# *****************************************************************************
# * | File        :	  epd2in13bc.py
# * | Author      :   Waveshare team
# * | Function    :   Electronic paper driver
# * | Info        :
# *----------------
# * | This version:   V4.0
# * | Date        :   2019-06-20
# # | Info        :   python demo
# -----------------------------------------------------------------------------
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documnetation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to  whom the Software is
# furished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS OR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import logging
from . import epdconfig

# Display resolution
EPD_WIDTH       = 104
EPD_HEIGHT      = 212

class EPD:
    def __init__(self):
        self.busy_pin = epdconfig.BUSY_PIN
        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT 
        
    def ReadBusy(self):
        logging.debug("e-Paper busy")
        epdconfig.send_command(0x71);
        while(epdconfig.digital_read(self.busy_pin) == 0): 
            epdconfig.send_command(0x71);
            epdconfig.delay_ms(100)
        logging.debug("e-Paper busy release")

    def init(self):
        if (epdconfig.module_init() != 0):
            return -1
            
        epdconfig.reset(200, 2, 200)
        epdconfig.send_command(0x04);  
        self.ReadBusy();#waiting for the electronic paper IC to release the idle signal

        epdconfig.send_command(0x00);    #panel setting
        epdconfig.send_data(0x0f);   #LUT from OTP,128x296
        epdconfig.send_data(0x89);    #Temperature sensor, boost and other related timing settings

        epdconfig.send_command(0x61);    #resolution setting
        epdconfig.send_data (0x68);  
        epdconfig.send_data (0x00);  
        epdconfig.send_data (0xD4);

        epdconfig.send_command(0X50);    #VCOM AND DATA INTERVAL SETTING
        epdconfig.send_data(0x77);   #WBmode:VBDF 17|D7 VBDW 97 VBDB 57
                            # WBRmode:VBDF F7 VBDW 77 VBDB 37  VBDR B7
        
        return 0

    def getbuffer(self, image):
        # logging.debug("bufsiz = ",int(self.width/8) * self.height)
        buf = [0xFF] * (int(self.width/8) * self.height)
        image_monocolor = image.convert('1')
        imwidth, imheight = image_monocolor.size
        pixels = image_monocolor.load()
        # logging.debug("imwidth = %d, imheight = %d",imwidth,imheight)
        if(imwidth == self.width and imheight == self.height):
            logging.debug("Vertical")
            for y in range(imheight):
                for x in range(imwidth):
                    # Set the bits for the column of pixels at the current position.
                    if pixels[x, y] == 0:
                        buf[int((x + y * self.width) / 8)] &= ~(0x80 >> (x % 8))
        elif(imwidth == self.height and imheight == self.width):
            logging.debug("Horizontal")
            for y in range(imheight):
                for x in range(imwidth):
                    newx = y
                    newy = self.height - x - 1
                    if pixels[x, y] == 0:
                        buf[int((newx + newy*self.width) / 8)] &= ~(0x80 >> (y % 8))
        return buf

    def display(self, imageblack, imagered):
        epdconfig.send_command(0x10)
        for i in range(0, int(self.width * self.height / 8)):
            epdconfig.send_data(imageblack[i])
        
        epdconfig.send_command(0x13)
        for i in range(0, int(self.width * self.height / 8)):
            epdconfig.send_data(imagered[i])
        
        epdconfig.send_command(0x12) # REFRESH
        epdconfig.delay_ms(100)
        self.ReadBusy()
        
    def Clear(self):
        epdconfig.send_command(0x10)
        for i in range(0, int(self.width * self.height / 8)):
            epdconfig.send_data(0xFF)
        
        epdconfig.send_command(0x13)
        for i in range(0, int(self.width * self.height / 8)):
            epdconfig.send_data(0xFF)
        
        epdconfig.send_command(0x12) # REFRESH
        epdconfig.delay_ms(100)
        self.ReadBusy()

    def sleep(self):
        epdconfig.send_command(0X50) 
        epdconfig.send_data(0xf7)
        epdconfig.send_command(0X02) 
        self.ReadBusy()
        epdconfig.send_command(0x07) # DEEP_SLEEP
        epdconfig.send_data(0xA5) # check code
        
        epdconfig.delay_ms(2000)
        epdconfig.module_exit()
### END OF FILE ###

