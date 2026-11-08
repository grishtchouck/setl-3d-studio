import bpy, bmesh, os, math
from mathutils import Vector

# Студия 21,39 м². Координаты плана: x вправо, z вниз (к нижней стене), y вверх. Метры.
H = 2.7
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
for c in list(bpy.data.collections): bpy.data.collections.remove(c)
for m in list(bpy.data.meshes): bpy.data.meshes.remove(m)
for m in list(bpy.data.materials): bpy.data.materials.remove(m)
scene = bpy.context.scene

def coll(n):
    c = bpy.data.collections.new(n); scene.collection.children.link(c); return c
CB = coll('Base'); CF = coll('Furniture')

def lin(c): return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
MATS = {}
def mat(name, hexc, rough=0.7, metal=0.0, alpha=1.0):
    if name in MATS: return MATS[name]
    m = bpy.data.materials.new(name)
    try: m.use_nodes = True
    except Exception: pass
    b = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    r, g, bb = [int(hexc[i:i+2], 16) / 255 for i in (1, 3, 5)]
    b.inputs['Base Color'].default_value = (lin(r), lin(g), lin(bb), 1)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    if alpha < 1:
        b.inputs['Alpha'].default_value = alpha
        try: m.surface_render_method = 'BLENDED'
        except Exception: pass
    MATS[name] = m; return m

M = dict(
 wall=mat('Wall', '#f3efe8', .9), lam=mat('Laminate', '#c9a27a', .5),
 hall=mat('Floor_Hall', '#d9d4cb', .4), tb=mat('Tile_Bath', '#e7ecec', .3), tw=mat('Tile_Wall', '#e9eeee', .25),
 log=mat('Loggia_Floor', '#b9b2a6', .8), glass=mat('Glass', '#cfe3ef', .05, 0, .2), frame=mat('Frame', '#fbfaf7', .45),
 white=mat('White', '#f7f5f1', .35), porc=mat('Porcelain', '#fbfbfa', .12), chrome=mat('Chrome', '#e6e8ea', .12, 1.0),
 steel=mat('Steel', '#c9cdd0', .3, .9), black=mat('Black', '#1e1e1e', .4), glossb=mat('Black_Glass', '#0e0e0f', .08),
 stone=mat('Stone', '#e4ded3', .25), oak=mat('Oak', '#c69c6d', .55), oakl=mat('Oak_Light', '#d8b98f', .55),
 walnut=mat('Walnut', '#6b4a33', .5), dent=mat('Door_Entry', '#3d3a37', .45), mirror=mat('Mirror', '#dfe7ea', .03, 1),
 dark=mat('Dark_Gap', '#3a3835', .8), kfront=mat('Kitchen_Front', '#97ab98', .45), carc=mat('Carcass', '#efece6', .5),
 sofa=mat('Sofa', '#56748f', .95), sofad=mat('Sofa_Base', '#47627a', .95), pil1=mat('Pillow', '#d98b67', .95),
 pil2=mat('Pillow_Sand', '#e3cfa8', .95), throw=mat('Throw', '#efe7da', .95), chairf=mat('Chair_Seat', '#c9a97f', .9),
 curtain=mat('Curtain', '#d8c8ad', .95), tulle=mat('Tulle', '#ffffff', .9, 0, .5), wood=mat('Door_Wood', '#b48c62', .5),
 tv=mat('TV_Screen', '#141518', .1), brass=mat('Brass', '#b8935a', .3, .9), led=mat('LED', '#fff1d6', .5),
 base=mat('Baseboard', '#f7f5f1', .4), conc=mat('Shaft', '#ece8e1', .9))

N = {}
def nm(p):
    N[p] = N.get(p, 0) + 1; return '%s_%02d' % (p, N[p])

def add(name, bm, m, c):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(m)
    o = bpy.data.objects.new(name, me); c.objects.link(o); return o

def bev(bm, r, seg):
    if r <= 0: return
    try:
        bmesh.ops.bevel(bm, geom=list(bm.edges), offset=r, offset_type='OFFSET', segments=seg, profile=0.5,
                        affect='EDGES', clamp_overlap=True)
    except TypeError:
        bmesh.ops.bevel(bm, geom=list(bm.edges), offset=r, segments=seg, profile=0.5, affect='EDGES', clamp_overlap=True)

def box(name, x1, z1, x2, z2, y0, h, m, c=None, r=0.0, seg=2, smooth=False):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    sx, sz = max(abs(x2 - x1), 1e-3), max(abs(z2 - z1), 1e-3)
    for v in bm.verts:
        v.co = Vector((v.co.x * sx + (x1 + x2) / 2, -(v.co.y * sz + (z1 + z2) / 2), v.co.z * h + y0 + h / 2))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    rr = min(r, sx / 2 - 1e-3, sz / 2 - 1e-3, h / 2 - 1e-3)
    if rr > 0: bev(bm, rr, seg)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if smooth:
        for f in bm.faces: f.smooth = True
    return add(nm(name), bm, m, c or CB)

def cyl(name, x, z, y0, h, r, m, c=None, seg=32, r2=None, smooth=True):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg, radius1=r, radius2=(r if r2 is None else r2), depth=h)
    for v in bm.verts: v.co += Vector((x, -z, y0 + h / 2))
    if smooth:
        for f in bm.faces:
            if len(f.verts) == 4: f.smooth = True
    return add(nm(name), bm, m, c or CB)

def hbar(name, axis, a, b, z_or_x, y, r, m, c=None):
    # горизонтальная трубка вдоль оси axis ('x' или 'z')
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=12, radius1=r, radius2=r, depth=abs(b - a))
    rot = 'Y' if axis == 'x' else 'X'
    import mathutils
    bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=mathutils.Matrix.Rotation(math.radians(90), 3, rot))
    mid = (a + b) / 2
    off = Vector((mid, -z_or_x, y)) if axis == 'x' else Vector((z_or_x, -mid, y))
    for v in bm.verts: v.co += off
    for f in bm.faces:
        if len(f.verts) == 4: f.smooth = True
    return add(nm(name), bm, m, c or CB)

def wave(name, axis, c0, a, b, y0, h, amp, waves, m, cl):
    # волнистая ткань: плоскость, изогнутая синусом
    bm = bmesh.new(); n = max(8, int(waves * 10)); rows = []
    for i in range(n + 1):
        t = i / n; p = a + (b - a) * t; d = amp * math.sin(2 * math.pi * waves * t)
        if axis == 'x':
            v1 = bm.verts.new((p, -(c0 + d), y0)); v2 = bm.verts.new((p, -(c0 + d), y0 + h))
        else:
            v1 = bm.verts.new((c0 + d, -p, y0)); v2 = bm.verts.new((c0 + d, -p, y0 + h))
        rows.append((v1, v2))
    for i in range(n):
        f = bm.faces.new((rows[i][0], rows[i + 1][0], rows[i + 1][1], rows[i][1])); f.smooth = True
    bm.normal_update()
    return add(nm(name), bm, m, cl)

def wall(axis, c, a1, a2, t, opens):
    opens = sorted(opens)
    def seg(a, b, y0, y1):
        if b - a < 1e-3 or y1 - y0 < 1e-3: return
        if axis == 'x': box('B_Wall', a, c - t / 2, b, c + t / 2, y0, y1 - y0, M['wall'])
        else: box('B_Wall', c - t / 2, a, c + t / 2, b, y0, y1 - y0, M['wall'])
    cur = a1
    for s, e, bot, top in opens:
        seg(cur, s, 0, H); seg(s, e, 0, bot); seg(s, e, top, H); cur = e
    seg(cur, a2, 0, H)

def window(axis, c, s, e, bot, top, t):
    fw = 0.06
    if axis == 'x':
        box('B_Glass', s, c - 0.01, e, c + 0.01, bot, top - bot, M['glass'])
        for (a, b, y0, h) in [(s, e, bot, fw), (s, e, top - fw, fw), (s, s + fw, bot, top - bot), (e - fw, e, bot, top - bot), ((s + e) / 2 - .03, (s + e) / 2 + .03, bot, top - bot)]:
            box('B_Frame', a, c - .045, b, c + .045, y0, h, M['frame'], r=.006)
        box('B_Sill', s - .06, c + t / 2 - .02, e + .06, c + t / 2 + .22, bot - .035, .035, M['white'], r=.008)
    else:
        box('B_Glass', c - 0.01, s, c + 0.01, e, bot, top - bot, M['glass'])
        for (a, b, y0, h) in [(s, e, bot, fw), (s, e, top - fw, fw), (s, s + fw, bot, top - bot), (e - fw, e, bot, top - bot), ((s + e) / 2 - .03, (s + e) / 2 + .03, bot, top - bot)]:
            box('B_Frame', c - .045, a, c + .045, b, y0, h, M['frame'], r=.006)
        box('B_Sill', c - t / 2 - .22, s - .06, c - t / 2 + .02, e + .06, bot - .035, .035, M['white'], r=.008)

# ---------- полы
box('B_Floor_Living', 2.27, 0, 6.52, 3.48, -.02, .02, M['lam'])
box('B_Floor_Living', 1.83, 1.73, 2.27, 3.48, -.02, .02, M['lam'])
box('B_Floor_Hall', 0, 1.78, 1.83, 3.48, -.02, .02, M['hall'])
box('B_Floor_Bath', 0, 0, 2.27, 1.73, -.02, .02, M['tb'])
box('B_Floor_Loggia', 6.82, 0, 8.12, 3.48, -.04, .02, M['log'])

# ---------- стены
wall('x', -.15, -.2, 8.17, .3, [(4.91, 5.78, .85, 2.45)])
wall('z', -.1, -.3, 3.63, .2, [(1.95, 2.85, 0, 2.1)])
wall('x', 3.555, -.2, 8.17, .15, [])
wall('z', 6.67, 0, 3.48, .3, [(.71, 1.49, 0, 2.2), (1.49, 2.39, .85, 2.2)])
wall('x', 1.73, 0, 2.27, .1, [(.68, 1.34, 0, 2.1)])
wall('z', 2.235, 0, 1.68, .07, [])
wall('z', 1.83, 1.78, 3.48, .1, [(1.99, 2.83, 0, 2.1)])
box('B_Shaft', 1.65, 0, 2.2, .3, 0, H, M['wall'])
box('B_Parapet', 8.07, 0, 8.17, 3.48, 0, 1.0, M['wall'])
box('B_Glass', 8.11, 0, 8.13, 3.48, 1.0, 1.6, M['glass'])
box('B_Frame', 8.08, 0, 8.16, 3.48, 2.6, .1, M['frame'])
box('B_Frame', 8.07, 0, 8.17, 3.48, 1.0, .05, M['frame'])
for zz in [0, .87, 1.74, 2.61, 3.43]:
    box('B_Frame', 8.08, zz, 8.16, zz + .05, 1.0, 1.6, M['frame'])

# ---------- окна, двери
window('x', -.15, 4.91, 5.78, .85, 2.45, .3)
window('z', 6.67, 1.49, 2.39, .85, 2.2, .3)
box('B_Glass', 6.66, .77, 6.68, 1.43, .12, 1.96, M['glass'])
for (a, b, y0, h) in [(.71, 1.49, 0, .12), (.71, 1.49, 2.08, .12), (.71, .77, 0, 2.2), (1.43, 1.49, 0, 2.2)]:
    box('B_Frame', 6.62, a, 6.72, b, y0, h, M['frame'], r=.006)
box('B_Door_Handle', 6.5, 1.36, 6.53, 1.39, 1.0, .12, M['chrome'], r=.005)
for i in range(8):
    x = 5.0 + i * .09
    box('B_Radiator', x, .04, x + .065, .11, .16, .5, M['white'], r=.012)
box('B_Door_Entry', -.14, 1.97, -.04, 2.83, 0, 2.06, M['dent'], r=.01)
box('B_Door_Handle', -.04, 2.64, .0, 2.78, 1.0, .025, M['chrome'], r=.008)
for (a, b, y0, h) in [(1.91, 1.97, 0, 2.12), (2.83, 2.89, 0, 2.12), (1.91, 2.89, 2.06, .06)]:
    box('B_Casing', .0, a, .015, b, y0, h, M['white'], r=.004)
box('B_Door', .68, 1.71, 1.34, 1.75, 0, 2.05, M['wood'], r=.006)
box('B_Door_Handle', 1.22, 1.75, 1.3, 1.77, 1.0, .02, M['chrome'], r=.006)
# открытая дверь кухня-гостиная (распахнута в кухню)
box('B_DoorOpen', 1.88, 2.79, 2.7, 2.83, 0, 2.05, M['wood'], r=.006)
for side in (1.77, 1.88):
    for (a, b, y0, h) in [(1.93, 1.99, 0, 2.12), (2.83, 2.89, 0, 2.12), (1.93, 2.89, 2.06, .06)]:
        box('B_Casing', side, a, side + .012, b, y0, h, M['white'], r=.004)
for side in (1.66, 1.78):
    for (a, b, y0, h) in [(.62, .68, 0, 2.12), (1.34, 1.40, 0, 2.12), (.62, 1.40, 2.06, .06)]:
        box('B_Casing', a, side, b, side + .012, y0, h, M['white'], r=.004)
# плинтусы
BB = [('x', .012, 2.27, 6.52), ('z', 6.508, 0, .71), ('z', 6.508, 1.49, 3.48), ('x', 3.468, 1.88, 6.52),
      ('x', 3.468, 0, 1.78), ('z', .012, 1.78, 1.95), ('z', .012, 2.85, 3.48), ('z', 1.766, 1.78, 1.99),
      ('z', 1.766, 2.83, 3.48), ('x', 1.792, 0, .68), ('x', 1.792, 1.34, 1.78)]
for ax, c, a, b in BB:
    if ax == 'x': box('B_Baseboard', a, c - .008, b, c + .008, 0, .07, M['base'], r=.003)
    else: box('B_Baseboard', c - .008, a, c + .008, b, 0, .07, M['base'], r=.003)

# ---------- санузел (база)
box('B_Shower_Tray', .02, .02, .9, .9, 0, .06, M['porc'], r=.015)
box('B_Shower_Glass', .9, .02, .91, .9, .06, 1.94, M['glass'])
box('B_Shower_Glass', .02, .9, .9, .91, .06, 1.94, M['glass'])
box('B_Shower_Frame', .895, .02, .915, .9, 1.99, .015, M['chrome'])
box('B_Shower_Frame', .02, .895, .9, .915, 1.99, .015, M['chrome'])
cyl('B_Shower_Head', .22, .22, 2.0, .015, .12, M['chrome'])
cyl('B_Shower_Pipe', .05, .05, 1.0, 1.05, .012, M['chrome'], seg=10)
box('B_Shower_Mixer', .01, .3, .05, .45, 1.0, .08, M['chrome'], r=.01)
box('B_Tile_Wall', 0, 0, 1.65, .01, 0, 2.1, M['tw'])
box('B_Tile_Wall', 0, 0, .01, 1.68, 0, 2.1, M['tw'])
box('B_Tile_Wall', 2.19, .3, 2.2, 1.68, 0, 2.1, M['tw'])
box('B_Toilet_Tank', 1.03, .01, 1.39, .19, .42, .4, M['porc'], r=.03, seg=3, smooth=True)
cyl('B_Toilet_Bowl', 1.21, .45, 0, .4, .16, M['porc'], r2=.19)
cyl('B_Toilet_Seat', 1.21, .45, .4, .035, .2, M['porc'])
box('B_Vanity', .01, 1.08, .47, 1.62, .3, .5, M['oak'], r=.01)
box('B_Vanity_Top', .01, 1.06, .5, 1.64, .8, .04, M['porc'], r=.01)
cyl('B_Basin', .26, 1.35, .82, .02, .17, M['dark'])
cyl('B_Faucet', .06, 1.35, .84, .2, .012, M['chrome'], seg=10)
hbar('B_Faucet', 'x', .06, .16, 1.35, 1.03, .01, M['chrome'])
box('B_Mirror', .01, 1.1, .025, 1.6, 1.05, .8, M['mirror'])
box('B_Mirror_Frame', .005, 1.09, .02, 1.61, 1.04, .82, M['black'])
for zz in (.48, .92):
    cyl('B_Towel', 2.16, zz, .8, .8, .012, M['chrome'], seg=10)
for yy in (.85, 1.0, 1.15, 1.3, 1.45):
    hbar('B_Towel', 'z', .48, .92, 2.16, yy, .01, M['chrome'])

# ---------- пакет меблировки
F = CF
def fb(name, x1, z1, x2, z2, y0, h, m, r=0.0, seg=2, smooth=False):
    return box(name, x1, z1, x2, z2, y0, h, m, c=F, r=r, seg=seg, smooth=smooth)

def chair(x, z, face):
    # face: +1 — сидящий смотрит в +z, -1 — в -z
    fb('F_Chair', x - .22, z - .21, x + .22, z + .21, .44, .05, M['chairf'], r=.02, seg=3, smooth=True)
    bz = z - .21 if face > 0 else z + .18
    fb('F_Chair', x - .21, bz, x + .21, bz + .03, .5, .36, M['oak'], r=.012)
    for dx in (-.17, .17):
        for dz in (-.16, .16):
            cyl('F_Chair', x + dx, z + dz, 0, .44, .016, M['oak'], c=F, seg=10, r2=.012)

# кухонный гарнитур
fb('F_Kitchen_Base', 2.27, .02, 2.865, 1.71, .1, .76, M['carc'])
fb('F_Kitchen_Plinth', 2.27, .05, 2.82, 1.71, 0, .1, M['black'])
for (s, e) in [(.02, .62), (.62, 1.12), (1.12, 1.71)]:
    fb('F_Kitchen_Front', 2.865, s + .003, 2.885, e - .003, .12, .72, M['kfront'], r=.004)
    fb('F_Kitchen_Handle', 2.885, (s + e) / 2 - .13, 2.9, (s + e) / 2 + .13, .78, .018, M['brass'], r=.005)
fb('F_Kitchen_Top', 2.27, .02, 2.905, 1.71, .86, .04, M['oak'], r=.006)
fb('F_Kitchen_Back', 2.27, .02, 2.282, 1.71, .9, .55, M['stone'])
fb('F_Sink', 2.42, .12, 2.8, .58, .9, .006, M['steel'], r=.01)
fb('F_Sink', 2.46, .16, 2.76, .54, .885, .02, M['dark'])
cyl('F_Faucet', 2.33, .35, .9, .3, .014, M['chrome'], c=F, seg=12)
hbar('F_Faucet', 'x', 2.33, 2.52, .35, 1.19, .011, M['chrome'], c=F)
fb('F_Cooktop', 2.33, 1.15, 2.855, 1.66, .9, .007, M['glossb'], r=.006)
for (bx, bz, br) in [(2.47, 1.28, .085), (2.47, 1.53, .065), (2.72, 1.28, .065), (2.72, 1.53, .085)]:
    cyl('F_Cooktop', bx, bz, .906, .002, br, M['dark'], c=F, seg=28)
fb('F_Kitchen_Upper', 2.27, .02, 2.6, 1.1, 1.45, .75, M['carc'])
for (s, e) in [(.02, .56), (.56, 1.1)]:
    fb('F_Kitchen_Front', 2.6, s + .003, 2.615, e - .003, 1.452, .746, M['kfront'], r=.004)
fb('F_Kitchen_LED', 2.4, .06, 2.43, 1.06, 1.44, .008, M['led'])
fb('F_Hood', 2.27, 1.15, 2.74, 1.66, 1.6, .08, M['steel'], r=.008)
fb('F_Hood', 2.27, 1.3, 2.46, 1.51, 1.68, .62, M['steel'], r=.006)
# холодильник
fb('F_Fridge', 1.9, 2.9, 2.5, 3.46, 0, 1.86, M['white'], r=.02)
fb('F_Fridge', 1.91, 2.885, 2.49, 2.9, 1.17, .002, M['dark'])
for (y0, h) in [(.25, .7), (1.3, .45)]:
    fb('F_Fridge_Handle', 2.42, 2.865, 2.44, 2.885, y0, h, M['steel'], r=.006)
# обеденная группа
cyl('F_Table', 3.05, 2.65, .71, .035, .42, M['oakl'], c=F, seg=48)
cyl('F_Table', 3.05, 2.65, .02, .69, .04, M['black'], c=F, seg=12)
cyl('F_Table', 3.05, 2.65, 0, .025, .24, M['black'], c=F, seg=32)
chair(3.05, 2.05, 1); chair(3.05, 3.25, -1)
# шкаф
fb('F_Wardrobe', 3.62, .02, 4.82, .6, .06, 2.29, M['carc'])
fb('F_Wardrobe', 3.63, .03, 4.81, .58, 0, .06, M['black'])
for i in range(3):
    s = 3.62 + i * .4
    fb('F_Wardrobe_Front', s + .003, .6, s + .397, .62, .07, 2.27, M['oakl'], r=.004)
    hx = s + .37 if i < 2 else s + .03
    fb('F_Wardrobe_Handle', hx - .01, .62, hx + .01, .635, .85, .5, M['black'], r=.005)
# диван (смотрит на ТВ, в +z)
for (lx, lz) in [(4.28, 1.62), (6.12, 1.62), (4.28, 2.42), (6.12, 2.42)]:
    cyl('F_Sofa_Leg', lx, lz, 0, .1, .022, M['walnut'], c=F, seg=10, r2=.016)
fb('F_Sofa', 4.22, 1.57, 6.18, 2.48, .1, .2, M['sofad'], r=.03, seg=2)
for (a, b) in [(4.42, 5.2), (5.2, 5.98)]:
    fb('F_Sofa', a + .005, 1.82, b - .005, 2.47, .3, .16, M['sofa'], r=.05, seg=3, smooth=True)
    fb('F_Sofa', a + .005, 1.58, b - .005, 1.84, .3, .52, M['sofa'], r=.06, seg=3, smooth=True)
fb('F_Sofa', 4.2, 1.55, 4.43, 2.5, .1, .52, M['sofa'], r=.06, seg=3, smooth=True)
fb('F_Sofa', 5.97, 1.55, 6.2, 2.5, .1, .52, M['sofa'], r=.06, seg=3, smooth=True)
fb('F_Sofa_Pillow', 4.5, 1.83, 4.92, 1.98, .44, .38, M['pil1'], r=.07, seg=3, smooth=True)
fb('F_Sofa_Pillow', 5.55, 1.83, 5.95, 1.98, .44, .36, M['pil2'], r=.07, seg=3, smooth=True)
fb('F_Sofa_Throw', 5.65, 1.85, 6.22, 2.35, .6, .035, M['throw'], r=.015, seg=2, smooth=True)
# тумба под ТВ и телевизор
fb('F_TV_Unit', 4.6, 3.06, 5.8, 3.46, .1, .42, M['walnut'], r=.01)
for i in range(3):
    s = 4.6 + i * .4
    fb('F_TV_Unit', s + .004, 3.045, s + .396, 3.06, .12, .38, M['walnut'], r=.004)
    fb('F_TV_Unit', s + .17, 3.035, s + .23, 3.045, .44, .015, M['brass'], r=.004)
for (lx, lz) in [(4.66, 3.12), (5.74, 3.12), (4.66, 3.4), (5.74, 3.4)]:
    cyl('F_TV_Unit', lx, lz, 0, .1, .015, M['black'], c=F, seg=8)
fb('F_TV', 4.62, 3.435, 5.78, 3.465, .82, .66, M['black'], r=.006)
fb('F_TV_Screen', 4.64, 3.43, 5.76, 3.436, .84, .62, M['tv'])
# панель с крючками
fb('F_Hooks', .2, 3.445, 1.3, 3.47, 1.55, .2, M['oak'], r=.008)
for hx in (.33, .54, .75, .96, 1.17):
    fb('F_Hook', hx - .01, 3.39, hx + .01, 3.445, 1.62, .02, M['brass'], r=.006)
    fb('F_Hook', hx - .01, 3.39, hx + .01, 3.41, 1.62, .06, M['brass'], r=.006)
# текстиль: карнизы, шторы, тюль
hbar('F_Rod', 'x', 4.84, 6.0, .1, 2.5, .012, M['black'], c=F)
wave('F_Curtain', 'x', .14, 4.84, 5.02, .03, 2.45, .025, 2.5, M['curtain'], F)
wave('F_Curtain', 'x', .14, 5.68, 5.96, .03, 2.45, .025, 3, M['curtain'], F)
wave('F_Tulle', 'x', .2, 4.86, 5.84, .03, 2.45, .015, 7, M['tulle'], F)
hbar('F_Rod', 'z', .45, 2.66, 6.44, 2.5, .012, M['black'], c=F)
wave('F_Curtain', 'z', 6.42, .48, .72, .03, 2.45, .025, 2.5, M['curtain'], F)
wave('F_Curtain', 'z', 6.42, 2.38, 2.63, .03, 2.45, .025, 2.5, M['curtain'], F)
wave('F_Tulle', 'z', 6.36, .72, 2.38, .03, 2.45, .015, 10, M['tulle'], F)

out = os.path.expanduser('~/Desktop/setl-studio'); os.makedirs(out, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out, 'studio.blend'))
bpy.ops.export_scene.gltf(filepath=os.path.join(out, 'studio.glb'), export_format='GLB', export_apply=True,
                          export_yup=True, export_cameras=False, export_lights=False)
result = {'objects': len(bpy.data.objects), 'base': len(CB.objects), 'furniture': len(CF.objects),
          'size': os.path.getsize(os.path.join(out, 'studio.glb'))}
