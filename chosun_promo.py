"""Create a 30-second 16:9 kinetic type promo with original beat-synced music."""
import io, math, os, random, struct, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.abspath(os.path.dirname(__file__))
W, H, FPS, SECONDS = 1280, 720, 24, 30
FRAMES = FPS * SECONDS
SR, BPM = 44100, 120
BEAT = 60 / BPM

def font(size, bold=False):
    path = r'C:\Windows\Fonts\malgunbd.ttf' if bold else r'C:\Windows\Fonts\malgun.ttf'
    return ImageFont.truetype(path, size)

def ease(v):
    v = max(0, min(1, v)); return v*v*(3-2*v)

def make_music():
    n = SR * SECONDS
    t = np.arange(n, dtype=np.float64) / SR
    mix = np.zeros(n, dtype=np.float64)
    def add(start, dur, sig):
        a = max(0, int(start * SR)); b = min(n, a + len(sig))
        if a < b: mix[a:b] += sig[:b-a]
    def env(length, attack=.006, release=.08):
        q = np.arange(length) / SR
        return np.minimum(1, q/max(attack, .001)) * np.minimum(1, (length/SR-q)/max(release, .001))
    # Bright, original major-key progression: C / G / Am / F, one bar apiece.
    chords = [[261.63,329.63,392.00],[196.00,246.94,293.66],[220.00,261.63,329.63],[174.61,220.00,261.63]]
    for bar, chord in enumerate(chords * 4):
        start = bar * 2
        for f in chord:
            length = min(int(2.05*SR), n-int(start*SR))
            q = np.arange(length)/SR
            pad = (.035*np.sin(2*np.pi*f*q) + .013*np.sin(4*np.pi*f*q)) * env(length,.18,.24)
            add(start,2.05,pad)
    # Four-on-the-floor kick, crisp backbeat claps, and bright eighth-note hats.
    rng = np.random.default_rng(230)
    for beat in np.arange(0, SECONDS, BEAT):
        length = int(.22*SR); q=np.arange(length)/SR
        freq = 105 - 65*np.minimum(q/.18,1)
        kick = .48*np.sin(2*np.pi*freq*q)*np.exp(-q*19)
        add(float(beat),.22,kick)
        b=int(round(beat/BEAT))
        if b % 4 in (1,3):
            length=int(.14*SR); noise=rng.normal(0,1,length); q=np.arange(length)/SR
            clap=(noise*.16 + .08*np.sin(2*np.pi*188*q))*np.exp(-q*28)
            add(float(beat),.14,clap)
        # eighth-note shaker / closed hat, with alternating accents
        for sub in (0,.5):
            s=float(beat+sub*BEAT)
            if s>=SECONDS: continue
            length=int(.045*SR); q=np.arange(length)/SR
            noise=rng.normal(0,1,length)
            hat=noise*(.07 if sub==0 else .045)*np.exp(-q*78)
            add(s,.045,hat)
    # Bouncy bass pulses and short, syncopated mallet-like synth notes.
    roots=[130.81,98,110,87.31]
    scale=[261.63,293.66,329.63,392.0,440.0,523.25,392.0,329.63]
    for b in range(int(SECONDS/BEAT)):
        s=b*BEAT; root=roots[(b//4)%4]
        length=int(.31*SR); q=np.arange(length)/SR
        bass=(.17*np.sin(2*np.pi*root*q)+.04*np.sin(4*np.pi*root*q))*np.exp(-q*7)
        add(s,.31,bass)
        if b%2==0:
            f=scale[(b//2)%len(scale)]
            length=int(.19*SR); q=np.arange(length)/SR
            bell=(np.sin(2*np.pi*f*q)+.24*np.sin(4*np.pi*f*q)+.10*np.sin(6*np.pi*f*q))*np.exp(-q*12)
            add(s,.19,bell*.12)
    fade=np.minimum(1,t/.32)*np.minimum(1,(SECONDS-t)/.6)
    mix *= fade
    mix *= .88/max(1e-9,np.max(np.abs(mix)))
    stereo=np.column_stack([mix, np.roll(mix,220)*.97])
    pcm=(stereo*32767).astype('<i2').tobytes()
    path=os.path.join(ROOT,'chosun_promo_music.wav')
    with wave.open(path,'wb') as wf:
        wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR); wf.writeframes(pcm)
    return pcm

SCENES = [
    ('지금, 세상은', '어디로 움직일까?', '오늘의 흐름을 여는 첫 장면'),
    ('속보부터 깊이 있는 분석까지', '뉴스의 맥락을 한눈에', '빠른 소식, 넓은 시야'),
    ('정치 · 경제 · 사회 · 국제', '오늘을 움직이는 모든 이야기', '관심 있는 분야를 한곳에서'),
    ('스포츠와 문화, 라이프까지', '관심의 지도를 더 넓게', '매일의 발견을 더 다채롭게'),
    ('빠르게. 정확하게. 다채롭게.', '당신의 하루에 필요한 뉴스', '새로운 시선으로 읽는 오늘'),
    ('다음 장면이 궁금하다면', '조선닷컴에서 만나세요', 'CHOSUN.COM  ·  오늘의 뉴스, 지금 시작')
]

def centered(draw, text, y, f, color, anchor_x=W//2, stroke=0, stroke_fill=None):
    box=draw.textbbox((0,0),text,font=f,stroke_width=stroke)
    x=anchor_x-(box[2]-box[0])/2
    draw.text((x,y),text,font=f,fill=color,stroke_width=stroke,stroke_fill=stroke_fill)

def render_frames():
    base=Image.new('RGB',(W,H),(247,246,241))
    # Subtle cool-gray paper tint and quiet editorial grid.
    px=base.load()
    for y in range(H):
        shade=int(3*y/H)
        for x in range(W): px[x,y]=(247-shade,246-shade,241-shade)
    frames=[]
    # Stable, sparse graphic dots rather than borrowed page imagery.
    random.seed(23)
    particles=[(random.randint(40,W-40),random.randint(40,H-40),random.randint(2,5),random.random()*6.28) for _ in range(30)]
    for fi in range(FRAMES):
        sec=fi/FPS; scene=min(5,int(sec//5)); local=sec-scene*5
        im=base.copy(); d=ImageDraw.Draw(im,'RGBA')
        # Top editorial masthead, red live indicator and category marker.
        d.rectangle((0,0,W,7),fill=(199,24,47,255))
        d.text((62,34),'CHOSUN.COM',font=font(25,True),fill=(28,31,38,255))
        d.text((258,42),'뉴스  ·  오피니언  ·  인사이트',font=font(15),fill=(91,94,101,255))
        d.rounded_rectangle((1054,37,1218,78),radius=20,fill=(198,20,44,255))
        d.ellipse((1072,52,1082,62),fill=(255,255,255,255))
        d.text((1094,47),'LIVE  ·  TODAY',font=font(14,True),fill=(255,255,255,255))
        d.line((62,97,W-62,97),fill=(34,37,43,210),width=2)
        # Beat-synced editorial ticker.
        d.rectangle((62,112,159,144),fill=(201,24,47,255))
        d.text((77,117),'TODAY',font=font(15,True),fill=(255,255,255,255))
        d.text((177,116),'정치     경제     사회     국제     스포츠     문화',font=font(16),fill=(72,76,83,255))
        # Sparse colorful paper confetti travels in an accent ribbon.
        pulse=.5+.5*math.sin(2*math.pi*(sec/BEAT))
        ribbon_y=H-54
        d.rectangle((62,ribbon_y,W-62,ribbon_y+3),fill=(210,211,208,255))
        progress=(fi%int(FPS*5))/(FPS*5)
        x=62+int((W-124)*progress)
        d.rectangle((62,ribbon_y,W-62,ribbon_y+3),fill=(206,207,203,255))
        d.rectangle((62,ribbon_y,max(62,x),ribbon_y+3),fill=(199,24,47,230))
        d.ellipse((x-7,ribbon_y-5,x+7,ribbon_y+9),fill=(199,24,47,255))
        # Large step number and highlighted lead-in.
        d.text((64,180),f'{scene+1:02d}',font=font(18,True),fill=(199,24,47,255))
        d.line((108,194,176,194),fill=(199,24,47,200),width=3)
        lead,sub,kicker=SCENES[scene]
        beat_phase=(local%BEAT)/BEAT
        beat_pop=math.sin(math.pi*beat_phase)**2
        intro=ease(local/.34)
        yshift=int((1-intro)*27 - beat_pop*5)
        alpha=int(255*ease(local/.24)*ease((5-local)/.28))
        # Keep long Korean headings compact and centered across the landscape frame.
        main_size=51 if len(lead)>13 else 62
        main_font=font(main_size,True)
        lead_color=(30,33,40,alpha)
        if scene==5: lead_color=(32,35,42,alpha)
        centered(d,lead,249+yshift,main_font,lead_color)
        # Impact accent underneath the first statement.
        barw=int(90+42*beat_pop)
        d.rounded_rectangle((W//2-barw,337,W//2+barw,344),radius=3,fill=(199,24,47,alpha))
        # The secondary hook snaps in on the next musical phrase.
        second_alpha=int(alpha*ease((local-1.48)/.32))
        sub_size=43 if len(sub)<16 else 36
        sub_font=font(sub_size,True)
        sub_x=W//2+int((1-ease((local-1.48)/.32))*36)
        box=d.textbbox((0,0),sub,font=sub_font)
        d.rounded_rectangle((sub_x-(box[2]-box[0])/2-22,379,sub_x+(box[2]-box[0])/2+22,443),radius=10,fill=(255,255,255,second_alpha))
        centered(d,sub,386,sub_font,(199,24,47,second_alpha),anchor_x=sub_x)
        kicker_alpha=int(alpha*ease((local-2.1)/.35))
        centered(d,kicker,475,font(22),(91,95,103,kicker_alpha))
        # A few beat-responsive blocks add a graphic newsroom pulse.
        for k in range(5):
            xx=W//2-68+k*34
            hh=8+int((6 if (int(local/BEAT)%5)==k else 0)*beat_pop)
            d.rounded_rectangle((xx,532-hh,xx+18,532+hh),radius=3,fill=((199,24,47,180) if k==int(local/BEAT)%5 else (42,79,133,100)))
        # Floating accents confined to the margins.
        for j,(ax,ay,r,phase) in enumerate(particles):
            xx=ax+math.sin(sec*.5+phase)*9; yy=ay+math.cos(sec*.45+phase)*5
            if xx<W*.12 or xx>W*.88:
                d.ellipse((xx-r,yy-r,xx+r,yy+r),fill=(199,24,47,65 if j%2 else 35))
        # Brand sign-off.
        if scene==5:
            reveal=ease((local-2.35)/.42)
            centered(d,'CHOSUN.COM',565,font(27,True),(199,24,47,int(255*reveal)))
        d.text((62,659),'조선닷컴  |  세상을 읽는 빠른 시작',font=font(14),fill=(99,102,108,230))
        d.text((W-185,659),f'{int(sec//60):02d}:{int(sec%60):02d}',font=font(14,True),fill=(99,102,108,230))
        frames.append(im)
    return frames

def avi_chunk(tag,data):
    return tag+struct.pack('<I',len(data))+data+(b'\0' if len(data)&1 else b'')
def avi_list(kind,data): return b'LIST'+struct.pack('<I',len(data)+4)+kind+data
def make_avi(frames,pcm):
    avih=struct.pack('<14I',int(1e6/FPS),W*H*3*FPS,0,0x10,FRAMES,0,2,0,W,H,0,0,0,0)
    def strh(typ,handler,scale,rate,length,suggested,sample_size,rect):
        return struct.pack('<4s4sIHH8I4h',typ,handler,0,0,0,0,scale,rate,0,length,suggested,0xFFFFFFFF,sample_size,*rect)
    bitmap=struct.pack('<IiiHH4sIiiII',40,W,H,1,24,b'MJPG',W*H*3,0,0,0,0)
    wavefmt=struct.pack('<HHIIHH',1,2,SR,SR*4,4,16)
    vstr=avi_list(b'strl',avi_chunk(b'strh',strh(b'vids',b'MJPG',1,FPS,FRAMES,W*H*3,0,(0,0,W,H)))+avi_chunk(b'strf',bitmap))
    samples=len(pcm)//4
    astr=avi_list(b'strl',avi_chunk(b'strh',strh(b'auds',b'\0\0\0\0',4,SR*4,samples,SR*4,4,(0,0,0,0)))+avi_chunk(b'strf',wavefmt))
    hdrl=avi_list(b'hdrl',avi_chunk(b'avih',avih)+vstr+astr)
    chunks=[]; index=[]; offset=4; audio_bytes_sec=SR*4
    for fi,fr in enumerate(frames):
        b=io.BytesIO(); fr.save(b,format='JPEG',quality=86,optimize=True); dat=b.getvalue()
        c=avi_chunk(b'00dc',dat); chunks.append(c); index.append((b'00dc',0x10,offset,len(dat))); offset+=len(c)
        if (fi+1)%FPS==0:
            sec=(fi+1)//FPS
            ad=pcm[(sec-1)*audio_bytes_sec:sec*audio_bytes_sec]
            c=avi_chunk(b'01wb',ad); chunks.append(c); index.append((b'01wb',0,offset,len(ad))); offset+=len(c)
    movi=b''.join(chunks)
    idx=b''.join(tag+struct.pack('<3I',flags,pos,size) for tag,flags,pos,size in index)
    data=b'AVI '+hdrl+avi_list(b'movi',movi)+avi_chunk(b'idx1',idx)
    path=os.path.join(ROOT,'chosun_com_30s_kinetic_promo.avi')
    with open(path,'wb') as f: f.write(b'RIFF'+struct.pack('<I',len(data))+data)
    return path

if __name__=='__main__':
    print('Creating original beat-synced soundtrack...')
    pcm=make_music()
    print('Rendering 30 seconds of landscape typography...')
    frames=render_frames()
    path=make_avi(frames,pcm)
    print(f'Created {path} ({os.path.getsize(path):,} bytes)')

