# (x, y, eps) = (-0.384393118817151, -1.5874003621860764e-05, 0.0003083735432563672)
# (x, y, eps) = (-0.3843898916521634, -1.1724742340572109e-06, 3.944312762581444e-05)
# (x, y, eps) = (-0.21402109248242293, -7.030827474311524e-05, 0.00749594375338021)
# (x, y, eps) = (-0.2210163540971984, 0.14249926434528387, 1.071365218763276e-12)
# (x, y, eps) = (-0.1706742352043414, -1.618367701470524e-07, 9.698385790992751e-05)
# (x, y, eps) = (-0.17064195363863055, 1.8294229843056375e-07, 4.504690208706064e-06)
# (x, y, eps) = (-0.17080164459249791, 0.00014076592124136352, 1.599822221218705e-07)
# (x, y, eps) = (-4.092177063946319, 3.0747094571840123e-07, 0.00018889330771918792)
# (x, y, eps) = (112.89926261247915, -522.6153047043296, 0.3604750392753431)
# (x, y, eps) = (-4.092091494224315, 6.373055911519406e-07, 0.0002991870417993755)
# (x, y, eps) = (2.7963927778374145, -0.0033871017876906046, 0.13456595726031595)
# (x, y, eps) = (-4.133455857425457, 0.00010204360319003184, 4.1756587472097415e-06)
# (x, y, eps) = (-4.133439593177311, 0.00011276978589557028, 1.0351947055640964e-11)
# (x, y, eps) = (-4.13343959315193, 0.00011276980316066802, 2.0068439409728044e-11)
# (x, y, eps) = (-4.086116071588547, 9.38070759198438e-10, 1.2490200196995116e-07)
# (x, y, eps) = (-4.0861172452798415, 7.287713992363359e-12, 1.1148431096635038e-09)
(x, y, eps) = (0, 0, 4)


import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from numba import njit, boolean

n = 1024
x0 = x
y0 = y


#parameters - tetration계산 관련
max_iter = 200 #최대 몇층까지 계산할 것인지를 정함. max_iter층 만큼 계산했는데 복소수 크기가 escape_radius를 벗어나지 않으면 수렴한것으로 처리.
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