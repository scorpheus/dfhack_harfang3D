__author__ = 'scorpheus'

import gs

mat = gs.Matrix4()

mat.SetRow(0, gs.Vector4(0.697289764881134, 0.0, 0.716785192489624, 0))
mat.SetRow(1, gs.Vector4(-0.692947268486023, 0.2557440400123596, 0.6741002202033997, 0))
mat.SetRow(2, gs.Vector4(-0.1833142638206482, -0.9667413830757141, 0.17832840979099274, 0))
mat.SetRow(3, gs.Vector4(94.54534149169922, 228.73983764648438, 66.8308334350586, 1))

frustum = gs.Frustum(gs.ZoomFactorToFov(1.399999976158142), 0.5, 50, gs.Vector2(1.7777777910232544, 1.0), mat)
frustum_planes = gs.BuildFrustumPlanes(frustum)

min_max = gs.MinMax(gs.Vector3(0, 128, 64), gs.Vector3(16, 192, 96))

min = min_max.mn
max = min_max.mx
center = min_max.GetCenter()

# visibility is clipped for the minmax
visibility = gs.ClassifyMinMax(frustum_planes, min_max)

# visibility is outside for my cut in 4 in x axis, what I ve done wrong ?
visibility = gs.ClassifyMinMax(frustum_planes, gs.MinMax(gs.Vector3(min.x, min.y, min.z),       gs.Vector3(max.x, center.y, center.z)))
visibility = gs.ClassifyMinMax(frustum_planes, gs.MinMax(gs.Vector3(min.x, min.y, center.z),    gs.Vector3(max.x, center.y, max.z)))
visibility = gs.ClassifyMinMax(frustum_planes, gs.MinMax(gs.Vector3(min.x, center.y, min.z),    gs.Vector3(max.x, max.y, center.z)))
visibility = gs.ClassifyMinMax(frustum_planes, gs.MinMax(gs.Vector3(min.x, center.y, center.z), gs.Vector3(max.x, max.y, max.z)))
