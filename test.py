from colour import Color
red = Color('red')
colors = list(red.range_to(Color("green"),10))
print(Color.get_rgb(colors[0]))