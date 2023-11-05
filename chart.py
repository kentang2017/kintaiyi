# -*- coding: utf-8 -*-
"""
Created on Thu Nov  2 16:46:02 2023

@author: kentang
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Nov  1 15:03:52 2023

@author: kentang
"""

import drawsvg as draw
import math


#第一層中間, 第二層八門
def gen_chart(first_layer, second_layer, sixth_layer):
    # Create an SVG drawing canvas
    d = draw.Drawing(380, 380, origin='center')
    # Set the donut's radii and number of divisions for each layer
    inner_radius = 20
    layer_gap = 35  # Gap between layers
    num_divisions = [1, 8, 16, 16, 16]
    # Define the data for each layer
    data = [
        [first_layer],
        second_layer,
        ['巳', '午', '未', '坤', '申', '酉', '戌', '乾', '亥', '子', '丑', '艮', '寅', '卯', '辰', '巽'],
        ['大神', '大威', '天道', '大武', '武德', '太簇', '陰主', '陰德', '大義', '地主', '陽德', '和德', '呂申', '高叢', '太陽', '大炅'],
        #['楚', '荊州', '秦', '梁州', '晉', '趙雍', '魯', '冀州', '衛', '齊兗', '吳', '青州', '燕', '徐州', '鄭', '揚州'],
        sixth_layer
    ]
    rotation_angle = 248
    # Draw the donut chart
    for layer_index, divisions in enumerate(num_divisions):
        for division in range(divisions):
            start_angle = (360 / divisions) * division + rotation_angle
            end_angle = (360 / divisions) * (division + 1) + rotation_angle
            label = data[layer_index][division]
    
            # Calculate the layer's inner and outer radius
            inner = inner_radius + layer_index * layer_gap
            outer = inner_radius + (layer_index + 1) * layer_gap
            path = draw.Path(stroke='white', stroke_width=1, fill='black')
            path.M(inner * math.cos(math.radians(start_angle)), inner * math.sin(math.radians(start_angle)))  # Move to the start point on the inner radius
            path.L(outer * math.cos(math.radians(start_angle)), outer * math.sin(math.radians(start_angle)))  # Line to the start point on the outer radius
            path.A(outer, outer, 0, 0, 1, outer * math.cos(math.radians(end_angle)), outer * math.sin(math.radians(end_angle)))  # Arc to the end point on the outer radius
            path.L(inner * math.cos(math.radians(end_angle)), inner * math.sin(math.radians(end_angle)))  # Line back to the start point on the inner radius
            path.Z()  # Close the path
            d.append(path)
    
            # Add labels to the pie slices
            label_x = (inner + outer) / 2 * math.cos(math.radians((start_angle + end_angle) / 2))
            label_y = (inner + outer) / 2 * math.sin(math.radians((start_angle + end_angle) / 2))
            #if divisions == 1:
            #    label_text = draw.Text(label, 8, label_x, label_y, center=1, fill='black')
            #else:
            label_text = draw.Text(label, 8, label_x, label_y, center=1, fill='white')
            d.append(label_text)
    #center_text = draw.Text("a", 40, center_x, center_y, center=1, fill="#ffffff")
    # Save the SVG file
      # Change this angle to the desired rotation
    return d.as_svg().replace('''<path d="M-7.492131868318246,-18.543677091335745 L-20.603362637875176,-50.995112001173304 A55,55,0,0,1,-20.603362637875144,-50.99511200117331 L-7.492131868318234,-18.543677091335752 Z" stroke="white" stroke-width="1" fill="black" />''', "")
