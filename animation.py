import copy
import xml.etree.ElementTree as et
from xml.dom import minidom
import pygame

FPS = 60

def save_animation(animation, sheetpath, outpath):
        if not animation:
                raise Exception('Invalid Animation')
        
        anim = et.Element('animation')
        anim.set('spritesheet', sheetpath)

        for frame in animation.frames:
                f = et.SubElement(anim, 'frame')
                f.set('x', str(frame.rect.x))
                f.set('y', str(frame.rect.y))
                f.set('w', str(frame.rect.w))
                f.set('h', str(frame.rect.h))
                f.set('duration', str(frame.duration))
                hitboxes = et.SubElement(f, 'hitboxes')
                damageboxes = et.SubElement(f, 'damageboxes')
                for hitbox in frame.hitboxes:
                        h = et.SubElement(hitboxes, 'hitbox')
                        h.set('x', str(hitbox.x))
                        h.set('y', str(hitbox.y))
                        h.set('w', str(hitbox.w))
                        h.set('h', str(hitbox.h))
                for dmgbox in frame.damageboxes:
                        d = et.SubElement(damageboxes, 'damagebox')
                        d.set('x', str(dmgbox.x))
                        d.set('y', str(dmgbox.y))
                        d.set('w', str(dmgbox.w))
                        d.set('h', str(dmgbox.h))

        ugly = et.tostring(anim, 'utf-8')
        parsed = minidom.parseString(ugly)
        pretty = parsed.toprettyxml(indent="    ")
        return pretty

def load_animation(filepath):
        root = et.parse(filepath).getroot()
        spritesheet = root.attrib['spritesheet']
        animation = Animation(None)
        for frame in root:
                attrs = frame.attrib
                rect = (int(frame.attrib[x]) for x in 'xywh')
                x,y,w,h = rect
                anim_frame = AnimFrame(pygame.Rect(x,y,w,h))
                for child in frame:
                        if len(child) > 0:
                                for box in child:
                                        rect = (int(frame.attrib[x]) for x in 'xywh')
                                        x,y,w,h = rect
                                        if box.tag == 'hitbox':
                                                anim_frame.add_hitbox(pygame.Rect(x,y,w,h))
                                        elif box.tag == 'damagebox':
                                                anim_frame.add_damagebox(pygame.Rect(x,y,w,h))
                animation.add_frame(anim_frame)
                       
        return (spritesheet, animation)

class Animation:
        def __init__(self, sheet):
                self.sheet = sheet
                self.frames = []
                self.playing = False
                self.current_frame = 0
                self.current_tick = 0

        def add_frame(self, frame):
                self.frames.append(copy.deepcopy(frame))

        def play(self, screen):
                self.playing = True

        def pause(self):
                self.playing = False

        def step(self):
                frame = self.frames[self.current_frame]
                if self.current_tick >= frame.duration:
                        self.current_frame += 1
                        self.current_tick = 0
                num_frames = len(self.frames)
                if self.current_frame >= num_frames:
                        self.current_frame = 0
                self.current_tick += 1


        def draw(self, screen, x, y):
                if len(self.frames) > 0:
                        frame = self.frames[self.current_frame]
                        screen.blit(self.sheet, (x, y), frame.rect)
                

class AnimFrame:
        def __init__(self, rect):
                self.rect = rect
                self.hitboxes = []
                self.damageboxes = []
                self.duration = 1

        def add_hitbox(self, rect):
                self.hitboxes.append(copy.deepcopy(rect))

        def add_damagebox(self, rect):
                self.damageboxes.append(copy.deepcopy(rect))

        def __str__(self):
                return "[%d, %d, %d, %d]" % (self.rect.x, self.rect.y,
                                             self.rect.w, self.rect.h)
        def __repr__(self):
                return "[%d, %d, %d, %d]" % (self.rect.x, self.rect.y,
                                             self.rect.w, self.rect.h)
