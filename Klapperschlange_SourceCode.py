import pygame, os
import numpy as np
import sounddevice as sd
import soundfile as sf
from scipy.signal import butter, lfilter

# ================= AUDIO CONFIG =================
SAMPLE_RATE = 44100
BLOCK_SIZE = 2048

# ================= GRID CONFIG =================
GRID = 16
CELL = 48
MARGIN = 4
SIDEBAR = 360

W = GRID * CELL + SIDEBAR
H = GRID * CELL

# ================= COLORS =================
BG = (240,240,240)            # Hellgrauer Hintergrund
GRID_FILL = (200,200,200)     # Etwas dunkler für Zellen
SIDEBAR_BG = (220,220,220)    # Sidebar leicht abgesetzt

NOTE_COLORS = [
    (98,214,163),(140,200,255),(255,170,120),(200,160,255),
    (255,110,150),(255,210,120),(120,230,255),(170,255,170),
    (255,140,255)
]

DRUM_COLORS = {
    "kick": (255,80,80),
    "snare": (80,160,255),
    "hihat": (255,220,80)
}

EFFECT_COLORS = {
    "pause": (120,120,120),
    "lowpass": (120,180,255),
    "reverb": (180,120,255),
    "distortion": (255,140,120)
}

SNAKE_COLORS = [
    (200,255,200),(200,200,255),(255,200,200),(255,255,200)
]

# ================= INIT =================
pygame.init()
screen = pygame.display.set_mode((W,H))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None,18)
BASE = os.path.dirname(os.path.abspath(__file__))

# ================= LOAD SAMPLES =================
def load_sample(path):
    if not os.path.exists(path):
        return np.zeros((BLOCK_SIZE,2),dtype=np.float32)
    data, sr = sf.read(path, dtype="float32")
    if data.ndim == 1:
        data = np.column_stack([data, data])
    return data

note_names = ["C","D","E","F","G","A","B","C2","D2"]
SAMPLES = [load_sample(os.path.join(BASE,f"Ton_{n}.wav")) for n in note_names]

DRUM_SAMPLES = {}
for name in ["Kick","Snare","HiHat"]:
    DRUM_SAMPLES[name.lower()] = load_sample(os.path.join(BASE,f"{name}.wav"))

# ================= DSP =================
def lowpass(signal,strength):
    cutoff = max(300,4000-strength*1000)
    b,a = butter(2, cutoff/(SAMPLE_RATE/2), btype='low')
    return lfilter(b,a,signal,axis=0)

def distortion(signal,strength):
    return np.tanh(signal*(1+strength))

def reverb(signal,strength):
    delay = int(0.03*SAMPLE_RATE)
    decay = 0.3+strength*0.1
    out = np.copy(signal)
    for i in range(delay,len(out)):
        out[i]+=out[i-delay]*decay
    return out

# ================= AUDIO ENGINE =================
audio_queue=[]
def audio_callback(outdata, frames, time, status):
    if audio_queue:
        outdata[:] = audio_queue.pop(0)
    else:
        outdata[:] = np.zeros((frames,2),dtype=np.float32)

stream = sd.OutputStream(
    samplerate=SAMPLE_RATE,
    channels=2,
    blocksize=BLOCK_SIZE,
    callback=audio_callback
)
stream.start()

# ================= HELPERS =================
def rect(r,c):
    return pygame.Rect(c*CELL+MARGIN,r*CELL+MARGIN,CELL-2*MARGIN,CELL-2*MARGIN)

def cell_from_mouse(pos):
    x,y = pos
    if x>=GRID*CELL: return None
    return y//CELL,x//CELL

# ================= SNAKE =================
class Snake:
    def __init__(self,pos,color):
        self.body=[{"pos":pos,"kind":None,"color":color}]
        self.color=color
        self.dir=(0,1)
        self.loop=[]
        self.play_idx=0
        self.effects={"lowpass":0,"reverb":0,"distortion":0}

    def step(self):
        r,c=self.body[0]["pos"]
        dr,dc=self.dir
        new=((r+dr)%GRID,(c+dc)%GRID)

        if new in turn_blocks:
            self.dir=turn_blocks[new]

        grew=None

        if new in notes:
            note=notes.pop(new)
            self.loop.append(note)
            if isinstance(note,int):
                grew={"kind":("note",note),"color":NOTE_COLORS[note]}
            else:
                grew={"kind":("drum",note),"color":DRUM_COLORS[note]}

        if new in effects:
            eff=effects.pop(new)
            if eff=="pause":
                self.loop.append(None)
                grew={"kind":("effect","pause"),"color":EFFECT_COLORS["pause"]}
            else:
                self.effects[eff]+=1
                grew={"kind":("effect",eff),"color":EFFECT_COLORS[eff]}

        old_positions=[seg["pos"] for seg in self.body]
        self.body[0]["pos"]=new
        for i in range(1,len(self.body)):
            self.body[i]["pos"]=old_positions[i-1]

        if grew:
            self.body.append({
                "pos":old_positions[-1],
                "kind":grew["kind"],
                "color":grew["color"]
            })

    def draw(self):
        for i,seg in enumerate(self.body):
            r,c=seg["pos"]
            rc=rect(r,c)
            col=seg["color"] if i==0 else tuple(int(x*0.6) for x in seg["color"])
            kind=seg["kind"]

            if kind is None:
                pygame.draw.rect(screen,col,rc,border_radius=12)
            else:
                t,_=kind
                if t=="note":
                    pygame.draw.rect(screen,col,rc,border_radius=8)
                elif t=="drum":
                    pygame.draw.circle(screen,col,rc.center,rc.width//2-4)
                elif t=="effect":
                    cx,cy=rc.center
                    points=[(cx,rc.top),(rc.right,cy),(cx,rc.bottom),(rc.left,cy)]
                    pygame.draw.polygon(screen,col,points)

# ================= WORLD =================
notes={}
effects={}
turn_blocks={}
snakes=[]

mode="note"
selected_note=0
current_effect="lowpass"
pending_dir=(0,1)

BPM=120
STEP=60/BPM
timer=0
playing=True

# ================= PLAY STEP =================
def play_step(snakes):
    combined=np.zeros((BLOCK_SIZE,2),dtype=np.float32)

    for s in snakes:
        if not s.loop: continue

        note=s.loop[s.play_idx%len(s.loop)]
        s.play_idx+=1

        if note is None: continue

        audio=None
        if isinstance(note,int):
            audio=np.copy(SAMPLES[note])
            if s.effects["lowpass"]>0:
                audio=lowpass(audio,s.effects["lowpass"])
            if s.effects["distortion"]>0:
                audio=distortion(audio,s.effects["distortion"])
            if s.effects["reverb"]>0:
                audio=reverb(audio,s.effects["reverb"])
        elif isinstance(note,str):
            audio=np.copy(DRUM_SAMPLES[note])

        if audio is None: continue

        block=audio[:BLOCK_SIZE]
        if block.shape[0]<BLOCK_SIZE:
            pad=np.zeros((BLOCK_SIZE-block.shape[0],2),dtype=np.float32)
            block=np.vstack([block,pad])

        combined+=block

    combined=np.clip(combined,-1,1)
    audio_queue.append(combined)

# ================= MAIN LOOP =================

run=True
while run:
    dt=clock.tick(60)/1000
    if playing: timer+=dt

    for e in pygame.event.get():
        if e.type==pygame.QUIT: run=False

        elif e.type==pygame.KEYDOWN:
            if e.key==pygame.K_SPACE: playing=not playing
            elif e.key==pygame.K_n: mode="note"
            elif e.key==pygame.K_t: mode="turn"
            elif e.key==pygame.K_s: mode="snake"
            elif e.key==pygame.K_e: mode="effect"

            elif e.key==pygame.K_p: current_effect="pause"
            elif e.key==pygame.K_l: current_effect="lowpass"
            elif e.key==pygame.K_r: current_effect="reverb"
            elif e.key==pygame.K_d: current_effect="distortion"

            elif pygame.K_1<=e.key<=pygame.K_9:
                selected_note=e.key-pygame.K_1
            elif e.key==pygame.K_z: selected_note="kick"
            elif e.key==pygame.K_x: selected_note="snare"
            elif e.key==pygame.K_c: selected_note="hihat"

            elif e.key==pygame.K_UP: pending_dir=(-1,0)
            elif e.key==pygame.K_DOWN: pending_dir=(1,0)
            elif e.key==pygame.K_LEFT: pending_dir=(0,-1)
            elif e.key==pygame.K_RIGHT: pending_dir=(0,1)

            elif e.key==pygame.K_EQUALS or e.key==pygame.K_PLUS:
                BPM=min(300,BPM+5); STEP=60/BPM
            elif e.key==pygame.K_MINUS:
                BPM=max(20,BPM-5); STEP=60/BPM

            elif e.key==pygame.K_BACKSPACE:
                cell=cell_from_mouse(pygame.mouse.get_pos())
                if cell:
                    notes.pop(cell,None)
                    effects.pop(cell,None)
                    turn_blocks.pop(cell,None)

        elif e.type==pygame.MOUSEBUTTONDOWN:
            cell=cell_from_mouse(e.pos)
            if not cell: continue
            r,c=cell
            if mode=="note": notes[(r,c)]=selected_note
            elif mode=="turn": turn_blocks[(r,c)]=pending_dir
            elif mode=="effect": effects[(r,c)]=current_effect
            elif mode=="snake":
                snakes.append(Snake((r,c),SNAKE_COLORS[len(snakes)%len(SNAKE_COLORS)]))

    if playing and timer>=STEP:
        timer=0
        for s in snakes:
            s.step()
        play_step(snakes)

    screen.fill(BG)

    for r in range(GRID):
        for c in range(GRID):
            pygame.draw.rect(screen,GRID_FILL,rect(r,c),border_radius=6)

    for (r,c),n in notes.items():
        if isinstance(n,int):
            pygame.draw.rect(screen,NOTE_COLORS[n],rect(r,c),border_radius=8)
        else:
            pygame.draw.circle(screen,DRUM_COLORS[n],rect(r,c).center,rect(r,c).width//2-4)

    for (r,c),eff in effects.items():
        if eff=="pause":
            pygame.draw.ellipse(screen,EFFECT_COLORS[eff],rect(r,c))
        else:
            rc=rect(r,c)
            cx,cy=rc.center
            points=[(cx,rc.top),(rc.right,cy),(cx,rc.bottom),(rc.left,cy)]
            pygame.draw.polygon(screen,EFFECT_COLORS[eff],points)

    for (r,c) in turn_blocks:
        pygame.draw.rect(screen,(255,255,255),rect(r,c),2,border_radius=6)

    for s in snakes: s.draw()

    # Hintergrund der Sidebar leicht abgesetzt
    pygame.draw.rect(screen,SIDEBAR_BG,(GRID*CELL,0,SIDEBAR,H))
    
    help_text = [
        "MODES: N/Note  T/Turn  S/Snake  E/Effect",
        "NOTES: 1–9",
        "DRUMS: Z=Kick  X=Snare  C=HiHat",
        "EFFECTS: P=Pause  L=Lowpass  R=Reverb  D=Distortion",
        "TURN: Arrow Keys",
        "SPACE: Play/Pause",
        "+/-: BPM",
        "Backspace: Delete"
    ]
    sidebar_font = pygame.font.SysFont("Arial", 16, bold=True)
    for i,t in enumerate(help_text):
        text_surface = sidebar_font.render(t, True, (30,30,30))  # dunkle Schrift auf hellem BG
        screen.blit(text_surface, (GRID*CELL+20, 20 + i*30))   # größere Zeilenabstände

    # BPM
    bpm_surface = sidebar_font.render(f"BPM: {BPM}", True, (30,30,30))
    screen.blit(bpm_surface, (GRID*CELL+20, 30+30*len(help_text)))

    import os
    logo_path = os.path.join(BASE, "klapperschlange_logo3.png")
    logo_img = pygame.image.load(logo_path).convert_alpha()
    # Größe optional anpassen
    logo_img = pygame.transform.smoothscale(logo_img, (340, 240))  # Breite 120px, Höhe 60px

    # Position in der Sidebar unten rechts
    screen.blit(logo_img, (W - logo_img.get_width() - 10, H - logo_img.get_height() - 10))
    pygame.display.flip()


pygame.quit()
stream.stop()