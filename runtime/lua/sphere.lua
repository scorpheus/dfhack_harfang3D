-- %{Name=Sphere;Type=SceneCreate;Menu=Primitive%}
execution_context = gs.ScriptContextAll

radius = 0.5 --> float
s_count = 6 --> int
c_count = 16 --> int

function Wrap(v, range_start, range_end)
	dt = math.floor(math.floor(range_end) - math.floor(range_start) + 1)

	while v < range_start do
		v = v+dt
	end
	while v > range_end do
		v = v-dt
	end

	return v
end

function CreateRenderGeometry(uname)
	geo = gs.CoreGeometry()
	geo:SetName(uname)

	geo:AllocateMaterialTable(1)
	geo:SetMaterial(0, "@core/materials/default.xml", true)

	-- generate vertices
	if geo:AllocateVertex((s_count + 1) * c_count + 2) == 0 then
		return
	end

	geo:SetVertex(0, 0, radius, 0)

	vtx_counter = 1
	for s=0,s_count do

		t = (s + 1) / (s_count + 2)
		a = t * math.rad(180)

		y = math.cos(a) * radius
		s_r = math.sin(a) * radius

		for c=0,(c_count-1) do

			c_a = c * (math.rad(360)) / c_count

			geo:SetVertex(vtx_counter, math.cos(c_a) * s_r, y, math.sin(c_a) * s_r)
			vtx_counter = vtx_counter + 1
		end
	end

	geo:SetVertex(vtx_counter, 0, -radius, 0)

	-- Build polygons.
	if geo:AllocatePolygon((s_count + 2) * c_count) == 0 then
		return
	end

	poly_counter = 0
    uv_counter = 0

	for c=0,(c_count-1) do
	   geo:SetPolygon(poly_counter, 3, 0)
	   poly_counter = poly_counter+1
        uv_counter = uv_counter + 3
	end

	for s=0,(s_count-1) do
		for c=0,(c_count-1) do
		   geo:SetPolygon(poly_counter, 4, 0)
		   poly_counter = poly_counter+1
        uv_counter = uv_counter + 4
		end
	end

	for c=0,(c_count-1) do
	   geo:SetPolygon(poly_counter, 3, 0)
	   poly_counter = poly_counter+1
        uv_counter = uv_counter + 3
	end

    geo:AllocateRgb(uv_counter)
    geo:AllocateUVChannel(3, uv_counter)

	if geo:AllocatePolygonBinding() == 0 then
		return
	end

	poly_counter = 0
	for c=0,(c_count-1) do
		geo:SetPolygonBinding(poly_counter, {0, Wrap(c + 2, 1, c_count), c+1})
        geo:SetRgb(poly_counter, {gs.Color.One, gs.Color.One, gs.Color.One})
        geo:SetUV(0, poly_counter, {gs.Vector2(0, Wrap((c+0.5)/c_count, 0, 1)), gs.Vector2(1/(s_count+2), Wrap((c+1)/c_count, 0, 1)), gs.Vector2(1/(s_count+2), c/c_count)})
        geo:SetUV(1, poly_counter, {gs.Vector2(0, Wrap((c+0.5)/c_count, 0, 1)), gs.Vector2(1/(s_count+2), Wrap((c+1)/c_count, 0, 1)), gs.Vector2(1/(s_count+2), c/c_count)})
        geo:SetUV(2, poly_counter, {gs.Vector2(0, Wrap((c+0.5)/c_count, 0, 1)), gs.Vector2(1/(s_count+2), Wrap((c+1)/c_count, 0, 1)), gs.Vector2(1/(s_count+2), c/c_count)})
		poly_counter = poly_counter+1
	end

	for s=0,(s_count-1) do
		i = 1 + c_count * s
		for c=0,(c_count-1) do
			geo:SetPolygonBinding(poly_counter, {i + c,
												Wrap(i + c + 1, i, i + c_count - 1) ,
												Wrap(i + c + c_count + 1, i + c_count, i + c_count * 2 - 1) ,
												i + c + c_count})
            uv1 = (s+1)/(s_count+2)
            uv2 = (s+2)/(s_count+2)
            uv3 = c/c_count
            uv4 = Wrap((c+1)/c_count, 0, 1)
            geo:SetRgb(poly_counter, {gs.Color.One, gs.Color.One, gs.Color.One, gs.Color.One})
            geo:SetUV(0, poly_counter, {gs.Vector2(uv1, uv3), gs.Vector2(uv1, uv4), gs.Vector2(uv2, uv4), gs.Vector2(uv2, uv3)})
            geo:SetUV(1, poly_counter, {gs.Vector2(uv1, uv3), gs.Vector2(uv1, uv4), gs.Vector2(uv2, uv4), gs.Vector2(uv2, uv3)})
            geo:SetUV(2, poly_counter, {gs.Vector2(uv1, uv3), gs.Vector2(uv1, uv4), gs.Vector2(uv2, uv4), gs.Vector2(uv2, uv3)})
		   poly_counter = poly_counter+1
		end
	end

	i = 1 + c_count * s_count
	for c=0,(c_count-1) do
		geo:SetPolygonBinding(poly_counter, {i + c, Wrap(i + c + 1, i, i + c_count - 1), i + c_count})
        geo:SetRgb(poly_counter, {gs.Color.One, gs.Color.One, gs.Color.One})
        geo:SetUV(0, poly_counter, {gs.Vector2(1-1/(s_count+2), c/c_count), gs.Vector2(1-1/(s_count+2), Wrap((c+1)/c_count, 0, 1)), gs.Vector2(0.99, Wrap((c+0.5)/c_count, 0, 1))})
        geo:SetUV(1, poly_counter, {gs.Vector2(1-1/(s_count+2), c/c_count), gs.Vector2(1-1/(s_count+2), Wrap((c+1)/c_count, 0, 1)), gs.Vector2(0.99, Wrap((c+0.5)/c_count, 0, 1))})
        geo:SetUV(2, poly_counter, {gs.Vector2(1-1/(s_count+2), c/c_count), gs.Vector2(1-1/(s_count+2), Wrap((c+1)/c_count, 0, 1)), gs.Vector2(0.99, Wrap((c+0.5)/c_count, 0, 1))})
		poly_counter = poly_counter+1
	end

	geo:ComputeVertexNormal(0.7)
    geo:ComputeVertexTangent()

	return render_system:CreateGeometry(geo)
end

function GetUniqueName()
	return "@gen/sphere_"..radius.."_"..s_count.."_"..c_count
end

function Setup()
	render_system = engine:GetRenderSystemAsync()

	uname = GetUniqueName()
	render_geo = render_system:HasGeometry(uname)

	if render_geo == nil then
		render_geo = CreateRenderGeometry(uname)
	end

	this.object:SetGeometry(render_geo)
end

function OnEditorSetParameter(name)
	if s_count < 4 then s_count = 4 end
	if c_count < 6 then c_count = 6 end
	if radius < 0.1 then radius = 0.1 end

	Setup() -- simply regenerate the geometry on parameter change
end

function Delete()
	this.object:SetGeometry(nil)
end
