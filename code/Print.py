from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

from escpos.printer import Usb

printWidth = 576
tmpImage = 'img-tmp.png'
fontPathBold = "bold-font.ttf"
fontPath = "regular-font.ttf"

p = Usb(0x04b8, 0x0e28, 0, profile="TM-T20II")
p.set(align="center")

def printHeader ():
    printHeight = 52
    fontSize = 52

    img = Image.new('RGB', (printWidth, printHeight), color = (255, 255, 255))
    drw = ImageDraw.Draw(img)
    drw.text((printWidth/2, 0), "Wireless Voucher", fill=(0,0,0), font=ImageFont.truetype(fontPathBold, fontSize), anchor="mt")
    img.save(tmpImage)

    p.ln(1)
    p.image(tmpImage)

def printTitle (titleText):
    printHeight = 52
    fontSize = 32

    img = Image.new('RGB', (printWidth, printHeight), color = (255, 255, 255))
    drw = ImageDraw.Draw(img)
    drw.text((0, 0), titleText, fill=(0,0,0), font=ImageFont.truetype(fontPathBold, fontSize))
    img.save(tmpImage)

    p.ln(1)
    p.image(tmpImage)

def printInfo (infoText):
    printHeight = 50
    fontSize = 52

    img = Image.new('RGB', (printWidth, printHeight), color = (255, 255, 255))
    drw = ImageDraw.Draw(img)
    drw.text((printWidth/2, 0), infoText, fill=(0,0,0), font=ImageFont.truetype(fontPath, fontSize), anchor="mt")
    img.save(tmpImage)

    p.image(tmpImage)
    
def printFooter (footerText):
    printHeight = 32
    fontSize = 24

    img = Image.new('RGB', (printWidth, printHeight), color = (255, 255, 255))
    drw = ImageDraw.Draw(img)
    drw.text((printWidth/2, 0), footerText, fill=(0,0,0), font=ImageFont.truetype(fontPath, fontSize), anchor="mt")
    img.save(tmpImage)

    p.image(tmpImage)

def printVoucher (vLogo, vNetworkName, vNetowrkPassword, vVoucher, vNote, vExpireNote):
    p.image(vLogo)
    printHeader()
    printTitle("Network Name")
    printInfo(vNetworkName)
    printTitle("Network Password")
    printInfo(vNetowrkPassword)
    printTitle("Voucher Code")
    printInfo(vVoucher)
    p.qr(f"WIFI:S:{vNetworkName};T:WPA;P:{vNetowrkPassword};;",size=6)
    printFooter("Valid for 24h after first use.")
    printFooter(vNote)
    p.ln(1)
    printFooter(vExpireNote)
    p.cut()
