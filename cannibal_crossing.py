import pygame
import itertools


class gv:
    starting_sitrep = [0, ['b', 'C', 'C', 'V', 'V'], []]
    finish_text = ''
    boat_slots = 2
class PygameEnvironment():
    def __init__(self, sx, sy, caption, mode=0) -> None:
        self.caption = caption
        self.sx = sx
        self.sy = sy
        
        self.running = True
        self.can_click = True

        pygame.init()
        pygame.font.init()
        pygame.display.set_caption(self.caption)
        self.s = pygame.display.set_mode((self.sx, self.sy))
        self.bg = pygame.Surface((self.sx, self.sy))
        self.bg.fill('White')
   
        while self.running == True:
            self.mainloop()

    def exit(self):
        self.running = False

    def mainloop(self):
        self.catch_events()
        if self.running == True:
            self.get_input()
            self.graphics()
            self.restrict_clicks()
            pygame.display.update()

    def catch_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.exit() ; pygame.quit() ; return
            
    def get_input(self):
        self.keys = pygame.key.get_pressed()
        self.mouse_pos = pygame.mouse.get_pos()

    def restrict_clicks(self):
        if pygame.mouse.get_pressed()[0]: self.can_click = False
        else: self.can_click = True

    def graphics(self):
        self.s.blit(self.bg, [0,0])
        for node in Node.node_list:
            if node.coords[0] + 150 > 0 and node.coords[0] < self.sx:
                if node.coords[1] + 75 > 0 and node.coords[1] < self.sy:
                    node.draw(self.s)

            if pygame.key.get_pressed()[pygame.K_LEFT]:
                node.coords[0] += 50
            if pygame.key.get_pressed()[pygame.K_RIGHT]:
                node.coords[0] -= 50
            if pygame.key.get_pressed()[pygame.K_DOWN]:
                node.coords[1] -= 50
            if pygame.key.get_pressed()[pygame.K_UP]:
                node.coords[1] += 50
        if pygame.key.get_pressed()[pygame.K_ESCAPE]:
            Node.explored_nodes.clear()
            Node.node_list.clear()
            node1 = Node([0, ['b', 'C', 'C', 'C', 'V', 'V', 'V'], []], [50,50])
            Node.explored_nodes.append([node1.text, 0])
            
class Node():
    node_list = []
    dead_nodes = []
    coords_list = []
    n_string_list = []
    explored_nodes = []
    y_offset = 0
    def __init__(self, sitrep, coords, boat_capacity=3, color='BLACK', parent=None) -> None:
        self.boat_capacity = boat_capacity
        self.color = color
        self.coords = coords
        self.parent = parent

        self.origin_distance = sitrep[0]
        self.sitrep = sitrep
        self.text = ' '.join(sorted(self.sitrep[1])) + ' / ' + ' '.join(sorted(self.sitrep[2]))
        if self.text == gv.finish_text: self.color = 'GREEN'
        elif self.is_dead_node() == True: 
            self.color = 'RED'
            Node.dead_nodes.append(self.text)
        
        Node.coords_list.append(self.coords)
        Node.node_list.append(self)
        if self.text != gv.finish_text:
            Node.n_string_list.append(self.text)

    def is_dead_node(self):
        for side in self.sitrep:
            if type(side) == int: pass
            else:
                c = 0
                v = 0
                for character in side:
                    if character == 'C': c += 1
                    if character == 'V': v += 1
                if c > v and v != 0: 
                    return True
        return False

    def draw(self, screen):
        self.rendered_text = pygame.font.SysFont('sans', 20)
        self.rendered_text = self.rendered_text.render(self.text, True, self.color)
        pygame.draw.rect(screen, self.color, [self.coords[0], self.coords[1], 150, 75], 1, 200)
        screen.blit(self.rendered_text, [self.coords[0] + 75 -  self.rendered_text.get_width()/2, self.coords[1] + 37.5 - self.rendered_text.get_height()/2])
        self.rect = pygame.rect.Rect(self.coords[0], self.coords[1], 150, 75)

        if self.parent != None:
            pygame.draw.line(screen, 'BLACK', [self.coords[0], self.coords[1]+37.5], [self.parent.coords[0]+150, self.parent.coords[1]+37.5])

    def find_valid_branches(self):
        new_sitrep = [0, [self.sitrep[1][:], self.sitrep[2][:]]] 
        if self.origin_distance % 2 == 0:
            new_sitrep[1][0].remove('b')
            new_sitrep[1][1].append('b')
            combinations = []
            for i in range(self.boat_capacity): combinations.extend(list(itertools.combinations(new_sitrep[1][0], i+1)))
            combinations = list(dict.fromkeys(combinations))
        else: 
            new_sitrep[1][1].remove('b')
            new_sitrep[1][0].append('b')
            combinations = []
            for i in range(self.boat_capacity): combinations.extend(list(itertools.combinations(new_sitrep[1][1], i+1)))
            combinations = list(dict.fromkeys(combinations))
        return combinations
    
    def generate_branch_nodes(self):
        i = 0
        for branch in self.find_valid_branches():
            new_sitrep = [0, [self.sitrep[1][:], self.sitrep[2][:]]]
            if self.origin_distance % 2 == 0:
                new_sitrep[1][0].remove('b')
                new_sitrep[1][1].append('b')
            else:
                new_sitrep[1][1].remove('b')
                new_sitrep[1][0].append('b')
            for character in branch:
                if self.origin_distance % 2 == 0:
                    new_sitrep[1][0].remove(character)
                    new_sitrep[1][1].append(character)
                else:
                    new_sitrep[1][1].remove(character)
                    new_sitrep[1][0].append(character)
            if 'b' in new_sitrep[1][0]: Node.explored_nodes.append([self.text, 0]) 
            elif 'b' in new_sitrep[1][1]: Node.explored_nodes.append([self.text, 1])
            self.place_node(new_sitrep)
            
    def place_node(self, sitrep):
        node_text = ' '.join(sorted(sitrep[1][0])) + ' / ' + ' '.join(sorted(sitrep[1][1]))
        if self.origin_distance+1 % 2 == 0:
            if [node_text, 0] not in Node.explored_nodes and node_text not in Node.n_string_list:
                if [self.coords[0] + 250, self.coords[1] + Node.y_offset] not in Node.coords_list: 
                    Node([self.origin_distance+1, sitrep[1][0], sitrep[1][1]], [self.coords[0] + 250, self.coords[1] + Node.y_offset], boat_capacity=gv.boat_slots, parent=self)
                    Node.y_offset = 0
                else: 
                    Node.y_offset += 90
                    self.place_node(sitrep)
        else:
            if [node_text, 1] not in Node.explored_nodes and node_text not in Node.n_string_list:
                if [self.coords[0] + 250, self.coords[1] + Node.y_offset] not in Node.coords_list: 
                    Node([self.origin_distance+1, sitrep[1][0], sitrep[1][1]], [self.coords[0] + 250, self.coords[1] + Node.y_offset], boat_capacity=gv.boat_slots, parent=self)
                    Node.y_offset = 0
                else: 
                    Node.y_offset += 90
                    self.place_node(sitrep)

def run_siimulation():
    c = input('Cannibals: ')
    v = input('Vegetarians: ')
    gv.boat_slots = int(input('Boat_slots: '))
    depth = 1000

    gv.starting_sitrep = [0, ['b'], []]
    for i in range(int(c)):
        gv.starting_sitrep[1].append('C')
    for i in range(int(v)):
        gv.starting_sitrep[1].append('V')

    gv.finish_text = ' /'
    for character in gv.starting_sitrep[1]:
        if character == 'C':
            gv.finish_text += ' C'
    for character in gv.starting_sitrep[1]:
        if character == 'V':
            gv.finish_text += ' V'
    gv.finish_text += ' b'
    print(gv.finish_text)

    test_node = Node(gv.starting_sitrep, [50,50], gv.boat_slots)
    test_node.generate_branch_nodes()

    i = 0
    for node in Node.node_list:
        i += 1
        if node.text not in Node.dead_nodes and node.text != gv.finish_text:
            if node.origin_distance % 2 == 0:
                if [node.text, 0] not in Node.explored_nodes:
                    node.generate_branch_nodes()
            else: 
                if [node.text, 1] not in Node.explored_nodes:
                    node.generate_branch_nodes()
        if i > depth: break

    PygameEnvironment(1200,800,'River Problem')
run_siimulation()
