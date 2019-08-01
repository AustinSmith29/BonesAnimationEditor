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

        def mainloop(self, app):
                for event in pygame.event.get():
                        if event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_DOWN:
                                        app.down_key()
                                elif event.key == pygame.K_UP:
                                        app.up_key()
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

        def remove_frame(self, index):
                prev_frame = self.anim_view.remove_frame(index)
                if not prev_frame:
                        self.anim_view.reset()
                        self.frame_view.reset()
                else:
                        self.frame_view.set_frame(prev_frame)

        def add_hitbox(self):
                self.frame_view.add_hitbox()

        def add_damagebox(self):
                self.frame_view.add_damagebox()

        def play_animation(self, loop):
                self.anim_view.loop = loop
                self.anim_view.play_animation()

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
                self.master.title("Bones Animation Tool")
                frame = Frame(master)
                frame.pack()
                self.spritesheet = None
                self.frame_count = 0

                self.view = View(frame, 800, 600)

                Label(frame, text="Frames").pack()               
                self.frameListbox = Listbox(frame)
                self.frameListbox.bind('<<ListboxSelect>>', self.onselect)
                self.frameListbox.pack()

                self.menu = Menu(self.master)
                self.master.config(menu=self.menu)
                file = Menu(self.menu)
                file.add_command(label="New", command=self.new_file)
                file.add_command(label="Open...", command=self.load_animation)
                file.add_command(label="Save...", command=self.save_animation)
                self.menu.add_cascade(label="File", menu=file)

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

                self.playAnimationBtn = Button(
                        frame, text="Play Animation", command=self.play_animation
                        )
                self.playAnimationBtn.pack()

                self.loop = BooleanVar()
                self.loopCheckbtn = Checkbutton(
                        frame, text="loop", variable=self.loop
                        )
                self.loopCheckbtn.pack()

                Label(frame, text="Frame Duration").pack()
                self.duration = StringVar()
                self.duration.trace("w", lambda name, index, mode, val=self.duration: self.change_duration(val))
                self.frameDurationEntry = Entry(frame, textvariable=self.duration)
                self.frameDurationEntry.insert(0, "1")
                self.frameDurationEntry.pack()

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
                        self.frameListbox.insert(END, 'Frame %d' % self.frame_count)
                        self.frame_count += 1

        def delete_frame(self):
                if self.frameListbox.size() > 0 and self.frameListbox.curselection():
                        index = self.frameListbox.curselection()[0]
                        self.frameListbox.delete(index)
                        self.view.remove_frame(index)

        def play_animation(self):
                loop = (self.loop.get() == 1)
                self.view.play_animation(loop)

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
                        self.set_listbox_selection(index)

        def set_listbox_selection(self, index):
                if self.frameListbox.size() == 0:
                        return
                self.view.set_detail_frame(index)
                current_duration = self.view.get_frame_duration()
                self.duration.set(str(current_duration))
                self.frameListbox.select_anchor(index)

        def down_key(self):
                self.frameListbox.focus_set()
                if not self.frameListbox.curselection():
                        self.set_listbox_selection(0)
                else:
                        index = int(self.frameListbox.curselection()[0])
                        if index < self.frameListbox.size()-1:
                                self.set_listbox_selection(index+1)
                        else:
                                self.set_listbox_selection(0)

        def up_key(self):
                self.frameListbox.focus_set()
                if not self.frameListbox.curselection():
                        self.set_listbox_selection(0)
                else:
                        index = int(self.frameListbox.curselection()[0])
                        if index == 0:
                                size = self.frameListbox.size()
                                self.set_listbox_selection(size-1)
                        else:
                                self.set_listbox_selection(index-1)

        def mainloop(self):
                self.view.mainloop(self)
                

root = Tk()
root.title('Animation Tool')

app = App(root)

while True:
        app.mainloop()
        root.update()
