from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askopenfile, asksaveasfile
import pygame
import os
import copy
import animation
from animation import Animation, AnimFrame
from subview import SpritesheetSubView, FrameSubView, AnimationSubView

FPS = 60

class View:
        def __init__(self, frame, width, height):
                embed = Frame(frame, width=width, height=height)
                embed.pack(side=RIGHT)
                os.environ['SDL_WINDOWID'] = str(embed.winfo_id())
                os.environ['SDL_VIDEODRIVER'] = 'windib'
                pygame.font.init()
                pygame.display.init()
                
                self.font = pygame.font.SysFont('arial', 16)
                self.width, self.height = (width, height)
                self.screen = pygame.display.set_mode((self.width,self.height))
                
                sheet_view = (0, 0, self.width, self.height/2)
                frame_view = (0, self.height/2, self.width/2, self.height/2)
                anim_view = (self.width/2, self.height/2,
                                     self.width/2, self.height/2)

                self.sheet_view = SpritesheetSubView(self, sheet_view)
                self.frame_view = FrameSubView(self, frame_view)
                self.anim_view = AnimationSubView(self, anim_view)
                self.subviews = [self.sheet_view, self.frame_view,
                                 self.anim_view]
                self.sheetpath = ""
                
                self.clock = pygame.time.Clock()
                
                pygame.display.update()

        def mainloop(self):
                for event in pygame.event.get():
                        for view in self.subviews:
                                view.handle_event(event)

                for view in self.subviews:
                        view.tick()

                self.screen.fill(pygame.Color(0, 0, 0))
                for view in self.subviews:
                        view.draw(self.screen)
                pygame.display.flip()
                self.clock.tick(FPS)

        def set_spritesheet(self, sheet):
                for view in self.subviews:
                        view.spritesheet = sheet

        def set_detail_frame(self, index):
                frame = self.anim_view.animation.frames[index]
                self.frame_view.set_frame(frame)
        
        def add_frame(self, duration):
                sheetclip = self.sheet_view.get_clip()
                if not sheetclip:
                        return None
                frame = AnimFrame(sheetclip)
                frame.duration = duration
                self.anim_view.add_frame(frame)
                self.frame_view.set_frame(frame)
                return len(self.anim_view.animation.frames)

        def add_hitbox(self):
                self.frame_view.add_hitbox()

        def add_damagebox(self):
                self.frame_view.add_damagebox()

        def save_animation(self, name):
                return animation.save_animation(
                        self.anim_view.animation,
                        self.sheetpath,
                        name)

        def load_animation(self, name):
                sheet, anim = animation.load_animation(name)
                self.anim_view.animation = anim
                return sheet
                

        def set_duration(self, val):
                if self.frame_view.frame and val > 0:
                        self.frame_view.frame.duration = val

        def get_frame_duration(self):
                return self.frame_view.frame.duration

        def reset(self):
                for view in self.subviews:
                        view.reset()
                
                
class App:
        def __init__(self, master):
                self.master = master
                frame = Frame(master)
                frame.pack()
                self.spritesheet = None

                self.view = View(frame, 800, 600)

                Label(frame, text="Frames").pack()               
                self.frameListbox = Listbox(frame)
                self.frameListbox.bind('<<ListboxSelect>>', self.onselect)
                self.frameListbox.pack()

                self.newButton = Button(
                        frame, text="New Animation", command=self.new_file
                        )
                self.newButton.pack()

                self.loadSheetBtn = Button(
                        frame, text="Load Sheet", command=self.load_sheet
                        )
                self.loadSheetBtn.pack()

                self.addHitboxBtn = Button(
                        frame, text="Add Hit Box", command=self.add_hitbox
                        )
                self.addHitboxBtn.pack()

                self.addDamageBoxBtn = Button(
                        frame, text="Add Damage Box", command=self.add_damagebox
                        )
                self.addDamageBoxBtn.pack()

                self.addFrameBtn = Button(
                        frame, text="Add Frame", command=self.add_frame
                        )
                self.addFrameBtn.pack()

                self.deleteFrameBtn = Button(
                        frame, text="Delete Frame", command=self.delete_frame
                        )
                self.deleteFrameBtn.pack()

                Label(frame, text="Frame Duration").pack()
                self.duration = StringVar()
                self.duration.trace("w", lambda name, index, mode, val=self.duration: self.change_duration(val))
                self.frameDurationEntry = Entry(frame, textvariable=self.duration)
                self.frameDurationEntry.insert(0, "1")
                self.frameDurationEntry.pack()
                
                self.playAnimation = Button(
                        frame, text="Play Animation", command=self.play_animation
                        )
                self.playAnimation.pack()

                self.saveButton = Button(
                        frame, text="Save", command=self.save_animation
                        )
                self.saveButton.pack()

                self.loadButton = Button(
                        frame, text="Load", command=self.load_animation
                        )
                self.loadButton.pack()

        def change_duration(self, val):
                if val.get().isdigit():
                        self.view.set_duration(int(val.get()))
                        
        def add_hitbox(self):
                self.view.add_hitbox()

        def add_damagebox(self):
                self.view.add_damagebox()
        
        def add_frame(self):
                index = self.view.add_frame(int(self.duration.get()))
                if index:
                        self.frameListbox.insert(END, 'Frame %d' % index)

        def delete_frame(self):
                if len(self.view.animation.frames) > 0:
                        index = int(self.frameListbox.curselection()[0])
                        frame = self.view.animation.frames.pop(index)
                        if self.view.current_frame == frame:
                                self.view.current_frame = None
                        self.frameListbox.delete(ANCHOR)

        def play_animation(self):
                pass

        def save_animation(self):
                ftypes = [("XML file", "*.xml"), ("All Files", "*.*")]
                f = asksaveasfile(mode='w', defaultextension=".xml",
                                  filetypes=ftypes)
                if f is None:
                        return
                xml = self.view.save_animation(f)
                f.write(xml)
                f.close()

        def load_animation(self):
                self.new_file()
                ftypes = [('XML', '*.xml')]
                file = askopenfile(initialdir=".", filetypes=ftypes)
                sheet = self.view.load_animation(file)
                spritesheet = pygame.image.load(sheet)
                self.view.set_spritesheet(spritesheet)
                self.view.sheetpath = sheet
                self.view.anim_view.animation.sheet = spritesheet
                for f in range(1,1+len(self.view.anim_view.animation.frames)):
                        self.frameListbox.insert(END, 'Frame %d' % f)

        def new_file(self):
                self.view.reset()
                self.frameListbox.delete(0, END)

        def load_sheet(self):
                ftypes = [('BMP', '*.bmp'), ('PNG', '*.png'), ('JPG', '*.jpg')]
                file= askopenfile(initialdir=".", filetypes = ftypes)
                spritesheet = pygame.image.load(file)
                self.view.set_spritesheet(spritesheet)
                self.view.sheetpath = file.name

        def onselect(self, evt):
                w = evt.widget
                if w.curselection():
                        index = int(w.curselection()[0])
                        self.view.set_detail_frame(index)
                        current_duration = self.view.get_frame_duration()
                        self.duration.set(str(current_duration))

        def mainloop(self):
                self.view.mainloop()
                

root = Tk()
root.title('Animation Tool')

app = App(root)

while True:
        app.mainloop()
        root.update()
