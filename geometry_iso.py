import gs
import gs.plus.render as render
import math
import random
import numpy as np

# [256]
edgeTable = [0x0, 0x109, 0x203, 0x30a, 0x406, 0x50f, 0x605, 0x70c,
			 0x80c, 0x905, 0xa0f, 0xb06, 0xc0a, 0xd03, 0xe09, 0xf00,
			 0x190, 0x99, 0x393, 0x29a, 0x596, 0x49f, 0x795, 0x69c,
			 0x99c, 0x895, 0xb9f, 0xa96, 0xd9a, 0xc93, 0xf99, 0xe90,
			 0x230, 0x339, 0x33, 0x13a, 0x636, 0x73f, 0x435, 0x53c,
			 0xa3c, 0xb35, 0x83f, 0x936, 0xe3a, 0xf33, 0xc39, 0xd30,
			 0x3a0, 0x2a9, 0x1a3, 0xaa, 0x7a6, 0x6af, 0x5a5, 0x4ac,
			 0xbac, 0xaa5, 0x9af, 0x8a6, 0xfaa, 0xea3, 0xda9, 0xca0,
			 0x460, 0x569, 0x663, 0x76a, 0x66, 0x16f, 0x265, 0x36c,
			 0xc6c, 0xd65, 0xe6f, 0xf66, 0x86a, 0x963, 0xa69, 0xb60,
			 0x5f0, 0x4f9, 0x7f3, 0x6fa, 0x1f6, 0xff, 0x3f5, 0x2fc,
			 0xdfc, 0xcf5, 0xfff, 0xef6, 0x9fa, 0x8f3, 0xbf9, 0xaf0,
			 0x650, 0x759, 0x453, 0x55a, 0x256, 0x35f, 0x55, 0x15c,
			 0xe5c, 0xf55, 0xc5f, 0xd56, 0xa5a, 0xb53, 0x859, 0x950,
			 0x7c0, 0x6c9, 0x5c3, 0x4ca, 0x3c6, 0x2cf, 0x1c5, 0xcc,
			 0xfcc, 0xec5, 0xdcf, 0xcc6, 0xbca, 0xac3, 0x9c9, 0x8c0,
			 0x8c0, 0x9c9, 0xac3, 0xbca, 0xcc6, 0xdcf, 0xec5, 0xfcc,
			 0xcc, 0x1c5, 0x2cf, 0x3c6, 0x4ca, 0x5c3, 0x6c9, 0x7c0,
			 0x950, 0x859, 0xb53, 0xa5a, 0xd56, 0xc5f, 0xf55, 0xe5c,
			 0x15c, 0x55, 0x35f, 0x256, 0x55a, 0x453, 0x759, 0x650,
			 0xaf0, 0xbf9, 0x8f3, 0x9fa, 0xef6, 0xfff, 0xcf5, 0xdfc,
			 0x2fc, 0x3f5, 0xff, 0x1f6, 0x6fa, 0x7f3, 0x4f9, 0x5f0,
			 0xb60, 0xa69, 0x963, 0x86a, 0xf66, 0xe6f, 0xd65, 0xc6c,
			 0x36c, 0x265, 0x16f, 0x66, 0x76a, 0x663, 0x569, 0x460,
			 0xca0, 0xda9, 0xea3, 0xfaa, 0x8a6, 0x9af, 0xaa5, 0xbac,
			 0x4ac, 0x5a5, 0x6af, 0x7a6, 0xaa, 0x1a3, 0x2a9, 0x3a0,
			 0xd30, 0xc39, 0xf33, 0xe3a, 0x936, 0x83f, 0xb35, 0xa3c,
			 0x53c, 0x435, 0x73f, 0x636, 0x13a, 0x33, 0x339, 0x230,
			 0xe90, 0xf99, 0xc93, 0xd9a, 0xa96, 0xb9f, 0x895, 0x99c,
			 0x69c, 0x795, 0x49f, 0x596, 0x29a, 0x393, 0x99, 0x190,
			 0xf00, 0xe09, 0xd03, 0xc0a, 0xb06, 0xa0f, 0x905, 0x80c,
			 0x70c, 0x605, 0x50f, 0x406, 0x30a, 0x203, 0x109, 0x0]
# [256][16]
triTable = [[-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
			[0, 8, 3, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
			[0, 1, 9, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
			[1, 8, 3, 9, 8, 1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
			[1, 2, 10, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
			[0, 8, 3, 1, 2, 10, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
			[9, 2, 10, 0, 2, 9, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
			[2, 8, 3, 2, 10, 8, 10, 9, 8, -1, -1, -1, -1, -1, -1, -1],
			[3, 11, 2, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
			[0, 11, 2, 8, 11, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
			[1, 9, 0, 2, 3, 11, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
			[1, 11, 2, 1, 9, 11, 9, 8, 11, -1, -1, -1, -1, -1, -1, -1],
			[3, 10, 1, 11, 10, 3, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
			[0, 10, 1, 0, 8, 10, 8, 11, 10, -1, -1, -1, -1, -1, -1, -1],
			[3, 9, 0, 3, 11, 9, 11, 10, 9, -1, -1, -1, -1, -1, -1, -1],
			[9, 8, 10, 10, 8, 11, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
			[4, 7, 8, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
			[4, 3, 0, 7, 3, 4, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
			[0, 1, 9, 8, 4, 7, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
			[4, 1, 9, 4, 7, 1, 7, 3, 1, -1, -1, -1, -1, -1, -1, -1],
			[1, 2, 10, 8, 4, 7, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
			[3, 4, 7, 3, 0, 4, 1, 2, 10, -1, -1, -1, -1, -1, -1, -1],
			[9, 2, 10, 9, 0, 2, 8, 4, 7, -1, -1, -1, -1, -1, -1, -1],
			[2, 10, 9, 2, 9, 7, 2, 7, 3, 7, 9, 4, -1, -1, -1, -1],
			[8, 4, 7, 3, 11, 2, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
			[11, 4, 7, 11, 2, 4, 2, 0, 4, -1, -1, -1, -1, -1, -1, -1],
			[9, 0, 1, 8, 4, 7, 2, 3, 11, -1, -1, -1, -1, -1, -1, -1],
			[4, 7, 11, 9, 4, 11, 9, 11, 2, 9, 2, 1, -1, -1, -1, -1],
			[3, 10, 1, 3, 11, 10, 7, 8, 4, -1, -1, -1, -1, -1, -1, -1],
			[1, 11, 10, 1, 4, 11, 1, 0, 4, 7, 11, 4, -1, -1, -1, -1],
			[4, 7, 8, 9, 0, 11, 9, 11, 10, 11, 0, 3, -1, -1, -1, -1],
			[4, 7, 11, 4, 11, 9, 9, 11, 10, -1, -1, -1, -1, -1, -1, -1],
			[9, 5, 4, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
			[9, 5, 4, 0, 8, 3, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
			[0, 5, 4, 1, 5, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
			[8, 5, 4, 8, 3, 5, 3, 1, 5, -1, -1, -1, -1, -1, -1, -1],
			[1, 2, 10, 9, 5, 4, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
			[3, 0, 8, 1, 2, 10, 4, 9, 5, -1, -1, -1, -1, -1, -1, -1],
			[5, 2, 10, 5, 4, 2, 4, 0, 2, -1, -1, -1, -1, -1, -1, -1],
			[2, 10, 5, 3, 2, 5, 3, 5, 4, 3, 4, 8, -1, -1, -1, -1],
			[9, 5, 4, 2, 3, 11, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
			[0, 11, 2, 0, 8, 11, 4, 9, 5, -1, -1, -1, -1, -1, -1, -1],
			[0, 5, 4, 0, 1, 5, 2, 3, 11, -1, -1, -1, -1, -1, -1, -1],
			[2, 1, 5, 2, 5, 8, 2, 8, 11, 4, 8, 5, -1, -1, -1, -1],
			[10, 3, 11, 10, 1, 3, 9, 5, 4, -1, -1, -1, -1, -1, -1, -1],
			[4, 9, 5, 0, 8, 1, 8, 10, 1, 8, 11, 10, -1, -1, -1, -1],
			[5, 4, 0, 5, 0, 11, 5, 11, 10, 11, 0, 3, -1, -1, -1, -1],
			[5, 4, 8, 5, 8, 10, 10, 8, 11, -1, -1, -1, -1, -1, -1, -1],
			[9, 7, 8, 5, 7, 9, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
			[9, 3, 0, 9, 5, 3, 5, 7, 3, -1, -1, -1, -1, -1, -1, -1],
			[0, 7, 8, 0, 1, 7, 1, 5, 7, -1, -1, -1, -1, -1, -1, -1],
			[1, 5, 3, 3, 5, 7, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
			[9, 7, 8, 9, 5, 7, 10, 1, 2, -1, -1, -1, -1, -1, -1, -1],
			[10, 1, 2, 9, 5, 0, 5, 3, 0, 5, 7, 3, -1, -1, -1, -1],
			[8, 0, 2, 8, 2, 5, 8, 5, 7, 10, 5, 2, -1, -1, -1, -1],
			[2, 10, 5, 2, 5, 3, 3, 5, 7, -1, -1, -1, -1, -1, -1, -1],
			[7, 9, 5, 7, 8, 9, 3, 11, 2, -1, -1, -1, -1, -1, -1, -1],
			[9, 5, 7, 9, 7, 2, 9, 2, 0, 2, 7, 11, -1, -1, -1, -1],
			[2, 3, 11, 0, 1, 8, 1, 7, 8, 1, 5, 7, -1, -1, -1, -1],
			[11, 2, 1, 11, 1, 7, 7, 1, 5, -1, -1, -1, -1, -1, -1, -1],
			[9, 5, 8, 8, 5, 7, 10, 1, 3, 10, 3, 11, -1, -1, -1, -1],
			[5, 7, 0, 5, 0, 9, 7, 11, 0, 1, 0, 10, 11, 10, 0, -1],
			[11, 10, 0, 11, 0, 3, 10, 5, 0, 8, 0, 7, 5, 7, 0, -1],
			[11, 10, 5, 7, 11, 5, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
			[10, 6, 5, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
			[0, 8, 3, 5, 10, 6, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
			[9, 0, 1, 5, 10, 6, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
			[1, 8, 3, 1, 9, 8, 5, 10, 6, -1, -1, -1, -1, -1, -1, -1],
			[1, 6, 5, 2, 6, 1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
			[1, 6, 5, 1, 2, 6, 3, 0, 8, -1, -1, -1, -1, -1, -1, -1],
			[9, 6, 5, 9, 0, 6, 0, 2, 6, -1, -1, -1, -1, -1, -1, -1],
			[5, 9, 8, 5, 8, 2, 5, 2, 6, 3, 2, 8, -1, -1, -1, -1],
			[2, 3, 11, 10, 6, 5, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
			[11, 0, 8, 11, 2, 0, 10, 6, 5, -1, -1, -1, -1, -1, -1, -1],
			[0, 1, 9, 2, 3, 11, 5, 10, 6, -1, -1, -1, -1, -1, -1, -1],
			[5, 10, 6, 1, 9, 2, 9, 11, 2, 9, 8, 11, -1, -1, -1, -1],
			[6, 3, 11, 6, 5, 3, 5, 1, 3, -1, -1, -1, -1, -1, -1, -1],
			[0, 8, 11, 0, 11, 5, 0, 5, 1, 5, 11, 6, -1, -1, -1, -1],
			[3, 11, 6, 0, 3, 6, 0, 6, 5, 0, 5, 9, -1, -1, -1, -1],
			[6, 5, 9, 6, 9, 11, 11, 9, 8, -1, -1, -1, -1, -1, -1, -1],
			[5, 10, 6, 4, 7, 8, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
			[4, 3, 0, 4, 7, 3, 6, 5, 10, -1, -1, -1, -1, -1, -1, -1],
			[1, 9, 0, 5, 10, 6, 8, 4, 7, -1, -1, -1, -1, -1, -1, -1],
			[10, 6, 5, 1, 9, 7, 1, 7, 3, 7, 9, 4, -1, -1, -1, -1],
			[6, 1, 2, 6, 5, 1, 4, 7, 8, -1, -1, -1, -1, -1, -1, -1],
			[1, 2, 5, 5, 2, 6, 3, 0, 4, 3, 4, 7, -1, -1, -1, -1],
			[8, 4, 7, 9, 0, 5, 0, 6, 5, 0, 2, 6, -1, -1, -1, -1],
			[7, 3, 9, 7, 9, 4, 3, 2, 9, 5, 9, 6, 2, 6, 9, -1],
			[3, 11, 2, 7, 8, 4, 10, 6, 5, -1, -1, -1, -1, -1, -1, -1],
			[5, 10, 6, 4, 7, 2, 4, 2, 0, 2, 7, 11, -1, -1, -1, -1],
			[0, 1, 9, 4, 7, 8, 2, 3, 11, 5, 10, 6, -1, -1, -1, -1],
			[9, 2, 1, 9, 11, 2, 9, 4, 11, 7, 11, 4, 5, 10, 6, -1],
			[8, 4, 7, 3, 11, 5, 3, 5, 1, 5, 11, 6, -1, -1, -1, -1],
			[5, 1, 11, 5, 11, 6, 1, 0, 11, 7, 11, 4, 0, 4, 11, -1],
			[0, 5, 9, 0, 6, 5, 0, 3, 6, 11, 6, 3, 8, 4, 7, -1],
			[6, 5, 9, 6, 9, 11, 4, 7, 9, 7, 11, 9, -1, -1, -1, -1],
			[10, 4, 9, 6, 4, 10, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
			[4, 10, 6, 4, 9, 10, 0, 8, 3, -1, -1, -1, -1, -1, -1, -1],
			[10, 0, 1, 10, 6, 0, 6, 4, 0, -1, -1, -1, -1, -1, -1, -1],
			[8, 3, 1, 8, 1, 6, 8, 6, 4, 6, 1, 10, -1, -1, -1, -1],
			[1, 4, 9, 1, 2, 4, 2, 6, 4, -1, -1, -1, -1, -1, -1, -1],
			[3, 0, 8, 1, 2, 9, 2, 4, 9, 2, 6, 4, -1, -1, -1, -1],
			[0, 2, 4, 4, 2, 6, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
			[8, 3, 2, 8, 2, 4, 4, 2, 6, -1, -1, -1, -1, -1, -1, -1],
			[10, 4, 9, 10, 6, 4, 11, 2, 3, -1, -1, -1, -1, -1, -1, -1],
			[0, 8, 2, 2, 8, 11, 4, 9, 10, 4, 10, 6, -1, -1, -1, -1],
			[3, 11, 2, 0, 1, 6, 0, 6, 4, 6, 1, 10, -1, -1, -1, -1],
			[6, 4, 1, 6, 1, 10, 4, 8, 1, 2, 1, 11, 8, 11, 1, -1],
			[9, 6, 4, 9, 3, 6, 9, 1, 3, 11, 6, 3, -1, -1, -1, -1],
			[8, 11, 1, 8, 1, 0, 11, 6, 1, 9, 1, 4, 6, 4, 1, -1],
			[3, 11, 6, 3, 6, 0, 0, 6, 4, -1, -1, -1, -1, -1, -1, -1],
			[6, 4, 8, 11, 6, 8, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
			[7, 10, 6, 7, 8, 10, 8, 9, 10, -1, -1, -1, -1, -1, -1, -1],
			[0, 7, 3, 0, 10, 7, 0, 9, 10, 6, 7, 10, -1, -1, -1, -1],
			[10, 6, 7, 1, 10, 7, 1, 7, 8, 1, 8, 0, -1, -1, -1, -1],
			[10, 6, 7, 10, 7, 1, 1, 7, 3, -1, -1, -1, -1, -1, -1, -1],
			[1, 2, 6, 1, 6, 8, 1, 8, 9, 8, 6, 7, -1, -1, -1, -1],
			[2, 6, 9, 2, 9, 1, 6, 7, 9, 0, 9, 3, 7, 3, 9, -1],
			[7, 8, 0, 7, 0, 6, 6, 0, 2, -1, -1, -1, -1, -1, -1, -1],
			[7, 3, 2, 6, 7, 2, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
			[2, 3, 11, 10, 6, 8, 10, 8, 9, 8, 6, 7, -1, -1, -1, -1],
			[2, 0, 7, 2, 7, 11, 0, 9, 7, 6, 7, 10, 9, 10, 7, -1],
			[1, 8, 0, 1, 7, 8, 1, 10, 7, 6, 7, 10, 2, 3, 11, -1],
			[11, 2, 1, 11, 1, 7, 10, 6, 1, 6, 7, 1, -1, -1, -1, -1],
			[8, 9, 6, 8, 6, 7, 9, 1, 6, 11, 6, 3, 1, 3, 6, -1],
			[0, 9, 1, 11, 6, 7, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
			[7, 8, 0, 7, 0, 6, 3, 11, 0, 11, 6, 0, -1, -1, -1, -1],
			[7, 11, 6, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
			[7, 6, 11, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
			[3, 0, 8, 11, 7, 6, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
			[0, 1, 9, 11, 7, 6, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
			[8, 1, 9, 8, 3, 1, 11, 7, 6, -1, -1, -1, -1, -1, -1, -1],
			[10, 1, 2, 6, 11, 7, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
			[1, 2, 10, 3, 0, 8, 6, 11, 7, -1, -1, -1, -1, -1, -1, -1],
			[2, 9, 0, 2, 10, 9, 6, 11, 7, -1, -1, -1, -1, -1, -1, -1],
			[6, 11, 7, 2, 10, 3, 10, 8, 3, 10, 9, 8, -1, -1, -1, -1],
			[7, 2, 3, 6, 2, 7, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
			[7, 0, 8, 7, 6, 0, 6, 2, 0, -1, -1, -1, -1, -1, -1, -1],
			[2, 7, 6, 2, 3, 7, 0, 1, 9, -1, -1, -1, -1, -1, -1, -1],
			[1, 6, 2, 1, 8, 6, 1, 9, 8, 8, 7, 6, -1, -1, -1, -1],
			[10, 7, 6, 10, 1, 7, 1, 3, 7, -1, -1, -1, -1, -1, -1, -1],
			[10, 7, 6, 1, 7, 10, 1, 8, 7, 1, 0, 8, -1, -1, -1, -1],
			[0, 3, 7, 0, 7, 10, 0, 10, 9, 6, 10, 7, -1, -1, -1, -1],
			[7, 6, 10, 7, 10, 8, 8, 10, 9, -1, -1, -1, -1, -1, -1, -1],
			[6, 8, 4, 11, 8, 6, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
			[3, 6, 11, 3, 0, 6, 0, 4, 6, -1, -1, -1, -1, -1, -1, -1],
			[8, 6, 11, 8, 4, 6, 9, 0, 1, -1, -1, -1, -1, -1, -1, -1],
			[9, 4, 6, 9, 6, 3, 9, 3, 1, 11, 3, 6, -1, -1, -1, -1],
			[6, 8, 4, 6, 11, 8, 2, 10, 1, -1, -1, -1, -1, -1, -1, -1],
			[1, 2, 10, 3, 0, 11, 0, 6, 11, 0, 4, 6, -1, -1, -1, -1],
			[4, 11, 8, 4, 6, 11, 0, 2, 9, 2, 10, 9, -1, -1, -1, -1],
			[10, 9, 3, 10, 3, 2, 9, 4, 3, 11, 3, 6, 4, 6, 3, -1],
			[8, 2, 3, 8, 4, 2, 4, 6, 2, -1, -1, -1, -1, -1, -1, -1],
			[0, 4, 2, 4, 6, 2, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
			[1, 9, 0, 2, 3, 4, 2, 4, 6, 4, 3, 8, -1, -1, -1, -1],
			[1, 9, 4, 1, 4, 2, 2, 4, 6, -1, -1, -1, -1, -1, -1, -1],
			[8, 1, 3, 8, 6, 1, 8, 4, 6, 6, 10, 1, -1, -1, -1, -1],
			[10, 1, 0, 10, 0, 6, 6, 0, 4, -1, -1, -1, -1, -1, -1, -1],
			[4, 6, 3, 4, 3, 8, 6, 10, 3, 0, 3, 9, 10, 9, 3, -1],
			[10, 9, 4, 6, 10, 4, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
			[4, 9, 5, 7, 6, 11, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
			[0, 8, 3, 4, 9, 5, 11, 7, 6, -1, -1, -1, -1, -1, -1, -1],
			[5, 0, 1, 5, 4, 0, 7, 6, 11, -1, -1, -1, -1, -1, -1, -1],
			[11, 7, 6, 8, 3, 4, 3, 5, 4, 3, 1, 5, -1, -1, -1, -1],
			[9, 5, 4, 10, 1, 2, 7, 6, 11, -1, -1, -1, -1, -1, -1, -1],
			[6, 11, 7, 1, 2, 10, 0, 8, 3, 4, 9, 5, -1, -1, -1, -1],
			[7, 6, 11, 5, 4, 10, 4, 2, 10, 4, 0, 2, -1, -1, -1, -1],
			[3, 4, 8, 3, 5, 4, 3, 2, 5, 10, 5, 2, 11, 7, 6, -1],
			[7, 2, 3, 7, 6, 2, 5, 4, 9, -1, -1, -1, -1, -1, -1, -1],
			[9, 5, 4, 0, 8, 6, 0, 6, 2, 6, 8, 7, -1, -1, -1, -1],
			[3, 6, 2, 3, 7, 6, 1, 5, 0, 5, 4, 0, -1, -1, -1, -1],
			[6, 2, 8, 6, 8, 7, 2, 1, 8, 4, 8, 5, 1, 5, 8, -1],
			[9, 5, 4, 10, 1, 6, 1, 7, 6, 1, 3, 7, -1, -1, -1, -1],
			[1, 6, 10, 1, 7, 6, 1, 0, 7, 8, 7, 0, 9, 5, 4, -1],
			[4, 0, 10, 4, 10, 5, 0, 3, 10, 6, 10, 7, 3, 7, 10, -1],
			[7, 6, 10, 7, 10, 8, 5, 4, 10, 4, 8, 10, -1, -1, -1, -1],
			[6, 9, 5, 6, 11, 9, 11, 8, 9, -1, -1, -1, -1, -1, -1, -1],
			[3, 6, 11, 0, 6, 3, 0, 5, 6, 0, 9, 5, -1, -1, -1, -1],
			[0, 11, 8, 0, 5, 11, 0, 1, 5, 5, 6, 11, -1, -1, -1, -1],
			[6, 11, 3, 6, 3, 5, 5, 3, 1, -1, -1, -1, -1, -1, -1, -1],
			[1, 2, 10, 9, 5, 11, 9, 11, 8, 11, 5, 6, -1, -1, -1, -1],
			[0, 11, 3, 0, 6, 11, 0, 9, 6, 5, 6, 9, 1, 2, 10, -1],
			[11, 8, 5, 11, 5, 6, 8, 0, 5, 10, 5, 2, 0, 2, 5, -1],
			[6, 11, 3, 6, 3, 5, 2, 10, 3, 10, 5, 3, -1, -1, -1, -1],
			[5, 8, 9, 5, 2, 8, 5, 6, 2, 3, 8, 2, -1, -1, -1, -1],
			[9, 5, 6, 9, 6, 0, 0, 6, 2, -1, -1, -1, -1, -1, -1, -1],
			[1, 5, 8, 1, 8, 0, 5, 6, 8, 3, 8, 2, 6, 2, 8, -1],
			[1, 5, 6, 2, 1, 6, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
			[1, 3, 6, 1, 6, 10, 3, 8, 6, 5, 6, 9, 8, 9, 6, -1],
			[10, 1, 0, 10, 0, 6, 9, 5, 0, 5, 6, 0, -1, -1, -1, -1],
			[0, 3, 8, 5, 6, 10, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
			[10, 5, 6, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
			[11, 5, 10, 7, 5, 11, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
			[11, 5, 10, 11, 7, 5, 8, 3, 0, -1, -1, -1, -1, -1, -1, -1],
			[5, 11, 7, 5, 10, 11, 1, 9, 0, -1, -1, -1, -1, -1, -1, -1],
			[10, 7, 5, 10, 11, 7, 9, 8, 1, 8, 3, 1, -1, -1, -1, -1],
			[11, 1, 2, 11, 7, 1, 7, 5, 1, -1, -1, -1, -1, -1, -1, -1],
			[0, 8, 3, 1, 2, 7, 1, 7, 5, 7, 2, 11, -1, -1, -1, -1],
			[9, 7, 5, 9, 2, 7, 9, 0, 2, 2, 11, 7, -1, -1, -1, -1],
			[7, 5, 2, 7, 2, 11, 5, 9, 2, 3, 2, 8, 9, 8, 2, -1],
			[2, 5, 10, 2, 3, 5, 3, 7, 5, -1, -1, -1, -1, -1, -1, -1],
			[8, 2, 0, 8, 5, 2, 8, 7, 5, 10, 2, 5, -1, -1, -1, -1],
			[9, 0, 1, 5, 10, 3, 5, 3, 7, 3, 10, 2, -1, -1, -1, -1],
			[9, 8, 2, 9, 2, 1, 8, 7, 2, 10, 2, 5, 7, 5, 2, -1],
			[1, 3, 5, 3, 7, 5, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
			[0, 8, 7, 0, 7, 1, 1, 7, 5, -1, -1, -1, -1, -1, -1, -1],
			[9, 0, 3, 9, 3, 5, 5, 3, 7, -1, -1, -1, -1, -1, -1, -1],
			[9, 8, 7, 5, 9, 7, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
			[5, 8, 4, 5, 10, 8, 10, 11, 8, -1, -1, -1, -1, -1, -1, -1],
			[5, 0, 4, 5, 11, 0, 5, 10, 11, 11, 3, 0, -1, -1, -1, -1],
			[0, 1, 9, 8, 4, 10, 8, 10, 11, 10, 4, 5, -1, -1, -1, -1],
			[10, 11, 4, 10, 4, 5, 11, 3, 4, 9, 4, 1, 3, 1, 4, -1],
			[2, 5, 1, 2, 8, 5, 2, 11, 8, 4, 5, 8, -1, -1, -1, -1],
			[0, 4, 11, 0, 11, 3, 4, 5, 11, 2, 11, 1, 5, 1, 11, -1],
			[0, 2, 5, 0, 5, 9, 2, 11, 5, 4, 5, 8, 11, 8, 5, -1],
			[9, 4, 5, 2, 11, 3, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
			[2, 5, 10, 3, 5, 2, 3, 4, 5, 3, 8, 4, -1, -1, -1, -1],
			[5, 10, 2, 5, 2, 4, 4, 2, 0, -1, -1, -1, -1, -1, -1, -1],
			[3, 10, 2, 3, 5, 10, 3, 8, 5, 4, 5, 8, 0, 1, 9, -1],
			[5, 10, 2, 5, 2, 4, 1, 9, 2, 9, 4, 2, -1, -1, -1, -1],
			[8, 4, 5, 8, 5, 3, 3, 5, 1, -1, -1, -1, -1, -1, -1, -1],
			[0, 4, 5, 1, 0, 5, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
			[8, 4, 5, 8, 5, 3, 9, 0, 5, 0, 3, 5, -1, -1, -1, -1],
			[9, 4, 5, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
			[4, 11, 7, 4, 9, 11, 9, 10, 11, -1, -1, -1, -1, -1, -1, -1],
			[0, 8, 3, 4, 9, 7, 9, 11, 7, 9, 10, 11, -1, -1, -1, -1],
			[1, 10, 11, 1, 11, 4, 1, 4, 0, 7, 4, 11, -1, -1, -1, -1],
			[3, 1, 4, 3, 4, 8, 1, 10, 4, 7, 4, 11, 10, 11, 4, -1],
			[4, 11, 7, 9, 11, 4, 9, 2, 11, 9, 1, 2, -1, -1, -1, -1],
			[9, 7, 4, 9, 11, 7, 9, 1, 11, 2, 11, 1, 0, 8, 3, -1],
			[11, 7, 4, 11, 4, 2, 2, 4, 0, -1, -1, -1, -1, -1, -1, -1],
			[11, 7, 4, 11, 4, 2, 8, 3, 4, 3, 2, 4, -1, -1, -1, -1],
			[2, 9, 10, 2, 7, 9, 2, 3, 7, 7, 4, 9, -1, -1, -1, -1],
			[9, 10, 7, 9, 7, 4, 10, 2, 7, 8, 7, 0, 2, 0, 7, -1],
			[3, 7, 10, 3, 10, 2, 7, 4, 10, 1, 10, 0, 4, 0, 10, -1],
			[1, 10, 2, 8, 7, 4, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
			[4, 9, 1, 4, 1, 7, 7, 1, 3, -1, -1, -1, -1, -1, -1, -1],
			[4, 9, 1, 4, 1, 7, 0, 8, 1, 8, 7, 1, -1, -1, -1, -1],
			[4, 0, 3, 7, 4, 3, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
			[4, 8, 7, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
			[9, 10, 8, 10, 11, 8, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
			[3, 0, 9, 3, 9, 11, 11, 9, 10, -1, -1, -1, -1, -1, -1, -1],
			[0, 1, 10, 0, 10, 8, 8, 10, 11, -1, -1, -1, -1, -1, -1, -1],
			[3, 1, 10, 11, 3, 10, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
			[1, 2, 11, 1, 11, 9, 9, 11, 8, -1, -1, -1, -1, -1, -1, -1],
			[3, 0, 9, 3, 9, 11, 1, 2, 9, 2, 11, 9, -1, -1, -1, -1],
			[0, 2, 11, 8, 0, 11, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
			[3, 2, 11, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
			[2, 3, 8, 2, 8, 10, 10, 8, 9, -1, -1, -1, -1, -1, -1, -1],
			[9, 10, 2, 0, 9, 2, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
			[2, 3, 8, 2, 8, 10, 0, 1, 8, 1, 10, 8, -1, -1, -1, -1],
			[1, 10, 2, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
			[1, 3, 8, 9, 1, 8, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
			[0, 9, 1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
			[0, 3, 8, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
			[-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]]


def get_index_to_create_it(vtx_array, normal_array, vtx):
	"""check if this vtx exist"""
	# for i in range(len(vtx_array)):
	# 	if vtx_array[i] == vtx:
	# 		return i

	# didn't found the vertx , so add it and s the new index
	normal_array.append(gs.Vector3(random.random(), random.random(), random.random()))
	vtx_array.append(vtx)
	return len(vtx_array) - 1


def Lerp2Vertex(isolevel, p1, p2, valp1, valp2):
	"""Linearly interpolate the position where an isosurface cuts an edge between two vertices, each with their own scalar value"""
	if abs(isolevel - valp1) < 0.00001:
		return p1

	if abs(isolevel - valp2) < 0.00001:
		return p2

	if abs(valp1 - valp2) < 0.00001:
		return p1

	mu = (isolevel - valp1) / (valp2 - valp1)
	return p1 + (p2 - p1) * mu


def IsoSurface(cube_val, cube_base_vtx, isolevel, index_array, vtx_array, normal_array, offset):
	"""Determine the index into the edge table which tells us which vertices are inside of the surface"""
	cubeindex = 0
	index_value = 1
	for val in range(8):
		if cube_val[val] < isolevel:
			cubeindex = cubeindex + index_value

		index_value = 2 ** (val + 1)

	# Cube is entirely in/out of the surface
	if edgeTable[cubeindex] == 0:
		return 0

	vertlist = [0] * 12
	#    Find the vertices where the surface intersects the dwarf_geo
	if edgeTable[cubeindex] & 1:
		vertlist[0] = Lerp2Vertex(isolevel, cube_base_vtx[0], cube_base_vtx[1], cube_val[0], cube_val[1])

	if edgeTable[cubeindex] & 2:
		vertlist[1] = Lerp2Vertex(isolevel, cube_base_vtx[1], cube_base_vtx[2], cube_val[1], cube_val[2])

	if edgeTable[cubeindex] & 4:
		vertlist[2] = Lerp2Vertex(isolevel, cube_base_vtx[2], cube_base_vtx[3], cube_val[2], cube_val[3])

	if edgeTable[cubeindex] & 8:
		vertlist[3] = Lerp2Vertex(isolevel, cube_base_vtx[3], cube_base_vtx[0], cube_val[3], cube_val[0])

	if edgeTable[cubeindex] & 16:
		vertlist[4] = Lerp2Vertex(isolevel, cube_base_vtx[4], cube_base_vtx[5], cube_val[4], cube_val[5])

	if edgeTable[cubeindex] & 32:
		vertlist[5] = Lerp2Vertex(isolevel, cube_base_vtx[5], cube_base_vtx[6], cube_val[5], cube_val[6])

	if edgeTable[cubeindex] & 64:
		vertlist[6] = Lerp2Vertex(isolevel, cube_base_vtx[6], cube_base_vtx[7], cube_val[6], cube_val[7])

	if edgeTable[cubeindex] & 128:
		vertlist[7] = Lerp2Vertex(isolevel, cube_base_vtx[7], cube_base_vtx[4], cube_val[7], cube_val[4])

	if edgeTable[cubeindex] & 256:
		vertlist[8] = Lerp2Vertex(isolevel, cube_base_vtx[0], cube_base_vtx[4], cube_val[0], cube_val[4])

	if edgeTable[cubeindex] & 512:
		vertlist[9] = Lerp2Vertex(isolevel, cube_base_vtx[1], cube_base_vtx[5], cube_val[1], cube_val[5])

	if edgeTable[cubeindex] & 1024:
		vertlist[10] = Lerp2Vertex(isolevel, cube_base_vtx[2], cube_base_vtx[6], cube_val[2], cube_val[6])

	if edgeTable[cubeindex] & 2048:
		vertlist[11] = Lerp2Vertex(isolevel, cube_base_vtx[3], cube_base_vtx[7], cube_val[3], cube_val[7])

	#    Create the triangles and app to the big list
	nbtri = 0
	i = 0
	while triTable[cubeindex][i] != -1:
		index_array.append(get_index_to_create_it(vtx_array, normal_array, vertlist[triTable[cubeindex][i]] + offset))
		index_array.append(get_index_to_create_it(vtx_array, normal_array, vertlist[triTable[cubeindex][i + 2]] + offset))
		index_array.append(get_index_to_create_it(vtx_array, normal_array, vertlist[triTable[cubeindex][i + 1]] + offset))
		nbtri += 1
		i += 3

	return nbtri


half_size = 0.5
cube_base_vtx = [gs.Vector3(-half_size, -half_size, -half_size), gs.Vector3(half_size, -half_size, -half_size),
				 gs.Vector3(half_size, -half_size, half_size), gs.Vector3(-half_size, -half_size, half_size),
				 gs.Vector3(-half_size, half_size, -half_size), gs.Vector3(half_size, half_size, -half_size),
				 gs.Vector3(half_size, half_size, half_size), gs.Vector3(-half_size, half_size, half_size)]

def find_valid_material_in_cube(x, y, z, mats):
	"""find valid material in one of the 8 corners"""
	mat = mats[x, y, z]
	if mat == 0:
		mat = mats[x, y+1, z]
	if mat == 0 and x+1 < mats.shape[0]:
		mat = mats[x+1, y, z]
		if mat == 0:
			mat = mats[x+1, y+1, z]
		if mat == 0 and z+1 < mats.shape[2]:
			mat = mats[x, y, z+1]
			if mat == 0:
				mat = mats[x, y+1, z+1]
			if mat == 0:
				mat = mats[x+1, y, z+1]
				if mat == 0:
					mat = mats[x+1, y+1, z+1]

	return mat

resolution = 2
resolution_y = 4

def CreateIsoFBO(array, width, height, length, isolevel, mats):
	index_array = []
	vtx_array = []
	normal_array = []
	material_array = []

	for x in range(width - 1):
		for y in range(height - 1):
			for z in range(length - 1):
				cube_val = [array[x, y, z], array[x + 1, y, z], array[x + 1, y, z + 1], array[x, y, z + 1],
							array[x, y + 1, z], array[x + 1, y + 1, z], array[x + 1, y + 1, z + 1],	array[x, y + 1, z + 1]]
				offset = gs.Vector3(x, y, z)
				nb_tri = IsoSurface(cube_val, cube_base_vtx, isolevel, index_array, vtx_array, normal_array, offset)
				for i in range(int(nb_tri)):
					material_array.append(find_valid_material_in_cube(x//resolution, 0, z//resolution, mats))

	return index_array, vtx_array, normal_array, material_array


def create_iso_c(array, width, height, length, mats, isolevel=0.5, material_path=None, name=None):

	# increase size of the array by the resolution
	array_res = np.kron(array, np.ones((resolution, resolution_y, resolution)))
	for i in range(1, array_res.shape[1]-1):
		array_res[:, i, :] = array_res[:, 0, :]

	# add floor if there is floor on the bottom
	mats_res = np.kron(mats, np.ones((resolution, 1, resolution)))
	id = np.where(mats_res[:, 0, :] == 1)
	array_res[id[0], 0, id[1]] = 1

	id = np.where(mats_res[:, 1, :] == 1)
	array_res[id[0], array_res.shape[1]-1, id[1]] = 1

	# for the ramp, if ramp down, add 1 to half the height
	id = np.where(mats_res[:, 0, :] == 6)
	array_res[id[0], :array_res.shape[1]*0.5, id[1]] = 1

	id = np.where(mats_res[:, 1, :] == 6)
	array_res[id[0], array_res.shape[1]-1, id[1]] = 1

	if array_res.sum() == 0 or np.average(array_res) == 1:
		return None

	# # smooth the value on XZ axis
	# # array_copy = np.copy(array_res)
	# # kernel_size = 3
	# # kernel = np.array([[0.25, 0.5, 0.25],
	# # 				  [0.5,  1.0, 0.5],
	# # 				  [0.25, 0.5, 0.25]])
	# # kernel_sum = kernel.sum()
	# # kernel_size_half = kernel_size // 2
	# # for smooth_pass in range(1):
	# # 	for x in range(kernel_size_half, array_res.shape[0] -kernel_size_half-1):
	# # 		for y in range(array_res.shape[1]):
	# # 			for z in range(kernel_size_half, array_res.shape[2] -kernel_size_half-1):
	# # 				array_res[x, y, z] = (array_copy[x-kernel_size_half:x+kernel_size_half+1, y, z-kernel_size_half:z+kernel_size_half+1]*kernel).sum() / kernel_sum
	#
	w, h, d = array_res.shape[0]-(resolution - 1), array_res.shape[1], array_res.shape[2]-(resolution - 1)

	# check floor
	# id = np.where(mats[:, 0, :] == 1)
	# array[id[0], 0, id[1]] = 1
	#
	# id = np.where(mats[:, 1, :] == 1)
	# array[id[0], array.shape[1]-1, id[1]] = 1
	#
	# # for the ramp, if ramp down, add 1 to half the height
	# id = np.where(mats[:, 0, :] == 6)
	# array[id[0], :array.shape[1]*0.5, id[1]] = 1
	#
	# id = np.where(mats[:, 1, :] == 6)
	# array[id[0], array.shape[1]-1, id[1]] = 1
	#
	# if array.sum() == 0 or np.average(array) == 1:
	# 	return None

	# w, h, d = array.shape[0], array.shape[1], array.shape[2]

	field = gs.BinaryBlob()

	field.Grow(w*d*h)
	for i in range(w*d*h):
		field.WriteFloat(0)

	def write_to_field(x, y, z, v):
		x, y, z = int(x), int(y), int(z)
		o = (w * d * y + w * z + x) * 4
		field.WriteFloatAt(v, o)


	for x in range(w):
		for y in range(h):
			for z in range(d):
				write_to_field(x, y, z, float(array_res[x, y, z]))
				# write_to_field(x, y, z, float(array[x, y, z]))

	# it = np.nditer(array_res, flags=['multi_index'])
	# # it = np.nditer(array, flags=['multi_index'])
	# while not it.finished:
	# 	write_to_field(it.multi_index[0], it.multi_index[1], it.multi_index[2], float(array_res[it.multi_index[0], it.multi_index[1], it.multi_index[2]]))
	# 	# write_to_field(it.multi_index[0], it.multi_index[1], it.multi_index[2], float(array[it.multi_index[0], it.multi_index[1], it.multi_index[2]]))
	# 	it.iternext()

	iso = gs.IsoSurface()

	inv_scale = gs.Vector3.One/gs.Vector3(resolution, resolution_y*2-1, resolution)
	gs.PolygoniseIsoSurface(w, h, d, field, isolevel, iso, inv_scale)
	# if not gs.PolygoniseIsoSurface(w, h, d, field, isolevel, iso):
	# 	return None

	# mat = render.load_material("iso.mat")
	mat = render.load_material("@core/materials/default.mat")
	geo = gs.RenderGeometry()
	gs.IsoSurfaceToRenderGeometry(render.get_render_system(), iso, geo, mat)

	return geo


def create_iso(array, width, height, length, mats, isolevel=0.5, material_path=None, name=None):
	"""Create an iso surface geometry"""
	if name is None:
		name = "@gen/iso_%f" % (isolevel)
	name = str(name)

	geo = render.get_render_system().HasGeometry(name)
	if geo is not None:
		return geo

	geo = gs.CoreGeometry()
	if material_path is None:
		material_path = "@core/materials/default.mat"

	geo.SetName(name)

	if type(material_path) is not list:
		geo.AllocateMaterialTable(1)
		geo.SetMaterial(0, material_path, True)
	else:
		geo.AllocateMaterialTable(len(material_path))
		count = 0
		for path in material_path:
			geo.SetMaterial(count, path, True)
			count += 1

	# increase size of the array by the resolution
	array_res = np.kron(array, np.ones((resolution, resolution_y, resolution)))
	for i in range(1, array_res.shape[1]-1):
		array_res[:, i, :] = array_res[:, 0, :]

	# add floor if there is floor on the bottom
	mats_res = np.kron(mats, np.ones((resolution, 1, resolution)))
	id = np.where(mats_res[:, 0, :] == 1)
	array_res[id[0], 0, id[1]] = 1

	id = np.where(mats_res[:, 1, :] == 1)
	array_res[id[0], array_res.shape[1]-1, id[1]] = 1

	if array_res.sum() == 0 or np.average(array_res) == 1:
		return None

	# smooth the value on XZ axis
	array_copy = np.copy(array_res)
	kernel_size = 3
	kernel = np.array([[0.25, 0.5, 0.25],
					  [0.5,  1.0, 0.5],
					  [0.25, 0.5, 0.25]])
	kernel_sum = kernel.sum()
	kernel_size_half = kernel_size // 2
	for smooth_pass in range(1):
		for x in range(kernel_size_half, array_res.shape[0] -kernel_size_half-1):
			for y in range(array_res.shape[1]):
				for z in range(kernel_size_half, array_res.shape[2] -kernel_size_half-1):
					array_res[x, y, z] = (array_copy[x-kernel_size_half:x+kernel_size_half+1, y, z-kernel_size_half:z+kernel_size_half+1]*kernel).sum() / kernel_sum

	# create the iso surface
	index_array, vtx_array, normal_array, material_array = CreateIsoFBO(array_res, array_res.shape[0]-(resolution - 1), array_res.shape[1], array_res.shape[2]-(resolution - 1), isolevel, mats)

	# generate vertices
	if not geo.AllocateVertex(len(vtx_array)):
		return None

	# send the vertices to the geometry with scaling them down to the right size
	count = 0
	inv_scale = gs.Vector3.One/gs.Vector3(resolution, resolution_y*2-1, resolution)
	for vtx in vtx_array:
		geo.SetVertex(count, vtx.x*inv_scale.x, vtx.y*inv_scale.y, vtx.z*inv_scale.z)
		count += 1

	# build polygons
	if not geo.AllocatePolygon(len(index_array) // 3):
		return None

	for n in range(len(index_array) // 3):
		geo.SetPolygon(n, 3, 0)

	if not geo.AllocatePolygonBinding():
		return None

	for n in range(len(index_array) // 3):
		geo.SetPolygonMaterialIndex(n, int(material_array[n]))
		geo.SetPolygonBinding(n, [index_array[n * 3], index_array[n * 3 + 1], index_array[n * 3 + 2]])

	geo.ComputeVertexNormal(math.radians(40))
	geo.ComputeVertexTangent()

	return render.create_geometry(geo)
