import pygame
import random
import math

# Constants
WIDTH, HEIGHT = 1000, 1000
MAX_SPEED = 0.00001
line_length = 1300
radius_length = 300 
SMOOTHNESS = 0.3 #

class Boid:
    def __init__(self,index):
        self.position = pygame.Vector2(random.randint(0, WIDTH), random.randint(0, HEIGHT))
        self.angle = random.uniform(0, 2 * math.pi)  # Random starting angle
        self.distance = random.uniform(0, line_length)  # Random distance along the line
        self.radius = random.randint(10, radius_length)  # Ensure radius isn't zero
        self.angle_speed = random.uniform(0.5, 300)  # Random speed for angle change
        self.target_position = self.position  # Initial target is the current position
        self.index = index 

    def update(self, diff_styles):
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        direction = mouse_pos - self.position
        if direction.length() > 0:
            direction = direction.normalize()

        if diff_styles == 0:
            if self.radius > 0:
                # Randomness in angle speed to simulate orbital variations
                self.angle_speed += random.uniform(-0.02, 0.02)  # Random small changes to the angle speed
                self.angle += self.angle_speed  # Update angle based on randomized speed
                
                self.radius += random.uniform(0, 200)
                self.radius = max(10, min(self.radius, radius_length))

                self.target_position = mouse_pos + pygame.Vector2(
                    self.radius * math.cos(self.angle),
                    self.radius * math.sin(self.angle),
                )

        elif diff_styles == 1:
            self.target_position = mouse_pos + direction * self.distance
            self.distance += random.uniform(-0.01, 0.01)
            self.distance = max(0, min(self.distance, line_length))

        elif diff_styles == 2:
            # Jupiter-like bands with randomness
            num_layers = 3 # Number of layers (concentric circles)
            num_circles_per_layer = 100  # Boids per layer
            spiral_scale = radius_length  # Base scale of the overall pattern
            layer_spacing = radius_length // 2  # Base distance between concentric layers
            mouse_pos = pygame.Vector2(pygame.mouse.get_pos())

            # Oscillate between structured orbits and randomness
            time_factor = (math.sin(pygame.time.get_ticks() * 0.001) + 1) / 2  # Oscillates between 0 and 1
            randomness_strength = 1 - time_factor  # Opposite of structure strength

            # Determine which layer and position within the layer
            total_circles = num_layers * num_circles_per_layer
            boid_index = self.index % total_circles
            layer_index = boid_index // num_circles_per_layer
            circle_index = boid_index % num_circles_per_layer

            # Add randomness to layer radii and spacing
            layer_radius = spiral_scale + layer_index * layer_spacing + random.uniform(-30, 30) * randomness_strength
            angle_offset = (2 * math.pi / num_circles_per_layer) * circle_index

            # Define the center of the layer around the mouse position
            layer_center = mouse_pos

            # Increment angle for orbital motion within the layer
            self.angle += self.angle_speed

            # Random offset for breaking away from structured orbits
            random_offset = pygame.Vector2(
                random.uniform(-layer_radius * randomness_strength, layer_radius * randomness_strength),
                random.uniform(-layer_radius * randomness_strength, layer_radius * randomness_strength),
            )

            # Calculate the boid's position in its layer's orbit
            structured_position = layer_center + pygame.Vector2(
                layer_radius * math.cos(self.angle + angle_offset),
                layer_radius * math.sin(self.angle + angle_offset),
            )
            self.target_position = structured_position + random_offset

        elif diff_styles == 3:
            # Transition between triangle and random motion
            base_size = radius_length // 2  # Base size of the triangle
            triangle_size = max(50, base_size)  # Ensure size is reasonable
            mouse_pos = pygame.Vector2(pygame.mouse.get_pos())

            # Define the vertices of the triangle
            vertex1 = mouse_pos + pygame.Vector2(0, -triangle_size)  # Top vertex
            vertex2 = mouse_pos + pygame.Vector2(
                -triangle_size * math.sin(math.pi / 3), triangle_size / 2
            )  # Bottom-left vertex
            vertex3 = mouse_pos + pygame.Vector2(
                triangle_size * math.sin(math.pi / 3), triangle_size / 2
            )  # Bottom-right vertex
            vertices = [vertex1, vertex2, vertex3]

            # Determine which edge the boid is currently traveling along
            segment = self.index % 3  # Cycle between 0, 1, and 2
            start_vertex = vertices[segment]
            end_vertex = vertices[(segment + 1) % 3]

            # Oscillate between triangle and random pattern
            time_factor = (math.sin(pygame.time.get_ticks() * 0.001) + 1) / 2  # Oscillates between 0 and 1
            randomness_strength = 1 - time_factor  # Opposite of triangle strength

            # Calculate random offset for breaking away from the triangle
            random_offset = pygame.Vector2(
                random.uniform(-triangle_size * randomness_strength, triangle_size * randomness_strength),
                random.uniform(-triangle_size * randomness_strength, triangle_size * randomness_strength),
            )

            # Interpolate between triangle and random position
            t = (self.angle_speed % 1)  # Smooth interpolation parameter (0 to 1)
            edge_position = start_vertex + t * (end_vertex - start_vertex)
            self.target_position = edge_position + random_offset * randomness_strength

            # Increment angle speed for smooth movement
            self.angle_speed += 0.005


        self.position = self.position + (self.target_position - self.position) * SMOOTHNESS

        # Keep boid inside screen bounds (wrapping around)
        self.position.x %= WIDTH
        self.position.y %= HEIGHT

    def draw(self, screen):
        size = 2
        direction = pygame.Vector2(math.cos(self.angle), math.sin(self.angle))

        point1 = self.position + direction * size
        point2 = self.position + direction.rotate(120) * (size / 2)
        point3 = self.position + direction.rotate(-120) * (size / 2)

        pygame.draw.polygon(screen, (255, 255, 255), [point1, point2, point3])



# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

boids = [Boid(index) for index in range(10000)]  # Create multiple boids

running = True
diff_styles = 0  # Initially, boids follow a line

while running:
    screen.fill((0, 0, 0))

    key_to_style = {
        pygame.K_1: 0,
        pygame.K_2: 1,
        pygame.K_3: 2,
        pygame.K_4: 3,
    }

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key in key_to_style:
                diff_styles = key_to_style[event.key]
            

    # Update and draw each boid
    for boid in boids:
        boid.update(diff_styles)
        boid.draw(screen)

    pygame.display.flip()  # Update the screen
    clock.tick(60)  # Limit the frame rate to 60 FPS

pygame.quit()