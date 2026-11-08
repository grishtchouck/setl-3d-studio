import bpy, bmesh, os
from mathutils import Vector

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
    m = bpy.data.materials.new(name); m.use_nodes = True
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
 wall=mat('Wall', '#f1ede6', .9), ceil=mat('Ceiling', '#fbfaf6', .95), lam=mat('Laminate', '#c9a27a', .5),
 hall=mat('Floor_Hall', '#d9d4cb', .4), tb=mat('Tile_Bath', '#e7ecec', .3), tw=mat('Tile_Wall', '#e9eeee', .3),
 log=mat('Loggia_Floor', '#b9b2a6', .8), glass=mat('Glass', '#cfe3ef', .05, 0, .2), frame=mat('Frame', '#fbfaf7', .5),
 white=mat('White', '#f6f4ef', .45), steel=mat('Steel', '#c0c4c7', .25, .9), black=mat('Black', '#232323', .4),
 stone=mat('Stone', '#e8e3da', .3), oak=mat('Oak', '#c09a6b', .6), walnut=mat('Walnut', '#6b4a33', .55),
 linen=mat('Linen', '#efe9df', .95), grey=mat('Fabric_Grey', '#7d8f9c', .95), terra=mat('Terracotta', '#c47a5a', .95),
 door=mat('Door', '#efe9df', .55), dent=mat('Door_Entry', '#4a4744', .5), mirror=mat('Mirror', '#dfe7ea', .03, 1),
 green=mat('Plant', '#4f7a4a', .8), pot=mat('Pot', '#d8cfc0', .7), shade=mat('Lamp_Shade', '#efe6d6', .9),
 art=mat('Art', '#e2c08a', .8), dark=mat('Dark_Gap', '#3a3835', .8),
 kfront=mat('Kitchen_Front', '#9fb2a0', .5), sofa=mat('Sofa', '#5f7f9a', .95), curtain=mat('Curtain', '#d9cbb3', .95),
 tulle=mat('Tulle', '#ffffff', .9, 0, .45), wood=mat('Door_Wood', '#a9825a', .55), tv=mat('TV_Screen', '#151515', .15))

N = {}
def nm(p):
    N[p] = N.get(p, 0) + 1; return '%s_%02d' % (p, N[p])

def add(name, bm, m, c):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(m)
    o = bpy.data.objects.new(name, me); c.objects.link(o); return o

def box(name, x1, z1, x2, z2, y0, h, m, c=None):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    sx, sz = max(abs(x2 - x1), 1e-3), max(abs(z2 - z1), 1e-3)
    for v in bm.verts:
        v.co = Vector((v.co.x * sx + (x1 + x2) / 2, -(v.co.y * sz + (z1 + z2) / 2), v.co.z * h + y0 + h / 2))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return add(nm(name), bm, m, c or CB)

def cyl(name, x, z, y0, h, r, m, c=None, seg=28, r2=None):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg, radius1=r, radius2=(r if r2 is None else r2), depth=h)
    for v in bm.verts: v.co += Vector((x, -z, y0 + h / 2))
    return add(nm(name), bm, m, c or CB)

def ball(name, x, y, z, r, m, c=None):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=2, radius=r)
    for v in bm.verts: v.co += Vector((x, -z, y))
    return add(nm(name), bm, m, c or CB)

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
    fw = 0.05
    if axis == 'x':
        box('B_Glass', s, c - 0.01, e, c + 0.01, bot, top - bot, M['glass'])
        for (a, b, y0, h) in [(s, e, bot, fw), (s, e, top - fw, fw), (s, s + fw, bot, top - bot), (e - fw, e, bot, top - bot), ((s + e) / 2 - .025, (s + e) / 2 + .025, bot, top - bot)]:
            box('B_Frame', a, c - .04, b, c + .04, y0, h, M['frame'])
        box('B_Sill', s - .05, c + t / 2 - .02, e + .05, c + t / 2 + .2, bot - .03, .03, M['white'])
    else:
        box('B_Glass', c - 0.01, s, c + 0.01, e, bot, top - bot, M['glass'])
        for (a, b, y0, h) in [(s, e, bot, fw), (s, e, top - fw, fw), (s, s + fw, bot, top - bot), (e - fw, e, bot, top - bot), ((s + e) / 2 - .025, (s + e) / 2 + .025, bot, top - bot)]:
            box('B_Frame', c - .04, a, c + .04, b, y0, h, M['frame'])
        box('B_Sill', c - t / 2 - .2, s - .05, c - t / 2 + .02, e + .05, bot - .03, .03, M['white'])

# ---------- floors / ceiling
box('B_Floor_Living', 2.27, 0, 6.52, 3.48, -.02, .02, M['lam'])
box('B_Floor_Living', 1.83, 1.73, 2.27, 3.48, -.02, .02, M['lam'])
box('B_Floor_Hall', 0, 1.78, 1.83, 3.48, -.02, .02, M['hall'])
box('B_Floor_Bath', 0, 0, 2.27, 1.73, -.02, .02, M['tb'])
box('B_Floor_Loggia', 6.82, 0, 8.12, 3.48, -.04, .02, M['log'])
box('B_Ceiling', -.2, -.3, 8.17, 3.63, H, .05, M['ceil'])

# ---------- walls
wall('x', -.15, -.2, 8.17, .3, [(4.91, 5.78, .85, 2.45)])
wall('z', -.1, -.3, 3.63, .2, [(1.95, 2.85, 0, 2.1)])
wall('x', 3.555, -.2, 8.17, .15, [])
wall('z', 6.67, 0, 3.48, .3, [(.71, 1.49, 0, 2.2), (1.49, 2.39, .85, 2.2)])
wall('x', 1.73, 0, 2.27, .1, [(.68, 1.34, 0, 2.1)])
wall('z', 2.235, 0, 1.68, .07, [])
wall('z', 1.83, 1.78, 3.48, .1, [(1.99, 2.83, 0, 2.1)])
box('B_Shaft', 1.65, 0, 2.2, .3, 0, H, M['wall'])
# loggia outer glazing
box('B_Parapet', 8.07, 0, 8.17, 3.48, 0, 1.0, M['wall'])
box('B_Glass', 8.11, 0, 8.13, 3.48, 1.0, 1.6, M['glass'])
box('B_Frame', 8.08, 0, 8.16, 3.48, 2.6, .1, M['frame'])
for zz in [0, .87, 1.74, 2.61, 3.43]:
    box('B_Frame', 8.08, zz, 8.16, zz + .05, 1.0, 1.6, M['frame'])

# ---------- windows, doors
window('x', -.15, 4.91, 5.78, .85, 2.45, .3)
window('z', 6.67, 1.49, 2.39, .85, 2.2, .3)
box('B_Glass', 6.66, .76, 6.68, 1.44, .1, 2.0, M['glass'])
for (a, b, y0, h) in [(.71, 1.49, 0, .1), (.71, 1.49, 2.1, .1), (.71, .76, 0, 2.2), (1.44, 1.49, 0, 2.2)]:
    box('B_Frame', 6.63, a, 6.71, b, y0, h, M['frame'])
box('B_Radiator', 4.98, .03, 5.72, .1, .15, .5, M['white'])
box('B_Door_Entry', -.13, 1.95, -.07, 2.85, 0, 2.05, M['dent'])
box('B_Door_Handle', -.07, 2.72, -.04, 2.77, 1.0, .03, M['steel'])
box('B_Door', .68, 1.71, 1.34, 1.75, 0, 2.05, M['wood'])
box('B_Door', 1.81, 1.99, 1.85, 2.83, 0, 2.05, M['wood'])

# ---------- bathroom fixtures (base)
box('B_Shower_Tray', .02, .02, .9, .9, 0, .06, M['white'])
box('B_Shower_Glass', .9, .02, .915, .9, .06, 1.94, M['glass'])
box('B_Shower_Glass', .02, .9, .9, .915, .06, 1.94, M['glass'])
cyl('B_Shower_Head', .2, .2, 2.0, .02, .1, M['steel'])
cyl('B_Shower_Pipe', .06, .06, 1.0, 1.05, .012, M['steel'], seg=8)
box('B_Tile_Wall', 0, 0, 1.65, .01, 0, 2.1, M['tw'])
box('B_Tile_Wall', 0, 0, .01, 1.68, 0, 2.1, M['tw'])
box('B_Tile_Wall', 2.19, .3, 2.2, 1.68, 0, 2.1, M['tw'])
box('B_Toilet_Tank', 1.02, .01, 1.4, .2, .4, .4, M['white'])
cyl('B_Toilet_Bowl', 1.21, .45, 0, .4, .17, M['white'], r2=.19)
cyl('B_Toilet_Seat', 1.21, .45, .4, .03, .2, M['white'])
box('B_Vanity', .01, 1.08, .47, 1.62, .25, .55, M['oak'])
box('B_Vanity_Top', .01, 1.06, .5, 1.64, .8, .04, M['stone'])
cyl('B_Basin', .26, 1.35, .84, .12, .17, M['white'], r2=.19)
cyl('B_Faucet', .06, 1.35, .84, .22, .012, M['steel'], seg=8)
box('B_Mirror', .01, 1.1, .025, 1.6, 1.05, .8, M['mirror'])

# ---------- furniture collection
F = CF
def fb(*a): return box(*a[:8], c=F)
def chair(x, z, back):
    fb('F_Chair', x - .21, z - .21, x + .21, z + .21, .44, .04, M['oak'])
    bz = z + .19 if back > 0 else z - .21
    fb('F_Chair', x - .21, bz, x + .21, bz + .02, .48, .4, M['oak'])
    for dx in (-.19, .17):
        for dz in (-.19, .17):
            fb('F_Chair', x + dx, z + dz, x + dx + .02, z + dz + .02, 0, .44, M['walnut'])
def plant(x, z, pr, ph, s):
    cyl('F_Pot', x, z, 0, ph, pr, M['pot'], c=F, r2=pr * 1.15)
    for i, (dx, dy, dz, r) in enumerate([(0, .55, 0, .22), (.08, .8, .05, .18), (-.07, .7, -.06, .17), (.03, 1.0, -.02, .13)]):
        ball('F_Leaf', x + dx * s, ph + dy * s, z + dz * s, r * s, M['green'], c=F)

# kitchen
# ---- package: kitchen
fb('F_Kitchen_Base', 2.27, .02, 2.87, 1.71, .1, .76, M['kfront'])
fb('F_Kitchen_Plinth', 2.27, .05, 2.84, 1.71, 0, .1, M['black'])
fb('F_Kitchen_Top', 2.27, .02, 2.9, 1.71, .86, .04, M['oak'])
for zz in [.6, 1.13]:
    fb('F_Kitchen_Gap', 2.87, zz, 2.875, zz + .005, .12, .72, M['dark'])
fb('F_Sink', 2.4, .12, 2.8, .58, .88, .025, M['steel'])
cyl('F_Faucet', 2.32, .35, .9, .28, .012, M['steel'], c=F, seg=8)
fb('F_Cooktop', 2.34, 1.15, 2.84, 1.65, .9, .006, M['black'])
fb('F_Kitchen_Upper', 2.27, .02, 2.6, 1.1, 1.45, .75, M['kfront'])
fb('F_Hood', 2.27, 1.15, 2.75, 1.65, 1.55, .12, M['steel'])
fb('F_Hood', 2.27, 1.3, 2.45, 1.5, 1.67, .53, M['steel'])
fb('F_Fridge', 1.9, 2.88, 2.5, 3.45, 0, 1.85, M['white'])
fb('F_Fridge_Handle', 2.5, 2.95, 2.52, 2.98, .9, .6, M['steel'])
# dining
cyl('F_Table', 3.05, 2.65, .72, .03, .4, M['white'], c=F, seg=40)
cyl('F_Table', 3.05, 2.65, 0, .72, .035, M['walnut'], c=F, seg=12)
cyl('F_Table', 3.05, 2.65, 0, .02, .22, M['walnut'], c=F)
chair(3.05, 2.05, -1); chair(3.05, 3.2, 1)
# wardrobe
fb('F_Wardrobe', 3.62, .02, 4.82, .62, 0, 2.35, M['oak'])
fb('F_Wardrobe_Gap', 4.215, .62, 4.225, .625, .05, 2.25, M['dark'])
# sofa (faces TV, +z)
fb('F_Sofa', 4.2, 1.55, 6.2, 2.5, .1, .32, M['sofa'])
fb('F_Sofa', 4.2, 1.55, 6.2, 1.8, .42, .42, M['sofa'])
fb('F_Sofa', 4.2, 1.55, 4.42, 2.5, .42, .2, M['sofa'])
fb('F_Sofa', 5.98, 1.55, 6.2, 2.5, .42, .2, M['sofa'])
fb('F_Sofa_Leg', 4.25, 1.6, 6.15, 2.45, 0, .1, M['black'])
# tv unit + tv
fb('F_TV_Unit', 4.6, 3.05, 5.8, 3.46, 0, .5, M['walnut'])
fb('F_TV', 4.65, 3.4, 5.75, 3.44, .85, .63, M['black'])
fb('F_TV_Screen', 4.68, 3.395, 5.72, 3.4, .88, .57, M['tv'])
# hall hook panel
fb('F_Hooks', .2, 3.44, 1.3, 3.47, 1.55, .2, M['oak'])
for hx in (.35, .6, .85, 1.1):
    cyl('F_Hook', hx, 3.41, 1.6, .06, .015, M['black'], c=F, seg=8)
# textiles: rods, curtains, tulle
fb('F_Rod', 4.83, .08, 6.1, .11, 2.5, .025, M['steel'])
fb('F_Curtain', 4.83, .1, 4.97, .2, .05, 2.43, M['curtain'])
fb('F_Curtain', 5.72, .1, 6.05, .2, .05, 2.43, M['curtain'])
fb('F_Tulle', 4.88, .2, 5.82, .21, .05, 2.43, M['tulle'])
fb('F_Rod', 6.42, .45, 6.45, 2.65, 2.5, .025, M['steel'])
fb('F_Curtain', 6.3, .45, 6.42, .7, .05, 2.43, M['curtain'])
fb('F_Curtain', 6.3, 2.4, 6.42, 2.65, .05, 2.43, M['curtain'])
fb('F_Tulle', 6.28, .7, 6.29, 2.4, .05, 2.43, M['tulle'])

sun = bpy.data.lights.new('Sun', 'SUN'); sun.energy = 3.0
so = bpy.data.objects.new('Sun', sun); scene.collection.objects.link(so)
so.rotation_euler = (0.9, 0.2, 2.6)
cam = bpy.data.cameras.new('Cam'); co = bpy.data.objects.new('Cam', cam); scene.collection.objects.link(co)
scene.camera = co

out = os.path.expanduser('~/Desktop/setl-studio'); os.makedirs(out, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out, 'studio.blend'))
bpy.ops.export_scene.gltf(filepath=os.path.join(out, 'studio.glb'), export_format='GLB', export_apply=True,
                          export_yup=True, export_cameras=False, export_lights=False)
result = {'objects': len(bpy.data.objects), 'base': len(CB.objects), 'furniture': len(CF.objects),
          'glb': os.path.join(out, 'studio.glb'), 'size': os.path.getsize(os.path.join(out, 'studio.glb'))}
