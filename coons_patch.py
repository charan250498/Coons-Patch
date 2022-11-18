import bpy
import bmesh

def read_control_points(filename):
    control_points = []
    for line in open(filename, 'r'):
        values = line.split()
        values = [float(values[0]), float(values[1]), float(values[2])]
        control_points.append(values)
    return control_points

def get_bezier_curve_points(P):
    P = [P[0], P[1], P[3], P[2]]
    curve_points = []
    for u in range(num_points):
        u = u/num_points
        x = P[0][0]*((1-u)**3) + P[1][0]*(((1-u)**2)*u*3) + P[2][0]*((1-u)*(u**2)*3) + P[3][0]*(u**3)
        y = P[0][1]*((1-u)**3) + P[1][1]*(((1-u)**2)*u*3) + P[2][1]*((1-u)*(u**2)*3) + P[3][1]*(u**3)
        z = P[0][2]*((1-u)**3) + P[1][2]*(((1-u)**2)*u*3) + P[2][2]*((1-u)*(u**2)*3) + P[3][2]*(u**3)
        curve_points.append([x, y, z])
    return curve_points

def linear_interpolate(curve0, curve1):
    linear_interpolated_curve = []
    denominator = num_points
    for i in range(num_points):
        row = []
        for j in range(num_points):
            x = (1-(i/denominator)) * curve0[j][0] + (i/denominator) * curve1[j][0]
            y = (1-(i/denominator)) * curve0[j][1] + (i/denominator) * curve1[j][1]
            z = (1-(i/denominator)) * curve0[j][2] + (i/denominator) * curve1[j][2]
            row.append([x, y, z])
        linear_interpolated_curve.append(row)
    return linear_interpolated_curve

def bilinear_interpolate(c0, c1, d0, d1):
    bilinear_interpolated_curve = []
    denominator = num_points
    for i in range(num_points):
        row = []
        for j in range(num_points):
            x = c0[0][0] * (1-(i/denominator)) * (1-(j/denominator)) + c0[num_points-1][0] * (i/denominator) * (1-(j/denominator)) + c1[0][0] * (1-(i/denominator)) * (j/denominator) + c1[num_points-1][0] * (i/denominator) * (j/denominator)
            y = c0[0][1] * (1-(i/denominator)) * (1-(j/denominator)) + c0[num_points-1][1] * (i/denominator) * (1-(j/denominator)) + c1[0][1] * (1-(i/denominator)) * (j/denominator) + c1[num_points-1][1] * (i/denominator) * (j/denominator)
            z = c0[0][2] * (1-(i/denominator)) * (1-(j/denominator)) + c0[num_points-1][2] * (i/denominator) * (1-(j/denominator)) + c1[0][2] * (1-(i/denominator)) * (j/denominator) + c1[num_points-1][2] * (i/denominator) * (j/denominator)
            row.append([x, y, z])
        bilinear_interpolated_curve.append(row)
    return bilinear_interpolated_curve

def get_blended_patch(lc, ld, b):
    final_patch = []
    for i in range(num_points):
        row = []
        for j in range(num_points):
            x = lc[i][j][0] + ld[i][j][0] - b[i][j][0]
            y = lc[i][j][1] + ld[i][j][1] - b[i][j][1]
            z = lc[i][j][2] + ld[i][j][2] - b[i][j][2]
            row.append([x, y, z])
        final_patch.append(row)
    return final_patch

def combine_pts(pts):
    return_pts = []
    for row in pts:
        return_pts += row
    return return_pts

def get_faces(pts):
    faces = []
    for i in range(num_points + 1, num_points*num_points):
        if i % 1000 == 0:
            continue
        face = [i, i-1, i-num_points-1, i-num_points]
        faces.append(face)
    return faces

filename = "C:\\Users\\chara\\OneDrive\\Desktop\\CMPT732 G200 Lab\\Assignments\\Assignment 3\\Assignment 3 Part 2\\A3-2\\coons_patch_points.txt"
control_points = read_control_points(filename)

num_points = 100

c0 = control_points[:4]
c1 = control_points[4:8]
d0 = control_points[8:12]
d1 = control_points[12:]

c0 = get_bezier_curve_points(c0)
c1 = get_bezier_curve_points(c1)
d0 = get_bezier_curve_points(d0)
d1 = get_bezier_curve_points(d1)

# Generate linear interpolated points from the curves
lc = linear_interpolate(c0, c1)
ld = linear_interpolate(d0, d1)

# Generate bilinear interpolated curve from all 4 curves
b = bilinear_interpolate(c0, c1, d0, d1)

# Obtain the final patch
C = get_blended_patch(lc, ld, b)

faces = get_faces(combine_pts(C))

name = "Coons Patch"
mesh = bpy.data.meshes.new(name)
obj = bpy.data.objects.new(name, mesh)
scn = bpy.context.scene
scn.collection.objects.link(obj)
bpy.context.view_layer.objects.active = obj
mesh.from_pydata(combine_pts(C), [], faces[:1000])