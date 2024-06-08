# 화소 및 데이터 변경
max_iter = 500
escape_radius = 1e+10

# (x, y, eps) = (-4.133439593177311, 0.00011276978589557028, 1.0351947055640964e-11)
# (x, y, eps) = (-4.0861172452798415, 7.287713992363359e-12, 1.1148431096635038e-09)
(x, y, eps) = (0, 0, 1)



import pygame
from PIL import Image
from numba import njit, boolean
import numpy as np
import time


# 그림 함수
@njit
def compute_tetration_divergence(x0, y0, x1, y1, width, height, max_iter = 500, escape_radius = 1e+10):
	x = np.linspace(x0, x1, width)
	y = np.linspace(y0, y1, height)
	c = x[:, None] + 1j * y[None, :]
	z = c
	divergence_map = np.zeros((width, height), dtype=boolean)
	for _ in range(max_iter):
		powered = c ** z
		z = powered
		divergence_map |= (np.abs(z) > escape_radius)

	return divergence_map

def getResetedDraw(n, mapY, offset, chunk):
	return ({
			"drawAll" : False,
			"map" : {
				(mapY -offset + 2*offset/chunk*y, y) : False
				for y in range(chunk)
			}
		},
			2*offset/chunk,
			np.zeros((n, n), dtype=bool)
		)

# 화면 리셋
pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = (800, 800)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

MAP_RENDER_SIZE = 256
chunk = 16

# 변수 리셋
# 시작 위치
mapX = x
mapY = y
# 시작 좌우 길이
mapShowOffset = eps

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
GRAY = (127, 127, 127)

DRAW_OFFSET = 20
DRAW_COUNT_BY_A_FRAME = 5
myFont = pygame.font.SysFont("malgungothic", 15)
lastTime = time.time()

isDrawn, oneChunckLen, mapImage = getResetedDraw(MAP_RENDER_SIZE, mapY, mapShowOffset, chunk)

# 그리기 변수
boxStartPos = (0, 0)
boxDragging = False
moveDragging = False

run = True
while run:
	# 맵 계산하기
	if not isDrawn['drawAll']:
		drawAll = True
		for key, value in isDrawn['map'].items():
			if not value:
				drawAll = False
				y,mapdrawy=key
				length = int(MAP_RENDER_SIZE/chunk)
				tmp = compute_tetration_divergence(mapX - mapShowOffset, y, mapX + mapShowOffset, y+oneChunckLen, MAP_RENDER_SIZE, length)
				mapImage[:,mapdrawy*length:(mapdrawy+1)*length] = tmp

				isDrawn['map'][key] = True
				break
			
		if drawAll:
			isDrawn['drawAll'] = True
			print(f"(x, y, eps) = ({mapX}, {mapY}, {mapShowOffset})")
		

	# 화면 그리기
	screen.fill((0, 0, 0))

	# 맵 그리기
	tmp = Image.fromarray(np.rot90(mapImage.astype('int') * 255, 3)).resize((SCREEN_WIDTH - 2*DRAW_OFFSET, SCREEN_HEIGHT - 2*DRAW_OFFSET), resample=Image.Resampling.NEAREST)
	frame = pygame.surfarray.make_surface(np.array(tmp))

	if moveDragging:
		screen.blit(frame, (DRAW_OFFSET + pygame.mouse.get_pos()[0] - boxStartPos[0], DRAW_OFFSET + pygame.mouse.get_pos()[1] - boxStartPos[1]))
	else:
		screen.blit(frame, (DRAW_OFFSET, DRAW_OFFSET))

	# 회색 테두리 그리기
	pygame.draw.rect(screen, GRAY, [0, 0, SCREEN_WIDTH, DRAW_OFFSET])
	pygame.draw.rect(screen, GRAY, [0, SCREEN_HEIGHT - DRAW_OFFSET, SCREEN_WIDTH, DRAW_OFFSET])
	pygame.draw.rect(screen, GRAY, [0, 0, DRAW_OFFSET, SCREEN_WIDTH])
	pygame.draw.rect(screen, GRAY, [SCREEN_WIDTH - DRAW_OFFSET, 0, DRAW_OFFSET, SCREEN_HEIGHT])

	# 프레임 그리기
	screen.blit(myFont.render(f"{int(1/(time.time() - lastTime))} fps", True, (0, 0, 255)), (0, 0))
	screen.blit(myFont.render(f"왼쪽 드래그 : 확대 / 휠 드래그 : 이동 / 우클릭 : 2배 축소 / ↑ : 화질 2배 / ↓ : 화질 0.5배", True, (0, 0, 255)), (100, 0))
	screen.blit(myFont.render(f"x {mapX} / y {mapY} / eps {mapShowOffset} / Image {MAP_RENDER_SIZE} X {MAP_RENDER_SIZE}", True, (0, 0, 255)), (0, SCREEN_HEIGHT - DRAW_OFFSET))
	lastTime = time.time()

	# 드래그 상자 그리기
	if boxDragging:
		mPos = pygame.mouse.get_pos()
		size = mPos[0] - boxStartPos[0]
		if size > 0:
			pygame.draw.rect(screen, YELLOW, [boxStartPos[0], boxStartPos[1], size, size], 2)
		else:
			pygame.draw.rect(screen, YELLOW, [boxStartPos[0]+size, boxStartPos[1]+size, -size, -size], 2)

	pygame.display.update()

	# 버튼 감지
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False
			pygame.quit()
			break

		elif event.type == pygame.KEYDOWN:
			if event.key == pygame.K_UP:
				MAP_RENDER_SIZE *= 2
				isDrawn, oneChunckLen, mapImage = getResetedDraw(MAP_RENDER_SIZE, mapY, mapShowOffset, chunk)
			elif event.key == pygame.K_DOWN:
				if MAP_RENDER_SIZE > 2:
					MAP_RENDER_SIZE = int(MAP_RENDER_SIZE/2)
					isDrawn, oneChunckLen, mapImage = getResetedDraw(MAP_RENDER_SIZE, mapY, mapShowOffset, chunk)

		elif event.type == pygame.MOUSEBUTTONDOWN:
			if event.button == 1: #좌클
				boxStartPos = pygame.mouse.get_pos()
				boxDragging = True
			elif event.button == 2:
				boxStartPos = pygame.mouse.get_pos()
				moveDragging = True
			elif event.button == 3:
				pass
		elif event.type == pygame.MOUSEBUTTONUP:
			if event.button == 1: #좌클
				if boxDragging:
					boxDragging = False
					mPos = pygame.mouse.get_pos()
					size = mPos[0] - boxStartPos[0]
					if size > 0:
						boxEndPos = (boxStartPos[0]+size, boxStartPos[1]+size)
					else:
						boxEndPos = (boxStartPos[0]+size, boxStartPos[1]+size)
						boxStartPos, boxEndPos = boxEndPos, boxStartPos
					x0,y0 = boxStartPos
					x1,y1 = boxEndPos

					x0-=DRAW_OFFSET
					y0=(SCREEN_HEIGHT - y0)
					x1-=DRAW_OFFSET
					y1=(SCREEN_HEIGHT - y1)
					
					x0 = mapY - mapShowOffset + 2*mapShowOffset*x0/(SCREEN_WIDTH-2*DRAW_OFFSET)
					x1 = mapY - mapShowOffset + 2*mapShowOffset*x1/(SCREEN_WIDTH-2*DRAW_OFFSET)
					y0 = mapX - mapShowOffset + 2*mapShowOffset*y0/(SCREEN_WIDTH-2*DRAW_OFFSET)
					y1 = mapX - mapShowOffset + 2*mapShowOffset*y1/(SCREEN_WIDTH-2*DRAW_OFFSET)

					mapShowOffset = x1 - x0

					mapY = (x0+x1)/2
					mapX = (y0+y1)/2

					isDrawn, oneChunckLen, mapImage = getResetedDraw(MAP_RENDER_SIZE, mapY, mapShowOffset, chunk)
			elif event.button == 2:
				if moveDragging:
					moveDragging = False
					mapY -= 2*mapShowOffset*(pygame.mouse.get_pos()[0] - boxStartPos[0]) / (SCREEN_WIDTH -2*DRAW_OFFSET)
					mapX += 2*mapShowOffset*(pygame.mouse.get_pos()[1] - boxStartPos[1]) / (SCREEN_WIDTH -2*DRAW_OFFSET)

					isDrawn, oneChunckLen, mapImage = getResetedDraw(MAP_RENDER_SIZE, mapY, mapShowOffset, chunk)

			elif event.button == 3:
				if not boxDragging and not moveDragging:
					mapShowOffset = mapShowOffset*2
					
					isDrawn, oneChunckLen, mapImage = getResetedDraw(MAP_RENDER_SIZE, mapY, mapShowOffset, chunk)

			if event.button != 1:
				boxDragging = False
			if event.button != 2:
				moveDragging = False