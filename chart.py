# -*- coding: utf-8 -*-
"""
Created on Thu Nov  2 16:46:02 2023

@author: kentang
"""

import drawsvg as draw
import math
import re

#第一層中間, 第二層八門
def gen_chart(first_layer, second_layer, sixth_layer):
    # ... [rest of your setup code remains the same]
    # Create an SVG drawing canvas
    d = draw.Drawing(390, 390, origin="center")
    # Set the donut's radii and number of divisions for each layer
    inner_radius = 13
    layer_gap = 45  # Gap between layers
    num_divisions = [1, 8, 16, 16]
    # Define the data for each layer
    #general = dict(zip(list("貴蛇雀合勾龍空虎常玄陰后"),re.findall('..', '貴人螣蛇朱雀六合勾陳青龍天空白虎常侍玄武太陰太后')))
    #skygeneral = [general.get(i) for i in skygeneral]
    data = [
        [first_layer],
        second_layer,
         [['巳','大神','楚'], ['午','大威','荊州'], ['未','天道','秦'], ['坤','大武','梁州'], ['申','武德','晉'], ['酉','太簇','趙雍'], ['戌','陰主','魯'], ['乾','陰德','冀州'], ['亥','大義','衛'], ['子','地主','齊兗'], ['丑','陽德','吳'], ['艮','和德','青州'], ['寅','呂申','燕'], ['卯','高叢','徐州'], ['辰','太陽','鄭'], ['巽','大炅','揚州']],
        #[['巳','大神'], ['午','大威'], ['未','天道'], ['坤','大武'], ['申','武德'], ['酉','太簇'], ['戌','陰主'], ['乾','陰德'], ['亥','大義'], ['子','地主'], ['丑','陽德'], ['艮','和德'], ['寅','呂申'], ['卯','高叢'], ['辰','太陽'], ['巽','大炅']],
        #['楚', '荊州', '秦', '梁州', '晉', '趙雍', '魯', '冀州', '衛', '齊兗', '吳', '青州', '燕', '徐州', '鄭', '揚州'],
        sixth_layer,
    ]
    rotation_angle = 248
    for layer_index, divisions in enumerate(num_divisions):
        layer_group = draw.Group(id=f'layer{layer_index + 1}')  # Group each layer for independent movement

        for division in range(divisions):
            start_angle = (360 / divisions) * division + rotation_angle
            end_angle = (360 / divisions) * (division + 1) + rotation_angle
            label = data[layer_index][division]

            inner = inner_radius + layer_index * layer_gap
            outer = inner_radius + (layer_index + 1) * layer_gap

            # Calculate start and end points for both inner and outer arcs
            start_outer_x, start_outer_y = outer * math.cos(math.radians(start_angle)), outer * math.sin(math.radians(start_angle))
            end_outer_x, end_outer_y = outer * math.cos(math.radians(end_angle)), outer * math.sin(math.radians(end_angle))
            start_inner_x, start_inner_y = inner * math.cos(math.radians(start_angle)), inner * math.sin(math.radians(start_angle))
            end_inner_x, end_inner_y = inner * math.cos(math.radians(end_angle)), inner * math.sin(math.radians(end_angle))

            path = draw.Path(stroke='white', stroke_width=1.8, fill='black')
            path.M(start_inner_x, start_inner_y)  # Move to the start point on the inner radius
            path.L(start_outer_x, start_outer_y)  # Line to the start point on the outer radius
            path.A(outer, outer, 0, 0, 1, end_outer_x, end_outer_y)  # Outer arc
            path.L(end_inner_x, end_inner_y)  # Line to the end point on the inner radius
            path.A(inner, inner, 0, 0, 0, start_inner_x, start_inner_y)  # Inner arc
            path.Z()  # Close the path
            layer_group.append(path)

            # Add labels to the pie slices
            label_x = (inner + outer) / 2 * math.cos(math.radians((start_angle + end_angle) / 2))
            label_y = (inner + outer) / 2 * math.sin(math.radians((start_angle + end_angle) / 2))
            label_text = draw.Text(label, 9, label_x, label_y, center=1, fill='white')
            layer_group.append(label_text)

        # Append the group for this layer to the main drawing
        d.append(layer_group)
    # ... [rest of your code remains the same]

    return d.as_svg().replace('''<path d="M-4.86988571440686,-12.053390109368236 L-21.72718241812291,-53.776663564873665 A58,58,0,0,1,-21.727182418122876,-53.77666356487368 L-4.869885714406852,-12.053390109368237 A13,13,0,0,0,-4.86988571440686,-12.053390109368236 Z" stroke="white" stroke-width="1.8" fill="black" />''', "")

#太乙命法盤
def gen_chart_life(second_layer, twelve, sixth_layer):
    # ... [rest of your setup code remains the same]
    # Create an SVG drawing canvas
    d = draw.Drawing(350, 350, origin="center")
    # Set the donut's radii and number of divisions for each layer
    inner_radius = 12
    layer_gap = 35  # Gap between layers
    num_divisions = [1, 12, 12, 12]
    # Define the data for each layer
    #general = dict(zip(list("貴蛇雀合勾龍空虎常玄陰后"),re.findall('..', '貴人螣蛇朱雀六合勾陳青龍天空白虎常侍玄武太陰太后')))
    #skygeneral = [general.get(i) for i in skygeneral]
    data = [
        [second_layer],
        twelve,
         ['巳', '午', '未', '申', '酉', '戌', '亥', '子', '丑', '寅','卯', '辰'],
        #[['巳','大神'], ['午','大威'], ['未','天道'], ['坤','大武'], ['申','武德'], ['酉','太簇'], ['戌','陰主'], ['乾','陰德'], ['亥','大義'], ['子','地主'], ['丑','陽德'], ['艮','和德'], ['寅','呂申'], ['卯','高叢'], ['辰','太陽'], ['巽','大炅']],
        #['楚', '荊州', '秦', '梁州', '晉', '趙雍', '魯', '冀州', '衛', '齊兗', '吳', '青州', '燕', '徐州', '鄭', '揚州'],
        sixth_layer
    ]
    rotation_angle = 248
    for layer_index, divisions in enumerate(num_divisions):
        layer_group = draw.Group(id=f'layer{layer_index + 1}')  # Group each layer for independent movement

        for division in range(divisions):
            start_angle = (360 / divisions) * division + rotation_angle
            end_angle = (360 / divisions) * (division + 1) + rotation_angle
            label = data[layer_index][division]

            inner = inner_radius + layer_index * layer_gap
            outer = inner_radius + (layer_index + 1) * layer_gap

            # Calculate start and end points for both inner and outer arcs
            start_outer_x, start_outer_y = outer * math.cos(math.radians(start_angle)), outer * math.sin(math.radians(start_angle))
            end_outer_x, end_outer_y = outer * math.cos(math.radians(end_angle)), outer * math.sin(math.radians(end_angle))
            start_inner_x, start_inner_y = inner * math.cos(math.radians(start_angle)), inner * math.sin(math.radians(start_angle))
            end_inner_x, end_inner_y = inner * math.cos(math.radians(end_angle)), inner * math.sin(math.radians(end_angle))

            path = draw.Path(stroke='white', stroke_width=1.8, fill='black')
            path.M(start_inner_x, start_inner_y)  # Move to the start point on the inner radius
            path.L(start_outer_x, start_outer_y)  # Line to the start point on the outer radius
            path.A(outer, outer, 0, 0, 1, end_outer_x, end_outer_y)  # Outer arc
            path.L(end_inner_x, end_inner_y)  # Line to the end point on the inner radius
            path.A(inner, inner, 0, 0, 0, start_inner_x, start_inner_y)  # Inner arc
            path.Z()  # Close the path
            layer_group.append(path)

            # Add labels to the pie slices
            label_x = (inner + outer) / 2 * math.cos(math.radians((start_angle + end_angle) / 2))
            label_y = (inner + outer) / 2 * math.sin(math.radians((start_angle + end_angle) / 2))
            label_text = draw.Text(label, 9, label_x, label_y, center=1, fill='white')
            layer_group.append(label_text)

        # Append the group for this layer to the main drawing
        d.append(layer_group)
    # ... [rest of your code remains the same]
    return d.as_svg().replace('''<path d="M-4.495279120990947,-11.126206254801447 L-17.606509890547876,-43.577641164639005 A47,47,0,0,1,-17.606509890547848,-43.57764116463901 L-4.49527912099094,-11.12620625480145 A12,12,0,0,0,-4.495279120990947,-11.126206254801447 Z" stroke="white" stroke-width="1.8" fill="black" />''', "")
#日家太乙盤
#第一層中間, 第二層八門
def gen_chart_day(first_layer, second_layer, golden, sixth_layer):
    # ... [rest of your setup code remains the same]
    # Create an SVG drawing canvas
    d = draw.Drawing(360, 360, origin="center")
    # Set the donut's radii and number of divisions for each layer
    inner_radius = 3
    layer_gap = 31.5  # Gap between layers
    num_divisions = [1, 8, 8, 16, 16]
    # Define the data for each layer
    #general = dict(zip(list("貴蛇雀合勾龍空虎常玄陰后"),re.findall('..', '貴人螣蛇朱雀六合勾陳青龍天空白虎常侍玄武太陰太后')))
    #skygeneral = [general.get(i) for i in skygeneral]
    data = [
        [first_layer],
        second_layer,
        golden,
         [['巳','大神','楚'], ['午','大威','荊州'], ['未','天道','秦'], ['坤','大武','梁州'], ['申','武德','晉'], ['酉','太簇','趙雍'], ['戌','陰主','魯'], ['乾','陰德','冀州'], ['亥','大義','衛'], ['子','地主','齊兗'], ['丑','陽德','吳'], ['艮','和德','青州'], ['寅','呂申','燕'], ['卯','高叢','徐州'], ['辰','太陽','鄭'], ['巽','大炅','揚州']],
        #[['巳','大神'], ['午','大威'], ['未','天道'], ['坤','大武'], ['申','武德'], ['酉','太簇'], ['戌','陰主'], ['乾','陰德'], ['亥','大義'], ['子','地主'], ['丑','陽德'], ['艮','和德'], ['寅','呂申'], ['卯','高叢'], ['辰','太陽'], ['巽','大炅']],
        #['楚', '荊州', '秦', '梁州', '晉', '趙雍', '魯', '冀州', '衛', '齊兗', '吳', '青州', '燕', '徐州', '鄭', '揚州'],
        sixth_layer,
    ]
    rotation_angle = 248
    for layer_index, divisions in enumerate(num_divisions):
        layer_group = draw.Group(id=f'layer{layer_index + 1}')  # Group each layer for independent movement

        for division in range(divisions):
            start_angle = (360 / divisions) * division + rotation_angle
            end_angle = (360 / divisions) * (division + 1) + rotation_angle
            label = data[layer_index][division]

            inner = inner_radius + layer_index * layer_gap
            outer = inner_radius + (layer_index + 1) * layer_gap

            # Calculate start and end points for both inner and outer arcs
            start_outer_x, start_outer_y = outer * math.cos(math.radians(start_angle)), outer * math.sin(math.radians(start_angle))
            end_outer_x, end_outer_y = outer * math.cos(math.radians(end_angle)), outer * math.sin(math.radians(end_angle))
            start_inner_x, start_inner_y = inner * math.cos(math.radians(start_angle)), inner * math.sin(math.radians(start_angle))
            end_inner_x, end_inner_y = inner * math.cos(math.radians(end_angle)), inner * math.sin(math.radians(end_angle))

            path = draw.Path(stroke='white', stroke_width=1.8, fill='black')
            path.M(start_inner_x, start_inner_y)  # Move to the start point on the inner radius
            path.L(start_outer_x, start_outer_y)  # Line to the start point on the outer radius
            path.A(outer, outer, 0, 0, 1, end_outer_x, end_outer_y)  # Outer arc
            path.L(end_inner_x, end_inner_y)  # Line to the end point on the inner radius
            path.A(inner, inner, 0, 0, 0, start_inner_x, start_inner_y)  # Inner arc
            path.Z()  # Close the path
            layer_group.append(path)

            # Add labels to the pie slices
            label_x = (inner + outer) / 2 * math.cos(math.radians((start_angle + end_angle) / 2))
            label_y = (inner + outer) / 2 * math.sin(math.radians((start_angle + end_angle) / 2))
            label_text = draw.Text(label, 9, label_x, label_y, center=1, fill='white')
            layer_group.append(label_text)

        # Append the group for this layer to the main drawing
        d.append(layer_group)
    return d.as_svg().replace('''<path d="M-1.1238197802477368,-2.781551563700362 L-12.923927472848973,-31.987842982554163 A34.5,34.5,0,0,1,-12.923927472848954,-31.98784298255417 L-1.123819780247735,-2.7815515637003627 A3.0,3.0,0,0,0,-1.1238197802477368,-2.781551563700362 Z" stroke="white" stroke-width="1.8" fill="black" />''', "")

#第一層中間, 第二層八門
def gen_chart_hour(first_layer, second_layer, skygeneral, sixth_layer, twentyeight):
    # ... [rest of your setup code remains the same]
    # Create an SVG drawing canvas
    d = draw.Drawing(386, 386, origin="center")
    # Set the donut's radii and number of divisions for each layer
    inner_radius = 3
    layer_gap = 31.5  # Gap between layers
    num_divisions = [1, 8, 16, 16, 16,28]
    # Define the data for each layer
    #general = dict(zip(list("貴蛇雀合勾龍空虎常玄陰后"),re.findall('..', '貴人螣蛇朱雀六合勾陳青龍天空白虎常侍玄武太陰太后')))
    #skygeneral = [general.get(i) for i in skygeneral]
    data = [
        [first_layer],
        second_layer,
        skygeneral,
         [['巳','大神','楚'], ['午','大威','荊州'], ['未','天道','秦'], ['坤','大武','梁州'], ['申','武德','晉'], ['酉','太簇','趙雍'], ['戌','陰主','魯'], ['乾','陰德','冀州'], ['亥','大義','衛'], ['子','地主','齊兗'], ['丑','陽德','吳'], ['艮','和德','青州'], ['寅','呂申','燕'], ['卯','高叢','徐州'], ['辰','太陽','鄭'], ['巽','大炅','揚州']],
        #[['巳','大神'], ['午','大威'], ['未','天道'], ['坤','大武'], ['申','武德'], ['酉','太簇'], ['戌','陰主'], ['乾','陰德'], ['亥','大義'], ['子','地主'], ['丑','陽德'], ['艮','和德'], ['寅','呂申'], ['卯','高叢'], ['辰','太陽'], ['巽','大炅']],
        #['楚', '荊州', '秦', '梁州', '晉', '趙雍', '魯', '冀州', '衛', '齊兗', '吳', '青州', '燕', '徐州', '鄭', '揚州'],
        sixth_layer,
        twentyeight
    ]
    rotation_angle = 248

    for layer_index, divisions in enumerate(num_divisions):
        layer_group = draw.Group(id=f'layer{layer_index + 1}')  # Group each layer for independent movement

        for division in range(divisions):
            start_angle = (360 / divisions) * division + rotation_angle
            end_angle = (360 / divisions) * (division + 1) + rotation_angle
            label = data[layer_index][division]

            inner = inner_radius + layer_index * layer_gap
            outer = inner_radius + (layer_index + 1) * layer_gap

            # Calculate start and end points for both inner and outer arcs
            start_outer_x, start_outer_y = outer * math.cos(math.radians(start_angle)), outer * math.sin(math.radians(start_angle))
            end_outer_x, end_outer_y = outer * math.cos(math.radians(end_angle)), outer * math.sin(math.radians(end_angle))
            start_inner_x, start_inner_y = inner * math.cos(math.radians(start_angle)), inner * math.sin(math.radians(start_angle))
            end_inner_x, end_inner_y = inner * math.cos(math.radians(end_angle)), inner * math.sin(math.radians(end_angle))

            path = draw.Path(stroke='white', stroke_width=1.8, fill='black')
            path.M(start_inner_x, start_inner_y)  # Move to the start point on the inner radius
            path.L(start_outer_x, start_outer_y)  # Line to the start point on the outer radius
            path.A(outer, outer, 0, 0, 1, end_outer_x, end_outer_y)  # Outer arc
            path.L(end_inner_x, end_inner_y)  # Line to the end point on the inner radius
            path.A(inner, inner, 0, 0, 0, start_inner_x, start_inner_y)  # Inner arc
            path.Z()  # Close the path
            layer_group.append(path)

            # Add labels to the pie slices
            label_x = (inner + outer) / 2 * math.cos(math.radians((start_angle + end_angle) / 2))
            label_y = (inner + outer) / 2 * math.sin(math.radians((start_angle + end_angle) / 2))
            label_text = draw.Text(label, 9, label_x, label_y, center=1, fill='white')
            layer_group.append(label_text)

        # Append the group for this layer to the main drawing
        d.append(layer_group)
    return d.as_svg().replace('''<path d="M-1.1238197802477368,-2.781551563700362 L-12.923927472848973,-31.987842982554163 A34.5,34.5,0,0,1,-12.923927472848954,-31.98784298255417 L-1.123819780247735,-2.7815515637003627 A3.0,3.0,0,0,0,-1.1238197802477368,-2.781551563700362 Z" stroke="white" stroke-width="1.8" fill="black" />''', "")

