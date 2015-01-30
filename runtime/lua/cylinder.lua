-- %{Name=Cylinder;Type=SceneCreate;Menu=Primitive%}
execution_context = gs.ScriptContextAll

radius = 0.5 --> float
height = 1.0 --> float
c_count = 16 --> int

function Wrap(v, range_start, range_end)
	dt = math.floor(math.floor(range_end) - math.floor(range_start) + 1)
	v = math.floor(v)

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
	if geo:AllocateVertex(c_count * 2) == 0 then
		return
	end

	for c=0,(c_count-1) do
        c_a = c * (math.rad(360)) / c_count
        geo:SetVertex(c, math.cos(c_a) * radius, height*0.5, math.sin(c_a) * radius)
	end
	for c=0,(c_count-1) do
        c_a = c * (math.rad(360)) / c_count
        geo:SetVertex(c + c_count, math.cos(c_a) * radius, -height*0.5, math.sin(c_a) * radius)
	end

	-- Build polygons.
	if geo:AllocatePolygon(c_count + 2) == 0 then
		return
	end

	geo:SetPolygon(0, c_count, 0)
	geo:SetPolygon(1, c_count, 0)

	for c=0,(c_count-1) do
	   geo:SetPolygon(c + 2, 4, 0)
	end

    geo:AllocateRgb(c_count*2 + c_count*4)
    geo:AllocateUVChannel(3, c_count*2 + c_count*4)

	if geo:AllocatePolygonBinding() == 0 then
		return
	end

    idx_vtx_up_list = {}
    uv_list = {}
    color_list = {}
	for c=0,(c_count-1) do
        idx_vtx_up_list [#idx_vtx_up_list +1] = (c_count-1)-c

        c_a = c * (math.rad(360)) / c_count
        uv_list [#uv_list +1] = gs.Vector2(math.cos(c_a)*0.25 + 0.25, math.sin(c_a)*0.25 + 0.25)
        color_list [#color_list +1] = gs.Color.One
    end
    geo:SetRgb(0, color_list)
    geo:SetUV(0, 0, uv_list)
    geo:SetUV(1, 0, uv_list)
    geo:SetUV(2, 0, uv_list)
    geo:SetPolygonBinding(0, idx_vtx_up_list)


    idx_vtx_down_list = {}
    uv_list = {}
    color_list = {}
	for c=0,(c_count-1) do
        idx_vtx_down_list [#idx_vtx_down_list +1] = c + c_count

        c_a = c * (math.rad(360)) / c_count
        uv_list [#uv_list +1] = gs.Vector2(math.cos(c_a)*0.25 + 0.75, math.sin(c_a)*0.25 + 0.25)
        color_list [#color_list +1] = gs.Color.One
    end
    geo:SetRgb(1, color_list)
    geo:SetUV(0, 1, uv_list)
    geo:SetUV(1, 1, uv_list)
    geo:SetUV(2, 1, uv_list)
    geo:SetPolygonBinding(1, idx_vtx_down_list)

    for c=0,(c_count-1) do
        geo:SetPolygonBinding(c+2, {c,
                                    Wrap(c + 1, 0, c_count - 1) ,
                                    Wrap(c + c_count + 1, c_count, c_count * 2 - 1) ,
                                    c + c_count})
        geo:SetRgb(c+2, {gs.Color.One, gs.Color.One, gs.Color.One, gs.Color.One})
        geo:SetUV(0, c+2, {gs.Vector2(c/c_count, 0.5), gs.Vector2((c+1)/c_count, 0.5), gs.Vector2(c/c_count, 1), gs.Vector2((c+1)/c_count, 1)})
    end

	geo:ComputeVertexNormal(0.7)
    geo:ComputeVertexTangent()

	return render_system:CreateGeometry(geo)
end

function GetUniqueName()
	return "@gen/cylinder_"..radius.."_"..height.."_"..c_count
end

function Setup()
	render_system = engine:GetRenderSystemAsync()

	uname = GetUniqueName()
	render_geo = render_system:HasGeometry(uname)

	if render_geo == nil then
		render_geo = CreateRenderGeometry(uname)
	end

	if object == nil then
		if this.object == nil then
			object = gs.Object()
			this:AddComponent(object)
		else
			object = this.object
		end
	end

	object:SetDoNotSerialize(true)
	object:SetGeometry(render_geo)
end

function OnEditorSetParameter(name)
	if c_count < 6 then c_count = 6 end
	if radius < 0.1 then radius = 0.1 end

	Setup() -- simply regenerate the geometry on parameter change
end

function Delete()
	this:RemoveComponent(object)
end
