# (x, y, eps) = (-0.384393118817151, -1.5874003621860764e-05, 0.0003083735432563672)
# (x, y, eps) = (-0.3843898916521634, -1.1724742340572109e-06, 3.944312762581444e-05)
# (x, y, eps) = (-0.21402109248242293, -7.030827474311524e-05, 0.00749594375338021)
# (x, y, eps) = (-0.2210163540971984, 0.14249926434528387, 1.071365218763276e-12)
# (x, y, eps) = (-0.1706742352043414, -1.618367701470524e-07, 9.698385790992751e-05)
# (x, y, eps) = (-0.17064195363863055, 1.8294229843056375e-07, 4.504690208706064e-06)
(x, y, eps) = (-0.17080164459249791, 0.00014076592124136352, 1.599822221218705e-07)


import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from numba import njit, boolean

n = 500
x0 = x
y0 = y


#parameters - tetration계산 관련
max_iter = 500 #최대 몇층까지 계산할 것인지를 정함. max_iter층 만큼 계산했는데 복소수 크기가 escape_radius를 벗어나지 않으면 수렴한것으로 처리.
escape_radius = 1e+10 #복소수크기가 escape_radius를 벗어나면 발산한 것으로 처리함.

@njit
def compute_tetration_divergence(n, max_iter, escape_radius):
    x = np.linspace(x0 - eps, x0 + eps, n)
    y = np.linspace(y0 - eps, y0 + eps, n)
    c = x[:, np.newaxis] + 1j * y[np.newaxis, :]

    divergence_map = np.zeros((n, n), dtype=boolean)

    for i in range(n):
        for j in range(n):
            c_val = c[i, j]
            z = c_val

            for k in range(max_iter):
                z = c_val ** z
                if np.abs(z) > escape_radius:
                    divergence_map[i, j] = True
                    break

    return divergence_map

#tetration 계산
divergence_map = compute_tetration_divergence(n, max_iter, escape_radius)

#plot
cmap = LinearSegmentedColormap.from_list("custom_cmap", ["black", "white"]) # 커스텀 컬러맵 생성: 발산은 흰색, 수렴은 검은색
plt.imshow(divergence_map.T, extent=[x0 - eps, x0 + eps, y0 - eps, y0 + eps], origin='lower', cmap=cmap)
plt.axis('off')  # 축 라벨과 타이틀 제거
filename = f"mytetration_x_{x0}_y_{y0}_eps_{eps}.png"
plt.savefig(filename, dpi=600, bbox_inches='tight', pad_inches=0)
plt.show()