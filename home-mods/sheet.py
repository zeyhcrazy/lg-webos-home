import sys
from PIL import Image, ImageDraw
out=sys.argv[1]; pairs=[a.split('=',1) for a in sys.argv[2:]]
ims=[(l,Image.open(f).convert('RGB').crop((0,0,1920,600)).resize((960,300))) for f,l in pairs]
sheet=Image.new('RGB',(960,len(ims)*330),(40,40,40)); d=ImageDraw.Draw(sheet)
for i,(l,im) in enumerate(ims):
    sheet.paste(im,(0,i*330+28)); d.text((8,i*330+6),l,fill=(255,255,0))
sheet.save(out)
