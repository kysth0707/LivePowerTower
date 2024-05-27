# 화소 및 데이터 변경
max_iter = 500
escape_radius = 1e+10

# 시작 위치
mapX = 0
mapY = 0
# 시작 좌우 길이
mapShowOffset = 5e-1



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
	c = x[:, np.newaxis] + 1j * y[np.newaxis, :]

	divergence_map = np.zeros((width, height), dtype=boolean)

	for i in range(width):
		for j in range(height):
			c_val = c[i, j]
			z = c_val

			for k in range(max_iter):
				z = c_val ** z
				if np.abs(z) > escape_radius:
					divergence_map[i, j] = True
					break

	return divergence_map

def getResetedDraw(n, mapY, offset, chunk):
	cnt = int(n / chunk)
	return ({
			"drawAll" : False,
			"map" : {
				(mapY -offset + 2*offset/cnt*y, y) : False
				for y in range(cnt)
			}
		},
			2*offset/(n/chunk)
		)

# 화면 리셋
pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = (800, 800)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

n = 256
chunk = 16

# 변수 리셋
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)

DRAW_OFFSET = 20
DRAW_COUNT_BY_A_FRAME = 5



isDrawn, oneChunckLen = getResetedDraw(n, mapY, mapShowOffset, chunk)
mapImage = np.zeros((n, n), dtype=bool)
# print(mapImage)

# 그리기 변수
boxStartPos = (0, 0)
boxDragging = False
moveDragging = False

run = True
while run:
	# 맵 계산하기
	if not isDrawn['drawAll']:
		drawAll = True
		# drawCnt = 0
		for key, value in isDrawn['map'].items():
			if not value:
				# drawCnt += 1
				drawAll = False
				y,mapdrawy=key
				# tmp = compute_tetration_divergence(mapX - mapShowOffset, mapY - mapShowOffset, key[0]+oneChunckLen, key[1]+oneChunckLen, chunk, chunk)
				tmp = compute_tetration_divergence(mapX - mapShowOffset, y, mapX + mapShowOffset, y+oneChunckLen, n, int(n/chunk))
				length = int(n/chunk)
				mapImage[:,mapdrawy*length:(mapdrawy+1)*length] = tmp

				isDrawn['map'][key] = True
				break
			
		if drawAll:
			isDrawn['drawAll'] = True
			print(f"(x, y, eps) = ({mapX}, {mapY}, {mapShowOffset})")
		

	# 화면 그리기
	screen.fill((127, 127, 127))
	pygame.draw.rect(screen, BLACK, [DRAW_OFFSET, DRAW_OFFSET, SCREEN_WIDTH - 2*DRAW_OFFSET, SCREEN_HEIGHT - 2*DRAW_OFFSET])

	# 맵 그리기
	# convert = mapImage.astype('int') * 256
	# frame = pygame.surfarray.make_surface(np.rot90(mapImage.astype('int') * 255, 3))
	tmp = Image.fromarray(np.rot90(mapImage.astype('int') * 255, 3)).resize((SCREEN_WIDTH - 2*DRAW_OFFSET, SCREEN_HEIGHT - 2*DRAW_OFFSET), resample=Image.Resampling.NEAREST)
	frame = pygame.surfarray.make_surface(np.array(tmp))

	screen.blit(frame, (DRAW_OFFSET, DRAW_OFFSET))
	# for y in range(n):
	# 	for x in range(n):
	# 		if mapImage[y][x]:
	# 			drawX = DRAW_OFFSET + x * ((SCREEN_WIDTH - DRAW_OFFSET*2) / n)
	# 			drawY = SCREEN_HEIGHT - DRAW_OFFSET - y * ((SCREEN_HEIGHT - DRAW_OFFSET*2) / n)

	# 			pygame.draw.rect(screen, WHITE, [drawX, drawY, ((SCREEN_WIDTH - DRAW_OFFSET*2) / n) + 1, ((SCREEN_HEIGHT - DRAW_OFFSET*2) / n) + 1])

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

		elif event.type == pygame.MOUSEBUTTONDOWN:
			if event.button == 1: #좌클
				boxStartPos = pygame.mouse.get_pos()
				boxDragging = True
			elif event.button == 2:
				boxStartPos = pygame.mouse.get_pos()
				moveDragging = True
			elif event.button == 3:
				# print("우클")
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
					# mapX -offset + 2*offset/cnt*x
					
					x0 = mapY - mapShowOffset + 2*mapShowOffset*x0/(SCREEN_WIDTH-2*DRAW_OFFSET)
					x1 = mapY - mapShowOffset + 2*mapShowOffset*x1/(SCREEN_WIDTH-2*DRAW_OFFSET)
					y0 = mapX - mapShowOffset + 2*mapShowOffset*y0/(SCREEN_WIDTH-2*DRAW_OFFSET)
					y1 = mapX - mapShowOffset + 2*mapShowOffset*y1/(SCREEN_WIDTH-2*DRAW_OFFSET)
					# print((x0, y0), (x1, y1))

					mapShowOffset = x1 - x0

					mapY = (x0+x1)/2
					mapX = (y0+y1)/2

					# 레전드 뻘짓 mapX랑 mapY랑 반대임

					# mapY += (pygame.mouse.get_pos()[0] - boxStartPos[0]) / (SCREEN_WIDTH -2*DRAW_OFFSET)
					# mapY += 

					isDrawn, oneChunckLen = getResetedDraw(n, mapY, mapShowOffset, chunk)
			elif event.button == 2:
				if moveDragging:
					moveDragging = False
					mapY -= 2*mapShowOffset*(pygame.mouse.get_pos()[0] - boxStartPos[0]) / (SCREEN_WIDTH -2*DRAW_OFFSET)
					mapX += 2*mapShowOffset*(pygame.mouse.get_pos()[1] - boxStartPos[1]) / (SCREEN_WIDTH -2*DRAW_OFFSET)

					isDrawn, oneChunckLen = getResetedDraw(n, mapY, mapShowOffset, chunk)

			elif event.button == 3:
				# mapX = 0
				# mapY = 0
				if not boxDragging and not moveDragging:
					mapShowOffset = mapShowOffset*2
					# print("2배 축소")

					isDrawn, oneChunckLen = getResetedDraw(n, mapY, mapShowOffset, chunk)
				# pass

			if event.button != 1:
				boxDragging = False
			if event.button != 2:
				moveDragging = False