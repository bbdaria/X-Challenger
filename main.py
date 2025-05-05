from ursina import *
import math
from ursina.prefabs.first_person_controller import FirstPersonController
import random
from math import sin
from pathlib import Path
import threading
import sys
import pygame
from PIL import Image
import os

app = Ursina()

# Arena
arena = Entity(model='plane', scale=(50,1,50), color=color.gray, collider='box', texture='white_cube')

# === 3D Model Paths ===
# Place your models in the project root.
GOLLIRA_MODEL = 'gollira.glb'  # Use the provided GLB model
PERSON_MODEL = 'person.obj'  # Use the provided OBJ model

# Gollira (3D model)
gollira = Entity(model=GOLLIRA_MODEL, color=color.black, scale=3, position=(0,1.5,0), collider='box')

# People (3D models)
people = []
num_people = 50  # Reduced for better performance
radius = 30  # Increased radius for further spawn
person_colors = [color.white, color.black, color.brown, color.rgb(200,180,140), color.rgb(120,60,30)]
for i in range(num_people):
    angle = i * (2 * math.pi / num_people)
    x = math.cos(angle) * radius
    z = math.sin(angle) * radius
    p_color = random.choice(person_colors)
    person = Entity(model=PERSON_MODEL, color=p_color, scale=1, position=(x,0.5,z), collider='box')
    people.append(person)

# Health and attack parameters
gollira.health = 1000
gollira.attack_power = 50
gollira.attack_range = 5

defeat_people = set()

for person in people:
    person.health = 20
    person.attack_power = 2
    person.attack_range = 2.5
    person.alive = True

# Camera orbit parameters
camera_orbit_angle = 0
camera_base_radius = 40
camera_height = 22
camera_zoom = 1.0
camera_shake = 0.0
camera_shake_intensity = 0.0
camera_focus_timer = 0
camera_focus_target = None
camera_min_radius = 25

# Animation state for gollira
gollira.is_attacking = False
gollira.attack_anim_timer = 0
gollira.is_roaring = False
gollira.roar_anim_timer = 0

# Animation state for people
for person in people:
    person.run_anim_phase = random.uniform(0, 2*math.pi)
    person.is_attacking = False
    person.attack_anim_timer = 0
    person.is_healing = False
    person.heal_anim_timer = 0

# Blood effect function
def blood_splatter(position):
    p = Entity(model='sphere', color=color.red, scale=0.5, position=position + Vec3(0,0.5,0))
    p.animate_scale(2, duration=0.3)
    p.fade_out(duration=0.5)

# === Abilities ===
# Gollira abilities
G_SLAM_COOLDOWN = 8
G_ROAR_COOLDOWN = 12
gollira.slam_timer = 0
gollira.roar_timer = 0

def gollira_ground_slam():
    # Damages and knocks back people in range
    focus_camera_on(gollira, duration=0.7, shake=0.5)
    gollira.is_attacking = True
    gollira.attack_anim_timer = 0.5
    for person in people:
        if person.alive and (person.position - gollira.position).length() < 6:
            person.health -= 40
            # Knockback effect
            person.position += (person.position - gollira.position).normalized() * 4
            # TODO: Add particle effect

def gollira_roar():
    # Stuns people in range
    focus_camera_on(gollira, duration=0.7, shake=0.3)
    gollira.is_roaring = True
    gollira.roar_anim_timer = 0.7
    for person in people:
        if person.alive and (person.position - gollira.position).length() < 10:
            person.stunned = 1.5  # seconds
            # TODO: Add visual effect

# People abilities
for person in people:
    person.stunned = 0
    person.dodge_chance = 0.1  # 10% chance to dodge
    person.healer = (i % 20 == 0)  # 1 in 20 is a healer
    person.heal_cooldown = 0

# Camera action focus helper
def focus_camera_on(target, duration=1.0, shake=0.2):
    global camera_focus_timer, camera_focus_target, camera_shake_intensity
    camera_focus_timer = duration
    camera_focus_target = target
    camera_shake_intensity = shake

victory_state = None  # None, 'gollira', or 'people'
victory_timer = 0
victory_targets = None
victory_text = None
victory_gif_shown = False

def show_cat_gif_pygame():
    """Show cat.gif in a Pygame window, looping, closes on key or click. Window is larger and offset left."""
    gif_path = 'cat.gif'
    try:
        img = Image.open(gif_path)
    except Exception as e:
        print(f"[ERROR] Could not load cat.gif: {e}")
        return
    # Extract frames
    frames = []
    durations = []
    scale_factor = 1.3
    try:
        while True:
            frame = img.copy().convert('RGBA')
            # Scale up
            new_size = (int(frame.width * scale_factor), int(frame.height * scale_factor))
            frame = frame.resize(new_size, Image.LANCZOS)
            frames.append(frame)
            durations.append(img.info.get('duration', 50))
            img.seek(len(frames))
    except EOFError:
        pass
    if not frames:
        print("[ERROR] No frames in cat.gif!")
        return
    w, h = frames[0].size
    # Set window position a little to the left
    screen_w = 1920  # fallback
    screen_h = 1080  # fallback
    try:
        import tkinter as tk
        root = tk.Tk()
        screen_w = root.winfo_screenwidth()
        screen_h = root.winfo_screenheight()
        root.destroy()
    except:
        pass
    x = max(0, (screen_w - w)//2 - 200)
    y = max(0, (screen_h - h)//2)
    os.environ['SDL_VIDEO_WINDOW_POS'] = f"{x},{y}"
    import pygame
    pygame.init()
    win = pygame.display.set_mode((w, h))
    pygame.display.set_caption('Victory Cat!')
    # Convert PIL frames to Pygame surfaces (after display is initialized)
    pygame_frames = [pygame.image.fromstring(f.tobytes(), f.size, f.mode).convert_alpha() for f in frames]
    clock = pygame.time.Clock()
    running = True
    frame_idx = 0
    elapsed = 0
    while running:
        for event in pygame.event.get():
            if event.type in (pygame.QUIT, pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                running = False
        win.fill((0,0,0))
        win.blit(pygame_frames[frame_idx], (0,0))
        pygame.display.flip()
        dt = clock.tick(60)
        elapsed += dt
        if elapsed >= durations[frame_idx]:
            elapsed = 0
            frame_idx = (frame_idx + 1) % len(pygame_frames)
    pygame.quit()

def update():
    global camera_orbit_angle, camera_zoom, camera_shake, camera_focus_timer, camera_focus_target, camera_shake_intensity
    global victory_state, victory_timer, victory_targets, victory_text, victory_gif_shown
    # Victory camera logic
    if victory_state:
        if victory_text is None:
            if victory_state == 'gollira':
                victory_text = Text('GOLLIRA WINS!', origin=(0,0), scale=16, color=color.red, position=(0,0.25), background=False)
            else:
                victory_text = Text('HUMANS WIN!', origin=(0,0), scale=16, color=color.red, position=(0,0.25), background=False)
            victory_text.bold = True
            victory_text.fit_to_text = True
            victory_text.text_size = 2
            victory_text.z = -10  # Ensure it's in front
        # Show GIF window only once, after timer ends
        if not victory_gif_shown:
            victory_gif_shown = True
            threading.Thread(target=show_cat_gif_pygame, daemon=True).start()
        victory_timer -= time.dt
        # Orbit around victors
        if isinstance(victory_targets, list):
            center = sum((p.position for p in victory_targets), Vec3(0,0,0)) / max(1,len(victory_targets))
        else:
            center = victory_targets.position
        angle = (5.0 - victory_timer) * 2 * math.pi / 5.0
        cam_x = center.x + math.cos(angle) * camera_base_radius
        cam_z = center.z + math.sin(angle) * camera_base_radius
        cam_y = center.y + camera_height
        camera.position = Vec3(cam_x, cam_y, cam_z)
        camera.look_at(center + Vec3(0,2,0))
        if victory_timer <= 0:
            if victory_text:
                destroy(victory_text)
                victory_text = None
            application.quit()
        return  # Skip the rest of update during victory
    # Idle animation: slow up-and-down movement
    gollira.y = 1.5 + sin(time.time() * 2) * 0.2
    # === Gollira procedural animations ===
    if gollira.is_attacking:
        gollira.scale = (3, 2.5 + sin(time.time()*20)*0.1, 3)
        gollira.attack_anim_timer -= time.dt
        if gollira.attack_anim_timer <= 0:
            gollira.is_attacking = False
            gollira.scale = 3
    elif gollira.is_roaring:
        gollira.rotation_x = sin(time.time()*20)*10
        gollira.roar_anim_timer -= time.dt
        if gollira.roar_anim_timer <= 0:
            gollira.is_roaring = False
            gollira.rotation_x = 0
    else:
        gollira.scale = (3, 3 + sin(time.time()*2)*0.2, 3)
        gollira.rotation_x = 0
    # === People procedural animations ===
    for person in people:
        if not person.alive:
            continue
        # Running bob
        if person.stunned > 0:
            person.y = 0.5
        else:
            person.run_anim_phase += time.dt * 8
            person.y = 0.5 + sin(person.run_anim_phase) * 0.15
        # Attack lunge
        if person.is_attacking:
            person.attack_anim_timer -= time.dt
            person.z += 0.2 * sin(person.attack_anim_timer*20)
            if person.attack_anim_timer <= 0:
                person.is_attacking = False
        # Heal pulse
        if person.is_healing:
            person.heal_anim_timer -= time.dt
            person.scale = 1.2 if int(person.heal_anim_timer*10)%2==0 else 1
            if person.heal_anim_timer <= 0:
                person.is_healing = False
                person.scale = 1
    # === Cinematic camera logic ===
    # Dynamic zoom based on people left, but clamp to min radius
    alive_count = sum(1 for p in people if p.alive)
    camera_zoom = lerp(camera_zoom, 1.0 + (alive_count/100)*1.2, 1.5 * time.dt)
    camera_orbit_radius = max(camera_base_radius * camera_zoom, camera_min_radius)
    # Camera focus on action
    if camera_focus_timer > 0 and camera_focus_target:
        camera_focus_timer -= time.dt
        shake = (random.uniform(-1,1), random.uniform(-1,1), random.uniform(-1,1)) if camera_shake_intensity > 0 else (0,0,0)
        cam_target = camera_focus_target.position + Vec3(0, camera_height, camera_orbit_radius/2)
        camera.position = lerp(camera.position, cam_target + Vec3(*shake)*camera_shake_intensity, 8 * time.dt)
        camera.look_at(camera_focus_target.position + Vec3(0,2,0))
        if camera_focus_timer <= 0:
            camera_focus_target = None
            camera_shake_intensity = 0
    else:
        camera_orbit_angle += time.dt * 0.3  # slow orbit
        cam_x = gollira.x + math.cos(camera_orbit_angle) * camera_orbit_radius
        cam_z = gollira.z + math.sin(camera_orbit_angle) * camera_orbit_radius
        cam_y = gollira.y + camera_height
        camera.position = lerp(camera.position, Vec3(cam_x, cam_y, cam_z), 2 * time.dt)
        camera.look_at(gollira.position + Vec3(0,2,0))
    # People AI: move toward gollira and attack if close
    for person in people:
        if not person.alive:
            continue
        direction = gollira.position - person.position
        distance = direction.length()
        if distance > person.attack_range:
            person.position += direction.normalized() * time.dt * 3  # move speed
        else:
            # Attack gollira
            gollira.health -= person.attack_power * time.dt
            person.is_attacking = True
            person.attack_anim_timer = 0.2
            if gollira.health <= 0:
                gollira.color = color.red
                print('Gollira defeated!')
                victory_state = 'people'
                victory_timer = 5.0
                victory_targets = [p for p in people if p.alive]
                return
    # Gollira AI: attack people in range
    for i, person in enumerate(people):
        if not person.alive:
            continue
        distance = (person.position - gollira.position).length()
        if distance < gollira.attack_range:
            person.health -= gollira.attack_power * time.dt
            if person.health <= 0 and person.alive:
                person.alive = False
                # Ripped apart effect: scale down and blood
                blood_splatter(person.position)
                person.animate_scale(0.1, duration=0.2)
                invoke(person.disable, delay=0.25)
                defeat_people.add(i)
    # End condition: all people defeated
    if not victory_state and len(defeat_people) == len(people):
        gollira.color = color.green
        print('Gollira wins!')
        victory_state = 'gollira'
        victory_timer = 5.0
        victory_targets = gollira
    if not victory_state and gollira.health <= 0:
        gollira.color = color.red
        print('Gollira defeated!')
        victory_state = 'people'
        victory_timer = 5.0
        victory_targets = [p for p in people if p.alive]
    # Gollira ability timers
    gollira.slam_timer -= time.dt
    gollira.roar_timer -= time.dt
    # Use abilities automatically for demo
    if gollira.slam_timer <= 0:
        gollira_ground_slam()
        gollira.slam_timer = G_SLAM_COOLDOWN
    if gollira.roar_timer <= 0:
        gollira_roar()
        gollira.roar_timer = G_ROAR_COOLDOWN
    # People group rush (every 5s, 10 random people rush)
    if int(time.time()) % 5 == 0:
        for person in random.sample([p for p in people if p.alive], min(10, len([p for p in people if p.alive]))):
            direction = gollira.position - person.position
            person.position += direction.normalized() * time.dt * 8  # fast rush
    # People heal ability
    for person in people:
        if not person.alive:
            continue
        if person.healer and person.heal_cooldown <= 0:
            for ally in people:
                if ally.alive and ally != person and (ally.position - person.position).length() < 3 and ally.health < 20:
                    ally.health += 5
                    person.is_healing = True
                    person.heal_anim_timer = 0.5
                    # TODO: Add heal effect
            person.heal_cooldown = 10
        person.heal_cooldown -= time.dt
    # People dodge
    for person in people:
        if not person.alive:
            continue
        if random.random() < person.dodge_chance:
            person.position += Vec3(random.uniform(-2,2),0,random.uniform(-2,2))
    # People stun timer
    for person in people:
        if person.stunned > 0:
            person.stunned -= time.dt
            continue  # skip actions while stunned

app.run() 