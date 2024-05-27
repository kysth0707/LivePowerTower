import pygame
from numba import njit, boolean
import numpy as np

# 그림 함수
@njit
def compute_tetration_divergence(x0, y0, x1, y1, width, height, max_iter = 500, escape_radius = 1e+10):
	x = np.linspace(x0, x1, n)
	y = np.linspace(y0, y1, chunk)
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

ScreenWidth, ScreenHeight = (800, 800)
screen = pygame.display.set_mode((ScreenWidth, ScreenHeight))

# 변수 리셋
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)

DRAW_OFFSET = 20
DRAW_COUNT_BY_A_FRAME = 5

# 화소 및 데이터 변경
n = 256
max_iter = 500
escape_radius = 1e+10


# 청크로 나누기
# 청크 X 청크로 보여줌
chunk = 16

# 현재 위치
mapX = 0
mapY = 0
mapShowOffset = 5e-1

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
				tmp = compute_tetration_divergence(mapX - mapShowOffset, y, mapX + mapShowOffset, y+oneChunckLen, n, chunk)
				length = int(n/chunk)
				mapImage[:,mapdrawy*length:(mapdrawy+1)*length] = tmp

				isDrawn['map'][key] = True
				break
			
		if drawAll:
			isDrawn['drawAll'] = True
			print(f"(x, y, eps) = ({mapX}, {mapY}, {mapShowOffset})")
		

	# 화면 그리기
	screen.fill((127, 127, 127))
	pygame.draw.rect(screen, BLACK, [DRAW_OFFSET, DRAW_OFFSET, ScreenWidth - 2*DRAW_OFFSET, ScreenHeight - 2*DRAW_OFFSET])

	# 맵 그리기
	for y in range(n):
		for x in range(n):
			if mapImage[y][x]:
				drawX = DRAW_OFFSET + x * ((ScreenWidth - DRAW_OFFSET*2) / n)
				drawY = ScreenHeight - DRAW_OFFSET - y * ((ScreenHeight - DRAW_OFFSET*2) / n)

				pygame.draw.rect(screen, WHITE, [drawX, drawY, ((ScreenWidth - DRAW_OFFSET*2) / n) + 1, ((ScreenHeight - DRAW_OFFSET*2) / n) + 1])

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
				print("우클")
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
					y0=(ScreenHeight - y0)
					x1-=DRAW_OFFSET
					y1=(ScreenHeight - y1)
					# mapX -offset + 2*offset/cnt*x
					
					x0 = mapY - mapShowOffset + 2*mapShowOffset*x0/(ScreenWidth-2*DRAW_OFFSET)
					x1 = mapY - mapShowOffset + 2*mapShowOffset*x1/(ScreenWidth-2*DRAW_OFFSET)
					y0 = mapX - mapShowOffset + 2*mapShowOffset*y0/(ScreenWidth-2*DRAW_OFFSET)
					y1 = mapX - mapShowOffset + 2*mapShowOffset*y1/(ScreenWidth-2*DRAW_OFFSET)
					# print((x0, y0), (x1, y1))

					mapShowOffset = x1 - x0

					mapY = (x0+x1)/2
					mapX = (y0+y1)/2

					# 레전드 뻘짓 mapX랑 mapY랑 반대임

					# mapY += (pygame.mouse.get_pos()[0] - boxStartPos[0]) / (ScreenWidth -2*DRAW_OFFSET)
					# mapY += 

					isDrawn, oneChunckLen = getResetedDraw(n, mapY, mapShowOffset, chunk)
			elif event.button == 2:
				if moveDragging:
					moveDragging = False
					mapY -= 2*mapShowOffset*(pygame.mouse.get_pos()[0] - boxStartPos[0]) / (ScreenWidth -2*DRAW_OFFSET)
					mapX += 2*mapShowOffset*(pygame.mouse.get_pos()[1] - boxStartPos[1]) / (ScreenWidth -2*DRAW_OFFSET)

					isDrawn, oneChunckLen = getResetedDraw(n, mapY, mapShowOffset, chunk)

			elif event.button == 3:
				# mapX = 0
				# mapY = 0
				mapShowOffset = mapShowOffset*2
				print("2배 축소")

				isDrawn, oneChunckLen = getResetedDraw(n, mapY, mapShowOffset, chunk)
				# pass

			if event.button != 1:
				boxDragging = False
			if event.button != 2:
				moveDragging = False