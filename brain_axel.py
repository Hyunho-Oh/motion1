"""Generate an original 30s Brain Axel kinetic typography spot and soundtrack."""
import math, os, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT=os.path.abspath(os.path.dirname(__file__))
FPS=30; SECONDS=30; FRAMES=FPS*SECONDS; SR=44100; BPM=144; BEAT=60/BPM
VW,VH=1280,720
OUT_MP4=os.path.join(ROOT,'brain_axel_30s.mp4')
OUT_WAV=os.path.join(ROOT,'brain_axel_music.wav')

def font(size,bold=True):
    path=r'C:\Windows\Fonts\malgunbd.ttf' if bold else r'C:\Windows\Fonts\malgun.ttf'
    return ImageFont.truetype(path,size)

def add_event(dst,start,samples):
    a=max(0,int(round(start*SR))); b=min(len(dst),a+len(samples))
    if b>a: dst[a:b]+=samples[:b-a]

def make_music():
    n=SR*SECONDS; mono=np.zeros(n,dtype=np.float64); rng=np.random.default_rng(144)
    # Four-on-the-floor kick with breakbeat clap and crisp offbeat hats.
    for bi in range(int(SECONDS/BEAT)):
        t=bi*BEAT; q=np.arange(int(.22*SR))/SR
        freq=96-53*np.minimum(q/.19,1)
        add_event(mono,t,.42*np.sin(2*np.pi*freq*q)*np.exp(-q*19))
        if bi%4 in (1,3):
            q=np.arange(int(.16*SR))/SR; noise=rng.normal(0,1,len(q))
            clap=(.13*noise+.06*np.sin(2*np.pi*210*q))*np.exp(-q*23)
            add_event(mono,t,clap)
        for off,level in ((0,.045),(.5,.032)):
            s=t+off*BEAT
            if s>=SECONDS: continue
            q=np.arange(int(.042*SR))/SR; noise=rng.normal(0,1,len(q))
            add_event(mono,s,level*noise*np.exp(-q*83))
    # Bright chord stabs, bouncy bass, and an original hook melody.
    chords=[[261.63,329.63,392.00],[196.00,246.94,293.66],[220.00,261.63,329.63],[174.61,220.00,261.63]]
    for bar in range(18):
        s=bar*4*BEAT; chord=chords[bar%4]
        for f in chord:
            q=np.arange(int(.54*SR))/SR
            env=np.minimum(1,q/.012)*np.exp(-q*4.3)
            sig=(.045*np.sin(2*np.pi*f*q)+.015*np.sin(4*np.pi*f*q))*env
            add_event(mono,s,sig)
    roots=[65.41,49.00,55.00,43.65]
    melody=[523.25,659.25,783.99,659.25,587.33,698.46,880.00,698.46]
    for bi in range(int(SECONDS/BEAT)):
        s=bi*BEAT
        q=np.arange(int(.32*SR))/SR
        root=roots[(bi//4)%4]
        bass=(.17*np.sin(2*np.pi*root*q)+.035*np.sin(4*np.pi*root*q))*np.exp(-q*7)
        add_event(mono,s,bass)
        if bi%2==0:
            f=melody[(bi//2)%len(melody)]
            q=np.arange(int(.18*SR))/SR
            pluck=(np.sin(2*np.pi*f*q)+.23*np.sin(4*np.pi*f*q)+.09*np.sin(6*np.pi*f*q))*np.exp(-q*13)
            add_event(mono,s,pluck*.10)
    # Two short synthesized risers into the scene changes and a final sting.
    for start in (9.35,19.35,28.85):
        length=int(.62*SR); q=np.arange(length)/SR
        sweep=350+1650*(q/.62)
        phase=2*np.pi*np.cumsum(sweep)/SR
        add_event(mono,start,.055*np.sin(phase)*(q/.62)**1.5)
    t=np.arange(n)/SR
    fade=np.minimum(1,t/.24)*np.minimum(1,(SECONDS-t)/.72)
    mono*=fade
    peak=np.max(np.abs(mono)); mono*=.86/max(peak,1e-9)
    stereo=np.column_stack([mono,np.roll(mono,193)*.97])
    pcm=(stereo*32767).astype('<i2')
    with wave.open(OUT_WAV,'wb') as wf:
        wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR); wf.writeframes(pcm.tobytes())

def make_background():
    im=Image.new('RGB',(VW,VH)); p=im.load()
    top=(17,12,41); bottom=(47,19,73)
    for y in range(VH):
        q=y/(VH-1)
        c=tuple(int(top[i]*(1-q)+bottom[i]*q) for i in range(3))
        for x in range(VW): p[x,y]=c
    layer=Image.new('RGBA',(VW,VH),(0,0,0,0)); g=ImageDraw.Draw(layer)
    g.ellipse((790,-270,1460,390),fill=(206,54,68,46))
    g.ellipse((-330,370,500,1160),fill=(155,248,63,24))
    layer=layer.filter(ImageFilter.GaussianBlur(88))
    im=Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB')
    d=ImageDraw.Draw(im,'RGBA')
    for x in range(0,VW,64): d.line((x,0,x,VH),fill=(205,205,255,13),width=1)
    for y in range(0,VH,64): d.line((0,y,VW,y),fill=(205,205,255,13),width=1)
    d.rounded_rectangle((28,28,VW-28,VH-28),radius=22,outline=(210,205,244,54),width=2)
    return im

BG=make_background()
F_HEAD=font(25,True); F_SMALL=font(18,True); F_MID=font(48,True)
F_HERO=font(108,True); F_HERO2=font(92,True); F_FOOT=font(17,True)
LIME=(188,255,54,255); CORAL=(255,101,77,255); WHITE=(250,247,255,255); MUTED=(205,197,224,255)

def center(d,text,y,f,fill,stroke=0,stroke_fill=(15,9,32,255),x=VW//2):
    d.text((x,y),text,font=f,fill=fill,anchor='mm',stroke_width=stroke,stroke_fill=stroke_fill)

def label(d,scene,sec,beat_pulse):
    d.rounded_rectangle((58,54,287,96),radius=20,fill=(188,255,54,255))
    d.text((78,62),'BRAIN AXEL',font=F_SMALL,fill=(21,15,39,255))
    d.text((302,62),'MOTION STUDY  /  144 BPM',font=F_SMALL,fill=(207,199,228,225))
    d.rounded_rectangle((1080,54,1219,96),radius=20,fill=(255,101,77,235))
    d.ellipse((1097,68,1111,82),fill=(255,250,244,255))
    d.text((1121,61),'SCENE 0'+str(scene+1),font=F_SMALL,fill=(255,250,244,255))
    # Thin progress rail advances exactly once per 10-second act.
    d.rounded_rectangle((58,632,1222,640),radius=4,fill=(255,255,255,40))
    seg=(1222-58)/3
    d.rounded_rectangle((58,632,58+seg*scene+seg*(min(sec,10)/10),640),radius=4,fill=(188,255,54,225))

def draw_frame(frame):
    t=frame/FPS; scene=min(2,int(t//10)); local=t-scene*10
    im=BG.copy(); d=ImageDraw.Draw(im,'RGBA')
    beat=math.sin(2*math.pi*t/BEAT)
    pulse=(1+beat)/2
    label(d,scene,local,pulse)
    if scene==0:
        if local<3.2:
            k=max(0,min(1,local/.8)); txt='오늘은 조용히…'
            center(d,txt,300+int((1-k)*22),F_HERO2,(255,247,235,int(255*k)),2)
            center(d,'아주 평범한 스크롤의 시작',382,F_SMALL,MUTED)
        elif local<6.65:
            center(d,'그냥 한 번만',286,F_HERO2,WHITE,2)
            center(d,'더 보고 끄자.',374,F_HERO2,CORAL,2)
            # A tiny indicator hints at acceleration.
            for i in range(5):
                alpha=int(80+150*((i/4)<(local-3.2)/3.45))
                d.rounded_rectangle((524+i*50,470,562+i*50,486),radius=7,fill=(188,255,54,alpha))
        else:
            scale=1+0.11*pulse
            center(d,'…보다가?',288,F_HERO, LIME if pulse>.5 else WHITE,3)
            center(d,'발끝이 먼저 움직였다',383,F_MID,MUTED)
            # Original accelerator pedal icon, drawn from geometric shapes.
            d.rounded_rectangle((570,460,710,515),radius=12,fill=(255,101,77,230))
            for y in (472,486,500): d.line((590,y,690,y),fill=(255,235,220,145),width=3)
            d.rounded_rectangle((727,453,736,523),radius=4,fill=(255,255,255,75))
    elif scene==1:
        # Speed lines live in the margins so the Korean lettering remains clear.
        for i in range(11):
            yy=140+i*38
            shift=int((t*420+i*121)%180)
            d.line((30+shift,yy,230+shift,yy),fill=(188,255,54,65),width=3)
            d.line((VW-250-shift,yy+17,VW-40-shift,yy+17),fill=(255,101,77,60),width=2)
        center(d,'브레인',254,F_HERO,(255,101,77,95),3,x=VW//2+7)
        center(d,'브레인',246,F_HERO,WHITE,3)
        # Main catchphrase lands on a beat at the exact act transition.
        if local<2.45:
            center(d,'악셀',374,F_HERO,LIME,3)
        elif local<4.75:
            center(d,'생각도',382,F_HERO2,WHITE,3)
            center(d,'드립도',476,F_HERO2,LIME,3)
        elif local<7.1:
            center(d,'풀가속!',405,F_HERO,CORAL,4)
        else:
            center(d,'한 번 밟으면',350,F_HERO2,WHITE,3)
            center(d,'생각도 드립도 풀가속!',438,F_MID,LIME,2)
    else:
        # The final act increases visual density, then resolves into a readable lockup.
        if local<2.6:
            for j in range(3):
                x=VW//2 + int(math.sin(t*5+j*2.1)*280)
                y=280+j*90+int(math.cos(t*4+j)*22)
                center(d,'밈!',y,F_HERO2,(188,255,54,210),2,x=x)
            center(d,'밈! 밈! 밈!',468,F_MID,WHITE,2)
        elif local<5.2:
            center(d,'생각도',315,F_HERO2,WHITE,2)
            center(d,'드립도',415,F_HERO2,CORAL,2)
            center(d,'속도 UP',500,F_SMALL,LIME)
        elif local<7.25:
            center(d,'풀가속—',365,F_HERO,LIME,4)
            for i in range(8):
                x=160+i*136
                d.rounded_rectangle((x,475,x+82,485),radius=5,fill=(255,101,77,int(90+140*pulse)))
        else:
            # Final title is stable and high contrast for the closing 2.75 seconds.
            if local<7.48:
                center(d,'브레인 악셀',354,F_HERO2,WHITE,4)
            else:
                d.rounded_rectangle((312,266,968,454),radius=34,fill=(188,255,54,255))
                center(d,'브레인 악셀',326,F_HERO2,(24,15,43,255),1)
                center(d,'ON',423,F_HERO2,(255,101,77,255),1)
            center(d,'한 번 밟으면 생각도 드립도 풀가속!',506,F_SMALL,MUTED)
    # Footer timecode and a tiny beat marker.
    d.text((58,663),'BRAIN AXEL  ·  ORIGINAL TYPE + SOUND',font=F_FOOT,fill=(205,197,224,185))
    d.text((1162,663),f'00:{int(t):02d}',font=F_FOOT,fill=(250,247,255,210),anchor='ra')
    marker_x=58+int((1222-58)*((t%BEAT)/BEAT))
    d.ellipse((marker_x-4,628,marker_x+4,644),fill=(255,101,77,255))
    return im.convert('RGB')

def render_mp4():
    sys.path.insert(0,os.path.join(ROOT,'.motiondeps'))
    import imageio_ffmpeg
    exe=imageio_ffmpeg.get_ffmpeg_exe()
    cmd=[exe,'-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{VW}x{VH}','-r',str(FPS),'-i','pipe:0','-i',OUT_WAV,
         '-t','30','-map','0:v:0','-map','1:a:0','-vf','scale=1920:1080:flags=lanczos','-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','-r','30','-c:a','aac','-b:a','192k','-ar','44100','-movflags','+faststart',OUT_MP4]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
    try:
        for i in range(FRAMES):
            proc.stdin.write(draw_frame(i).tobytes())
            if i and i%150==0: print(f'Rendered {i}/{FRAMES} frames',flush=True)
    except Exception:
        proc.kill(); raise
    finally:
        if proc.stdin: proc.stdin.close()
    err=proc.stderr.read().decode('utf-8','replace')
    code=proc.wait()
    if code: raise RuntimeError('ffmpeg failed: '+err[-3000:])

if __name__=='__main__':
    print('Composing original 144 BPM music...',flush=True)
    make_music()
    print('Rendering synchronized 30 second motion graphic...',flush=True)
    render_mp4()
    print('Finished:',OUT_MP4,os.path.getsize(OUT_MP4),'bytes')

