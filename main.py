import pygame
import random
import enum
from os import path
import webbrowser

# assets helper function
def asset(filename):
	return path.join(path.dirname(__file__), "assets", filename)

# constants
MAX_ABS_VEL = 500
PADDLE_WIDTH = 150
PADDLE_HEIGHT = 10
PADDLE_EDGE_DISTANCE = 50

FONT_FAMILY = asset("IBMPlexMono-Regular.ttf")
TITLE_FONT_SIZE = 70
SUBTITLE_FONT_SIZE = 40
SCORE_FONT_SIZE = 30
SMALL_FONT_SIZE = 16
SCORE_PADDING = 10

EASY_MODE = 1
EASY_MODE = 1.05
HARD_MODE = 1.1

GAME_MODE_NAMES = ["EASY", "MEDIUM", "HARD"]
GAME_MODE = [EASY_MODE, HARD_MODE, HARD_MODE]

# initialization
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((720, 800))
pygame.display.set_caption("PyPong")

# fonts initialization
title_font = pygame.font.Font(FONT_FAMILY, TITLE_FONT_SIZE)
subtitle_font = pygame.font.Font(FONT_FAMILY, SUBTITLE_FONT_SIZE)
small_font = pygame.font.Font(FONT_FAMILY, SMALL_FONT_SIZE)
score_font = pygame.font.Font(FONT_FAMILY, SCORE_FONT_SIZE)

# images initialization
pause_img = pygame.image.load(asset("pause.png"))
pause_img = pygame.transform.scale(pause_img, (150, 150))
github_img = pygame.image.load(asset("github.png"))
volume_on_img = pygame.image.load(asset("volume_on.png"))
volume_off_img = pygame.image.load(asset("volume_off.png"))

# sound initialization
pygame.mixer.music.load(asset("sound.mp3"))

# game variables initialization
running = True
paused = False
clock = pygame.time.Clock()
dt = 0

ball_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)
ball_vel = pygame.Vector2(0, 0)
ball_size = 10

mouse_paddle_pos = screen.get_width() / 2 - PADDLE_WIDTH / 2
mouse_paddle_old_pos = mouse_paddle_pos
mouse_paddle_vel = 0

bot_paddle_pos = screen.get_width() / 2 - PADDLE_WIDTH / 2
bot_paddle_vel = 0

score = [0, 0]
selected_game_mode = 0

display_game_menu = True

countdown = 0
current_time = pygame.time.get_ticks()
next_time = current_time

mouse_hover_pos = pygame.Vector2(0, 0)
mouse_click_pos = pygame.Vector2(0, 0)
last_mouse_move = pygame.time.get_ticks()
is_mouse_moving = False

sounds_enabled = True
hovering_game_mode = []
for i in range(len(GAME_MODE)):
	hovering_game_mode.append(False)

# helper classes
class Color():
	white = (255, 255, 255)
	black = (0, 0, 0)
class Player(enum.Enum):
	HUMAN = 1
	BOT = 2

# helper functions
def limit_vel(vel, max_abs_vel):
	return min(max(vel, -max_abs_vel), max_abs_vel)

def two_ranges_random(range1: tuple[int, int], range2: tuple[int, int]):
	range = range1 if random.random() < 0.5 else range2
	return random.randrange(*range)

def play_sound():
	global sounds_enabled
	if not sounds_enabled:
		return
	pygame.mixer.music.play()

def reset_game(winning_player = Player.BOT, reset_score = False, use_countdown = True):
	global ball_pos, ball_vel, bot_paddle_pos, bot_paddle_vel, score, countdown

	y_vel = 300 if winning_player == Player.BOT else -300

	ball_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)
	ball_vel = pygame.Vector2(two_ranges_random((-300, -50), (50, 300)), y_vel)
	bot_paddle_pos = screen.get_width() / 2 - PADDLE_WIDTH / 2
	bot_paddle_vel = 0

	if reset_score:
		score = [0, 0]
	if use_countdown:
		countdown = 4

def start_game():
	global display_game_menu
	display_game_menu = False
	reset_game(reset_score=True)

# rendering functions
def render():
	global ball_pos, bot_paddle_pos, mouse_paddle_pos, score

	screen.fill(Color.black)

	ball = pygame.draw.circle(screen, Color.white, (int(ball_pos.x), int(ball_pos.y)), ball_size)

	player_paddle = pygame.draw.rect(
		screen,
		Color.white,
		(mouse_paddle_pos, screen.get_height() - PADDLE_EDGE_DISTANCE, PADDLE_WIDTH, PADDLE_HEIGHT)
	)
	bot_paddle = pygame.draw.rect(
		screen,
		Color.white,
		(bot_paddle_pos, PADDLE_EDGE_DISTANCE, PADDLE_WIDTH, PADDLE_HEIGHT)
	)

	# Score text rendering
	bot_score_text = score_font.render(f"{score[0]}", True, Color.white)
	human_score_text = score_font.render(f"{score[1]}", True, Color.white)
	screen.blit(
		bot_score_text,
		(10, screen.get_width() / 2 - bot_score_text.get_width() / 2 - SCORE_PADDING)
	)
	screen.blit(
		human_score_text,
		(10, screen.get_width() / 2 + human_score_text.get_width() / 2 + SCORE_PADDING)
	)

def render_game_menu():
	global display_game_menu, selected_game_mode, sounds_enabled

	screen.fill(Color.black)
	title_text = title_font.render("PyPong", True, Color.white)
	menu_text = subtitle_font.render("Select a game mode", True, Color.white)
	screen.blit(
		title_text,
		(screen.get_width() / 2 - title_text.get_width() / 2, title_text.get_height() / 2 + 30)
	)
	screen.blit(
		menu_text,
		(screen.get_width() / 2 - menu_text.get_width() / 2, menu_text.get_height() / 2 + title_text.get_height() + 50)
	)

	is_hovering_any_mode = True if True in hovering_game_mode else False
	for i, mode in enumerate(GAME_MODE_NAMES):
		subtitle_font.set_underline((i == selected_game_mode and not is_hovering_any_mode and not is_mouse_moving) or hovering_game_mode[i])
		mode_text = subtitle_font.render(mode, True, Color.white)
		rect = screen.blit(
			mode_text,
			(screen.get_width() / 2 - mode_text.get_width() / 2, mode_text.get_height() / 2 + menu_text.get_height() + 200 + 75 * i)
		)
		hovering_game_mode[i] = rect.collidepoint(mouse_hover_pos)
		if rect.collidepoint(mouse_click_pos):
			selected_game_mode = i
			start_game()

	subtitle_font.set_underline(False)

	copyright_text = small_font.render("Copyright © 2024 Giorgio Bellisario", True, Color.white)
	screen.blit(
		copyright_text,
		(screen.get_width() / 2 - copyright_text.get_width() / 2, screen.get_height() - copyright_text.get_height() - 15)
	)
	sound_toggle = screen.blit(
		volume_on_img if sounds_enabled else volume_off_img,
		(screen.get_width() - volume_on_img.get_width() - 10, 10)
	)
	if sound_toggle.collidepoint(mouse_click_pos):
		sounds_enabled = not sounds_enabled
		play_sound()

	github_link = screen.blit(
		github_img,
		(screen.get_width() - github_img.get_width() - 10, screen.get_height() - github_img.get_height() - 10)
	)
	if github_link.collidepoint(mouse_click_pos):
		webbrowser.open("https://github.com/Bellisario/pypong", new=2)

def render_pause():
	global paused, sounds_enabled
	screen.blit(
		pause_img,
		(screen.get_width() / 2 - pause_img.get_width() / 2, screen.get_height() / 2 - pause_img.get_height() / 2)
	)
	mode_text = small_font.render(f"Mode: {GAME_MODE_NAMES[selected_game_mode]}", True, Color.white)
	info_text = small_font.render("Press Space to resume, Escape to reset game.", True, Color.white)
	screen.blit(mode_text, (10, 10))
	screen.blit(
		info_text,
		(10, screen.get_height() - info_text.get_height() - 10)
	)
	sound_toggle = screen.blit(
		volume_on_img if sounds_enabled else volume_off_img,
		(screen.get_width() - volume_on_img.get_width() - 10, 10)
	)
	if sound_toggle.collidepoint(mouse_click_pos):
		sounds_enabled = not sounds_enabled
		play_sound()

def render_countdown():
	global countdown
	countdown_text = title_font.render(f"{countdown}", True, Color.white)
	screen.blit(
		countdown_text,
		(screen.get_width() / 2 - countdown_text.get_width() / 2, screen.get_height() / 2 - countdown_text.get_height() / 2 - 60)
	)

# main game loop
while running:
	# reset mouse_click_pos every frame
	mouse_click_pos = pygame.Vector2(0, 0)

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
		elif event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE and paused:
				paused = False
				display_game_menu = True
				reset_game(reset_score=True)
			elif event.key == pygame.K_SPACE:
				if not display_game_menu:
					paused = not paused
					# stop time ticking
					clock.tick()
				else:
					display_game_menu = False
					reset_game(reset_score=True)
			elif event.key == pygame.K_RETURN and display_game_menu:
				start_game()
			elif event.key == pygame.K_DOWN and display_game_menu:
				selected_game_mode = (selected_game_mode + 1) % len(GAME_MODE)
			elif event.key == pygame.K_UP and display_game_menu:
				selected_game_mode = (selected_game_mode - 1) % len(GAME_MODE)
		elif event.type == pygame.MOUSEMOTION and not paused:
			mouse_hover_pos = pygame.Vector2(pygame.mouse.get_pos())
			last_mouse_move = pygame.time.get_ticks()
			is_mouse_moving = True
			mouse_paddle_pos = max(min(mouse_hover_pos.x - PADDLE_WIDTH/2, screen.get_width() - PADDLE_WIDTH), 0)
		elif event.type == pygame.MOUSEBUTTONDOWN:
			if event.button == 1:
				mouse_click_pos = pygame.Vector2(pygame.mouse.get_pos())
				countdown = 0

	if pygame.time.get_ticks() - last_mouse_move > 500:
		is_mouse_moving = False

	if paused:
		render()
		render_pause()
		pygame.display.flip()
		continue
	elif display_game_menu:
		render_game_menu()
		pygame.display.flip()

		dt = clock.tick(60) / 1000
		continue
	elif countdown > 0:
		render()

		current_time = pygame.time.get_ticks()

		if current_time >= next_time:
			countdown -= 1
			next_time = current_time + 1000

		if countdown > 0:
			render_countdown()
			mode_text = small_font.render(f"Mode: {GAME_MODE_NAMES[selected_game_mode]}", True, Color.white)
			info_text = small_font.render("Press Space to pause at any time. Click to skip countdown.", True, Color.white)
			screen.blit(mode_text, (10, 10))
			screen.blit(
				info_text,
				(10, screen.get_height() - info_text.get_height() - 10)
			)
		
		pygame.display.flip()
		dt = clock.tick(60) / 1000
		continue

	# Ball movement
	if (ball_pos.x - ball_size) <= 0:
		ball_vel.x = limit_vel(abs(ball_vel.x) * 1.1, MAX_ABS_VEL)
		play_sound()
	elif (ball_pos.x + ball_size) >= screen.get_width():
		ball_vel.x = limit_vel(abs(ball_vel.x) * -1.1, MAX_ABS_VEL)
		play_sound()

	if (ball_pos.y - ball_size) <= 0 or (ball_pos.y + ball_size) >= screen.get_height():
		# leaving the implementation here for future use... maybe "bounce" (when ball is lost) mode?
		# ball_vel.y = limit_vel(ball_vel.y * -1.1, MAX_ABS_VEL)

		# Score update
		if (ball_pos.y + ball_size) >= screen.get_height():
			score[0] += 1
			reset_game(Player.BOT)
		else:
			score[1] += 1
			reset_game(Player.HUMAN, use_countdown=False)

	ball_pos.x += ball_vel.x * dt
	ball_pos.y += ball_vel.y * dt

	# Bot paddle movement
	bot_paddle_vel = (ball_pos.x - (bot_paddle_pos + PADDLE_WIDTH/2)) * GAME_MODE[selected_game_mode] + bot_paddle_vel * 0.8

	bot_paddle_pos += bot_paddle_vel * dt
	if bot_paddle_pos < 0:
		bot_paddle_pos = 0
		bot_paddle_vel = 0
	elif bot_paddle_pos + PADDLE_WIDTH > screen.get_width():
		bot_paddle_pos = screen.get_width() - PADDLE_WIDTH
		bot_paddle_vel = 0

	# Mouse paddle movement
	# calculate mouse_paddle_vel from old mouse_paddle_pos
	mouse_paddle_vel = (mouse_paddle_pos - mouse_paddle_old_pos) * 700 * dt
	mouse_paddle_old_pos = mouse_paddle_pos

	# Ball collision with paddle
	#   IMPLEMENTATION NOTES:
	#	   Ball collides with paddle if:
	#		   - ball has overtaken paddle
	#		   - ball is on paddle boundaries when overtaking
	#		   - ball has overtaken paddle NOT more than 1/2 of paddle height

	mouse_paddle_boundary = screen.get_height() - PADDLE_EDGE_DISTANCE
	mouse_paddle_ending_pos = mouse_paddle_pos + PADDLE_WIDTH
	bot_paddle_boundary = PADDLE_EDGE_DISTANCE + PADDLE_HEIGHT
	bot_paddle_ending_pos = bot_paddle_pos + PADDLE_WIDTH

	if (
		(ball_pos.y + ball_size/2 >= mouse_paddle_boundary >= ball_pos.y - ball_size/2)
		and (ball_pos.x + ball_size) >= mouse_paddle_pos
		and (ball_pos.x - ball_size) <= mouse_paddle_ending_pos
	):
		ball_vel.y = limit_vel(abs(ball_vel.y) * -1.1, MAX_ABS_VEL)
		center_collision_distance = (ball_pos.x - (mouse_paddle_pos + PADDLE_WIDTH/2)) * 1.5
		paddle_velocity_multiplier = mouse_paddle_vel * 50
		ball_vel.x = limit_vel(ball_vel.x + center_collision_distance + paddle_velocity_multiplier, MAX_ABS_VEL)
		play_sound()
	if (
		(ball_pos.y + ball_size/2 >= bot_paddle_boundary >= ball_pos.y - ball_size/2)
		and (ball_pos.x + ball_size) >= bot_paddle_pos
		and (ball_pos.x - ball_size) <= bot_paddle_ending_pos
	):
		ball_vel.y = limit_vel(abs(ball_vel.y) * 1.1, MAX_ABS_VEL)
		center_collision_distance = (ball_pos.x - (bot_paddle_pos + PADDLE_WIDTH/2)) * 1.5
		ball_vel.x = limit_vel(ball_vel.x + center_collision_distance, MAX_ABS_VEL)
		play_sound()

	render()

	pygame.display.flip()
	dt = clock.tick(60) / 1000

pygame.quit()
