import math, os, struct, wave, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = os.path.abspath(os.path.dirname(__file__))
W, H, FPS, SECS = 540, 960, 20, 10
NFR = FPS * SECS

def font(size, bold=False):
    p = r'C:\Windows\Fonts\malgunbd.ttf' if bold else r'C:\Windows\Fonts\malgun.ttf'
    return ImageFont.truetype(p, size)

def smooth(x):
    x=max(0,min(1,x)); return x*x*(3-2*x)

# Music: original, gentle carol-like bell melody over warm strings.
SR=44100
N=SR*SECS
t=np.arange(N,dtype=np.float64)/SR
audio=np.zeros(N,dtype=np.float64)
def add_tone(freq, start, dur, amp, decay=2.5, vibrato=0):
    i0=max(0,int(start*SR)); i1=min(N,int((start+dur)*SR))
    tt=np.arange(i1-i0)/SR
    env=np.minimum(1,tt/.025)*np.exp(-decay*tt)*np.minimum(1,np.maximum(0,(dur-tt)/.09))
    phase=2*np.pi*freq*tt + vibrato*np.sin(2*np.pi*4.3*tt)
    audio[i0:i1] += amp*env*(np.sin(phase)+.22*np.sin(2*phase)+.08*np.sin(3*phase))

# Chords: C, Am, F, G, C; soft sustained triads, each two seconds.
chords=[[261.63,329.63,392.00],[220,261.63,329.63],[174.61,220,261.63],[196,246.94,293.66],[261.63,329.63,392.00]]
for ci, chord in enumerate(chords):
    start=ci*2
    for f in chord:
        add_tone(f,start,2.3,.065,decay=.38,vibrato=.018)
        add_tone(f*2,start+.015,2.1,.018,decay=.48,vibrato=.018)
# Original melody (notes and durations), bell-like.
mel=[(523.25,.1,.42),(659.25,.6,.42),(783.99,1.1,.62),(659.25,1.85,.38),(587.33,2.35,.42),(523.25,2.85,.4),(392,3.35,.64),(440,4.1,.4),(523.25,4.6,.42),(587.33,5.1,.62),(523.25,5.85,.4),(493.88,6.35,.42),(440,6.85,.4),(392,7.35,.62),(523.25,8.1,.42),(659.25,8.6,.42),(783.99,9.1,.72)]
for f,s,d in mel:
    add_tone(f,s,d,.18,decay=3.2)
    add_tone(f*2,s,d,.045,decay=4.4)
# Soft sleigh-like high shimmer, deliberately restrained.
for s in np.arange(.28,9.9,.5):
    add_tone(1567.98,float(s),.12,.018,decay=10)
# Subtle low pulse on chord roots.
for i,root in enumerate([130.81,110,87.31,98,130.81]):
    add_tone(root,i*2,.8,.07,decay=1.3)
# Fade in/out and gentle stereo width.
fade=np.minimum(1,t/.45)*np.minimum(1,(SECS-t)/.75)
audio*=fade
peak=np.max(np.abs(audio)); audio=audio*(.88/peak)
stereo=np.column_stack([audio, np.roll(audio, 350)*.96])
pcm=(stereo*32767).astype('<i2').tobytes()
wavpath=os.path.join(OUT,'year_end_carol.wav')
with wave.open(wavpath,'wb') as wf:
    wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR); wf.writeframes(pcm)

# Visual design: midnight winter palette, gold typography, subtle light and snow.
bg=Image.new('RGB',(W,H)); px=bg.load()
for y in range(H):
    q=y/H
    c=(int(8+7*q), int(21+13*q), int(44+18*q))
    for x in range(W): px[x,y]=c
glow=Image.new('RGBA',(W,H),(0,0,0,0)); gd=ImageDraw.Draw(glow)
gd.ellipse((65,110,475,520), fill=(201,151,68,28)); glow=glow.filter(ImageFilter.GaussianBlur(95))
bg=Image.alpha_composite(bg.convert('RGBA'),glow)
# Fine vertical strands of warm lights near the edges.
lights=[]
rng=random.Random(18)
for i in range(22):
    x=rng.choice([rng.randint(18,66),rng.randint(W-66,W-18)])
    y=rng.randint(75,H-90); r=rng.choice([1,1,2])
    lights.append((x,y,r,(255,202,112,rng.randint(45,95))))
snow=[]
for i in range(46):
    snow.append(((i*113+29)%W,(i*197+83)%H,1+(i%3),.65+(i%4)*.18))
scenes=[
    ('한 해의 끝에', '조용히 내려앉는 마음', '01'),
    ('조금 느려진', '나의 걸음', '02'),
    ('창밖엔 첫눈', '방 안엔 작은 불빛', '03'),
    ('고마웠던 순간들이', '하나둘 떠오르고', '04'),
    ('다가오는 새해에도', '우리의 온기가 계속되길', '05'),
]
def centered(draw, text, y, f, fill, stroke=0):
    box=draw.textbbox((0,0),text,font=f,stroke_width=stroke)
    draw.text(((W-(box[2]-box[0]))/2,y),text,font=f,fill=fill,stroke_width=stroke,stroke_fill=(6,17,36,220))

frames=[]
for fi in range(NFR):
    sec=fi/FPS; si=min(4,int(sec//2)); local=sec-si*2
    base=bg.copy(); d=ImageDraw.Draw(base,'RGBA')
    # Slowly drifting snow and pinprick lights.
    for j,(x,y,r,a) in enumerate(snow):
        yy=(y+sec*(13+j%9))%H; xx=(x+math.sin(sec*.48+j)*8)%W
        if 112 < xx < W-112 and 350 < yy < 555: continue
        d.ellipse((xx-r,yy-r,xx+r,yy+r),fill=(225,239,255,int(155*a)))
    for j,(x,y,r,col) in enumerate(lights):
        pulse=.62+.38*math.sin(sec*2+j*1.7)
        alpha=int(col[3]*pulse)
        d.ellipse((x-r,y-r,x+r,y+r),fill=(col[0],col[1],col[2],alpha))
    # Delicate framing ornaments.
    d.line((52,180,52,770),fill=(218,178,104,75),width=1); d.line((W-52,180,W-52,770),fill=(218,178,104,75),width=1)
    d.ellipse((W//2-5,207,W//2+5,217),fill=(245,205,132,190))
    d.line((W//2,218,W//2,258),fill=(245,205,132,100),width=1)
    # Scene typography reveals with a gentle upward float and fade.
    intro=smooth(local/.42); outro=smooth((2-local)/.34); alpha=int(255*intro*outro)
    float_y=int((1-intro)*24)
    main,sub,num=scenes[si]
    centered(d,num,294,font(14,True),(232,194,128,int(alpha*.72)))
    centered(d,main,386+float_y,font(40 if len(main)<10 else 34,True),(255,238,194,alpha),1)
    centered(d,sub,458+float_y,font(24),(226,231,239,int(alpha*.92)))
    # A restrained underline draws on per scene.
    linew=int(74*smooth(local/.6)); d.line((W//2-linew,535,W//2+linew,535),fill=(231,190,115,int(alpha*.8)),width=2)
    if si==4:
        a=int(235*intro*outro)
        centered(d,'새해에도, 따뜻하게',601+float_y,font(21,True),(246,205,131,a))
        centered(d,'MERRY & BRIGHT',680+float_y,font(16,True),(247,239,220,int(a*.85)))
    # Small footer mark, consistent throughout.
    centered(d,'DECEMBER  ·  A QUIET WISH',850,font(11,True),(198,207,220,110))
    # Convert each frame to adaptive palette for compact GIF fallback.
    frames.append(base.convert('RGB'))

# Save lightweight animated GIF preview alongside master video.
gifpath=os.path.join(OUT,'year_end_kinetic_typography.gif')
palframes=[]
for fr in frames:
    palframes.append(fr.quantize(colors=160,method=Image.Quantize.MEDIANCUT))
palframes[0].save(gifpath,save_all=True,append_images=palframes[1:],duration=50,loop=0,optimize=True,disposal=2)

# Minimal AVI muxer: MJPEG video + stereo PCM audio in a single, portable file.
def chunk(tag,data):
    return tag+struct.pack('<I',len(data))+data+(b'\0' if len(data)&1 else b'')
def listchunk(kind,data): return b'LIST'+struct.pack('<I',len(data)+4)+kind+data
def avih():
    return struct.pack('<14I',int(1e6/FPS),W*H*3*FPS,0,0x10,NFR,0,2,0,W,H,0,0,0,0)
def strh(typ,handler,scale,rate,length,suggested,quality,sample_size,rect):
    return struct.pack('<4s4sIHH8I4h',typ,handler,0,0,0,0,scale,rate,0,length,suggested,quality,sample_size,*rect)
def bitmapinfo():
    return struct.pack('<IiiHH4sIiiII',40,W,H,1,24,b'MJPG',W*H*3,0,0,0,0)
def wavefmt(): return struct.pack('<HHIIHH',1,2,SR,SR*4,4,16)
vidstr=listchunk(b'strl',chunk(b'strh',strh(b'vids',b'MJPG',1,FPS,NFR,W*H*3,0xFFFFFFFF,0,(0,0,W,H)))+chunk(b'strf',bitmapinfo()))
audlen=len(pcm)//4
audstr=listchunk(b'strl',chunk(b'strh',strh(b'auds',b'\0\0\0\0',4,SR*4,audlen,SR*4,0xFFFFFFFF,4,(0,0,0,0)))+chunk(b'strf',wavefmt()))
hdrl=listchunk(b'hdrl',chunk(b'avih',avih())+vidstr+audstr)
movichunks=[]; index=[]; offset=4
audio_bytes_per_sec=SR*4
for fi,fr in enumerate(frames):
    import io
    b=io.BytesIO(); fr.save(b,format='JPEG',quality=83,optimize=True)
    dat=b.getvalue(); c=chunk(b'00dc',dat); movichunks.append(c); index.append((b'00dc',0x10,offset,len(dat))); offset+=len(c)
    if (fi+1)%FPS==0:
        a0=(fi+1-FPS)*audio_bytes_per_sec//FPS; a1=(fi+1)*audio_bytes_per_sec//FPS
        ad=pcm[a0:a1]; c=chunk(b'01wb',ad); movichunks.append(c); index.append((b'01wb',0,offset,len(ad))); offset+=len(c)
movi_data=b''.join(movichunks)
idx=b''.join(tag+struct.pack('<3I',flags,pos,size) for tag,flags,pos,size in index)
avi=b'RIFF'+struct.pack('<I',4+len(hdrl)+8+len(movi_data)+8+len(idx))+b'AVI '+hdrl+listchunk(b'movi',movi_data)+chunk(b'idx1',idx)
avipath=os.path.join(OUT,'year_end_kinetic_typography.avi')
with open(avipath,'wb') as f: f.write(avi)
print('Created:')
for p in (avipath,gifpath,wavpath): print(p,os.path.getsize(p))

