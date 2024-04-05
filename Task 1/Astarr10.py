import pygame
import sys
import random
import heapq

# Constants
WINDOW_SIZE = (800, 600)
GRID_SIZE = (40, 30)
CELL_SIZE = (WINDOW_SIZE[0] // GRID_SIZE[0], WINDOW_SIZE[1] // GRID_SIZE[1])
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)
FPS = 10

# Pygame initialization
pygame.init()
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Multi-Agent CBS Algorithm")
clock = pygame.time.Clock()

# Manually set obstacles
obstacles = [
    (5, 5), (5, 6), (5, 7), (5, 8), (5, 9),
    (15, 20), (15, 21), (15, 22), (15, 23), (15, 24),
    (30, 10), (30, 11), (30, 12), (30, 13), (30, 14)
]

# Map generation
map_grid = [[0 for _ in range(GRID_SIZE[0])] for _ in range(GRID_SIZE[1])]
for obstacle in obstacles:
    x, y = obstacle
    map_grid[y][x] = 1

# Agent class
class Agent:
    def __init__(self, start_pos, end_pos, color):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.color = color
        self.path = []
        self.move_index = 0

    def find_path(self, map_grid, constraints):
        open_list = []
        closed_list = set()
        heapq.heappush(open_list, (0, self.start_pos, []))

        while open_list:
            current_cost, current_pos, path = heapq.heappop(open_list)

            if current_pos == self.end_pos:
                self.path = path + [current_pos]
                break

            if current_pos in closed_list:
                continue

            closed_list.add(current_pos)

            for neighbor in self.get_neighbors(current_pos):
                if map_grid[neighbor[1]][neighbor[0]] == 0 and neighbor not in closed_list and neighbor not in constraints:
                    new_path = path + [current_pos]
                    new_cost = len(new_path) + self.heuristic(neighbor, self.end_pos)
                    heapq.heappush(open_list, (new_cost, neighbor, new_path))

    def get_neighbors(self, pos):
        x, y = pos
        neighbors = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
        return [(nx, ny) for nx, ny in neighbors if 0 <= nx < GRID_SIZE[0] and 0 <= ny < GRID_SIZE[1]]

    def heuristic(self, pos, end_pos):
        return abs(pos[0] - end_pos[0]) + abs(pos[1] - end_pos[1])

    def move(self):
        if self.move_index < len(self.path) - 1:
            self.move_index += 1

    def draw(self):
        pygame.draw.rect(screen, self.color, (self.path[self.move_index][0] * CELL_SIZE[0], self.path[self.move_index][1] * CELL_SIZE[1], CELL_SIZE[0], CELL_SIZE[1]))

# CBS algorithm
def cbs(agents):
    paths = {}  # Dictionary to store paths of agents
    constraints = set()  # Set to store constraints

    for agent in agents:
        agent.find_path(map_grid, constraints)
        paths[agent] = agent.path

    # Resolve conflicts
    for i in range(len(agents)):
        for j in range(i+1, len(agents)):
            for k in range(1, min(len(paths[agents[i]]), len(paths[agents[j]]))):
                if paths[agents[i]][k] == paths[agents[j]][k] and paths[agents[i]][k-1] != paths[agents[j]][k-1]:
                    # Conflict detected, resolve by selecting agent with higher cost
                    if len(paths[agents[i]]) < len(paths[agents[j]]):
                        agent1, agent2 = agents[j], agents[i]
                    else:
                        agent1, agent2 = agents[i], agents[j]
                    
                    # Add constraints for the conflicting cell
                    constraints.add(paths[agent1][k])
                    constraints.add(paths[agent2][k])
                    
                    # Re-plan path for the higher-cost agent
                    agent2.find_path(map_grid, constraints)
                    paths[agent2] = agent2.path

    for agent in agents:
        constraints.add(agent.end_pos)  # Add end positions to constraints

# Create agents
agents = [
    Agent((0, 0), (0, 20), RED),
    Agent((0, 20), (0, 0), GREEN),
    Agent((5, 3), (27, 23), BLUE),
    Agent((27, 23), (5, 3), PURPLE),
    Agent((15, 15), (3, 2), ORANGE)
]

# Main loop
running = True
while running:
    screen.fill(WHITE)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Map drawing
    for y, row in enumerate(map_grid):
        for x, cell in enumerate(row):
            color = BLACK if cell == 1 else WHITE
            pygame.draw.rect(screen, color, (x * CELL_SIZE[0], y * CELL_SIZE[1], CELL_SIZE[0], CELL_SIZE[1]))

    # CBS algorithm
    cbs(agents)

    # Move agents
    for agent in agents:
        agent.move()

    # Draw agents
    for agent in agents:
        agent.draw()

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
