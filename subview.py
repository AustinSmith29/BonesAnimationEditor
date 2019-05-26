import pygame
import copy
from animation import Animation, AnimFrame

class SubView:
    def __init__(self, parent, rect_coords, title):
        self.view_rect = pygame.Rect(rect_coords)
        self.title_text = parent.font.render(title, True, (255, 255, 255))
        self.camera = copy.deepcopy(self.view_rect)
        self.scroll_anchor = (None, None)
        self.spritesheet = None

    def handle_event(self, event):
        # Set anchor point for scrolling
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 3:
                self.scroll_anchor = pygame.mouse.get_pos()

    def tick(self):
        # Scroll camera by delta mouse position
        valid_anchor = (None not in self.scroll_anchor)
        if pygame.mouse.get_pressed()[2] and valid_anchor:
            x, y = pygame.mouse.get_pos()
            anchx, anchy = self.scroll_anchor
            dx, dy = anchx - x, anchy - y
            self.scroll_anchor = (x, y)
            self.camera.move_ip(dx, dy)

    def draw(self, surface):
        pygame.draw.rect(surface, (255,255,255), self.view_rect, 1)
        surface.blit(self.title_text, (self.view_rect.x, self.view_rect.y,
                                       50, 32))

    def reset(self):
        pass

class SpritesheetSubView(SubView):
    def __init__(self, parent, rect_coords):
        super().__init__(parent, rect_coords, 'Spritesheet View')
        self.select_rect = pygame.Rect(0,0,0,0)
        self.has_clicked = False

    def handle_event(self, event):
        super().handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN:
            in_bounds = self.view_rect.collidepoint(pygame.mouse.get_pos())
            # Start selection box
            if event.button == 1 and in_bounds:
                self.has_clicked = True
                self.select_rect.x, self.select_rect.y = pygame.mouse.get_pos()
            else:
                self.select_rect = pygame.Rect(0,0,0,0)

        elif event.type == pygame.MOUSEBUTTONUP:
            # Complete selection box            
            if event.button == 1 and self.spritesheet != None and self.has_clicked:
                self.has_clicked = False
                # restrict rect to spritesheet's bounds
                mx, my = pygame.mouse.get_pos()
                select_start = (self.select_rect.x, self.select_rect.y)
                sheet_rect = self.spritesheet.get_rect()
                # clip won't work if top left of select_rect is out of bounds
                if not sheet_rect.collidepoint(select_start):
                    self.select_rect = pygame.Rect(0,0,0,0)
                else:
                    clip = self.select_rect.clip(sheet_rect)
                    if clip:
                        clip.normalize()
                        clip = self.cam_to_sheet(clip)
                        self.select_rect = self.shrink_frame(self.spritesheet, clip)

    def tick(self):
        super().tick()
        # Update select_rect size
        if pygame.mouse.get_pressed()[0] and self.has_clicked:
            mx, my = pygame.mouse.get_pos()
            self.select_rect.w = mx - self.select_rect.x
            self.select_rect.h = my - self.select_rect.y

    def draw(self, surface):
        if self.spritesheet:
            surface.blit(self.spritesheet, self.view_rect, self.camera)
        try:
            pygame.draw.rect(surface, (255,255,255), self.select_rect, 1)
        except TypeError:
            print ('Rect %s' % self.select_rect)
        super().draw(surface)

    def reset(self):
        super().reset()

    def get_clip(self):
        """Returns current selection on spritesheet"""
        return self.cam_to_sheet(self.select_rect)

    def cam_to_sheet(self, rect):
        """Gets rect of selection in terms of spritesheet's coords"""
        if rect.w == 0 or rect.h == 0:
            return None
        camx, camy = self.camera.x, self.camera.y
        clip = pygame.Rect(rect.x + camx,
                           rect.y + camy,
                           rect.w,
                           rect.h)
        return clip

    def sheet_to_cam(self, rect):
        """Returns rect in sheet coords to cam coords"""
        if rect.w == 0 or rect.h == 0:
            return None
        camx, camy = self.camera.x, self.camera.y
        clip = pygame.Rect(rect.x - camx,
                           rect.y - camy,
                           rect.w,
                           rect.h)
        return clip

    def shrink_frame(self, image, rect):
        """Given an initial rect around the sprite, returns the smallest rect that contains the sprite."""
        mask = image.get_at((rect.x, rect.y))
        new_x = -1
        new_y = -1
        new_w = -1
        new_h = -1

        # Scan from outside in from each edge to find the first
        # non-mask pixel. That is the closest point to contain
        # the sprite on that respective side. UGLY CODE BUT
        # IT WORKS.
        
        # top scan
        for y in range(rect.y, rect.y + rect.h + 1):
                for x in range(rect.x, rect.x + rect.w + 1):
                        try:
                                color = image.get_at((x,y))
                        except:
                                continue
                        if color != mask and new_y == -1:
                                new_y = y
        # left scan
        for x in range(rect.x, rect.x + rect.w + 1):
                for y in range(rect.y, rect.y + rect.h + 1):
                        try:
                                color = image.get_at((x,y))
                        except:
                                continue
                        if color != mask and new_x == -1:
                                new_x = x

        # bottom scan
        for y in range(rect.y + rect.h, rect.y-1, -1):
                for x in range(rect.x, rect.x + rect.w + 1):
                        try:
                                color = image.get_at((x,y))
                        except:
                                continue
                        if color != mask and new_h == -1:
                                new_h = y

        # right scan
        for x in range(rect.x + rect.w, rect.x-1, -1):
                for y in range(rect.y, rect.y + rect.h + 1):
                        try:
                                color = image.get_at((x,y))
                        except:
                                continue
                        if color != mask and new_w == -1:
                                new_w = x

        new_rect = pygame.Rect(new_x, new_y, new_w - new_x, new_h - new_y)
        new_rect = self.sheet_to_cam(new_rect)
        return new_rect     

class FrameSubView(SubView):
    def __init__(self, parent, rect_coords):
        super().__init__(parent, rect_coords, 'Frame View')
        self.frame = None
        self.frame_rect = pygame.Rect(self.view_rect.centerx,
                                      self.view_rect.centery,
                                      0,
                                      0)
        self.box = pygame.Rect(0,0,0,0)
        self.has_clicked = False

    def handle_event(self, event):
        super().handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN:
            in_bounds = self.view_rect.collidepoint(pygame.mouse.get_pos())
            if event.button == 1 and in_bounds:
                self.has_clicked = True
                self.box.x, self.box.y = pygame.mouse.get_pos()
                
        elif event.type == pygame.MOUSEBUTTONUP:
            self.has_clicked = False
            if event.button == 1 and self.frame != None:
                # restrict rect to spritesheet's bounds
                mx, my = pygame.mouse.get_pos()
                select_start = (self.box.x, self.box.y)
                # clip won't work if top left of select_rect is out of bounds
                if not self.frame_rect.collidepoint(select_start):
                    self.box = pygame.Rect(0,0,0,0)
                else:
                    self.box = self.box.clip(self.frame_rect)
                    

    def tick(self):
        super().tick()
        # Update box size
        if pygame.mouse.get_pressed()[0] and self.has_clicked:
            mx, my = pygame.mouse.get_pos()
            self.box.w = mx - self.box.x
            self.box.h = my - self.box.y

    def draw(self, surface):
        super().draw(surface)
        if self.frame and self.spritesheet:
            surface.blit(self.spritesheet, self.frame_rect, self.frame.rect)
            for hbox in self.frame.hitboxes:
                pygame.draw.rect(surface, (0,0,255), hbox, 1)
            for dbox in self.frame.damageboxes:
                pygame.draw.rect(surface, (255, 0, 0), dbox, 1)
        pygame.draw.rect(surface, (255,0,0), self.box, 1)

    def reset(self):
        super().reset()
        self.frame = None

    def set_frame(self, frame):
        #self.frame = self.spritesheet.subsurface(frame.rect)
        self.frame = frame
        self.frame_rect.w = self.frame.rect.w
        self.frame_rect.h = self.frame.rect.h

    def add_hitbox(self):
        if self.valid_box() and self.frame:
            self.frame.add_hitbox(self.box)

    def add_damagebox(self):
        if self.valid_box() and self.frame:
            self.frame.add_damagebox(self.box)

    def valid_box(self):
        return self.box.w != 0 and self.box.h != 0

class AnimationSubView(SubView):
    def __init__(self, parent, rect_coords):
        super().__init__(parent, rect_coords, 'Animation View')
        self.animation = None

    def handle_event(self, event):
        super().handle_event(event)

    def tick(self):
        super().tick()
        if self.animation:
            self.animation.step()

    def draw(self, surface):
        super().draw(surface)
        if self.animation:
            self.animation.draw(surface, self.view_rect.centerx,
                                self.view_rect.centery)

    def reset(self):
        super().reset()
        self.animation = None

    def add_frame(self, frame):
        if not self.animation:
            self.animation = Animation(self.spritesheet)
        self.animation.add_frame(frame)
