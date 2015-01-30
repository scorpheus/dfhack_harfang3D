-- %{Name=Cone;Type=SceneCreate;Menu=Primitive%}
execution_context = gs.ScriptContextAll

radius = 1 --> float
height = 1 --> float
sides = 4 --> int

function CreateRenderGeometry(uname)
	geo = gs.CoreGeometry()
	geo:SetName(uname)

	geo:AllocateMaterialTable(1)
	geo:SetMaterial(0, "@core/materials/default.xml", true)

	-- generate vertices
	if geo:AllocateVertex(sides + 1) == 0 then
		return
	end

	for c=0,(sides-1) do
        c_a = c * (math.rad(360)) / sides
        geo:SetVertex(c, math.cos(c_a) * radius, 0, math.sin(c_a) * radius)
	end
	geo:SetVertex(sides, 0, height, 0)

	-- build polygons
	if geo:AllocatePolygon(sides + 1) == 0 then
		return
	end

	geo:SetPolygon(0, sides, 0)
	for n=1,sides do
	   geo:SetPolygon(n, 3, 0)
	end

	if geo:AllocatePolygonBinding() == 0 then
		return
	end

    local idx_vtx_up_list = {}
    -- the big polygon at the back of the cone
	for c=0,(sides-1) do
        idx_vtx_up_list [#idx_vtx_up_list +1] = c
    end
    geo:SetPolygonBinding(0, idx_vtx_up_list)

    -- side of the cone
    for c=0,(sides-1) do
        local next_id = c+1
        if c+1 >= sides then
            next_id = 0
        end
        geo:SetPolygonBinding(c+1, {next_id ,
                                    c,
                                    sides})
    end

	geo:ComputeVertexNormal(0.7)

	return render_system:CreateGeometry(geo)
end

function GetUniqueName()
	return "@gen/cone_"..radius.."_"..height.."_"..sides
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
	if sides < 3 then sides = 3 end
	Setup() -- simply regenerate the geometry on parameter change
end

function Delete()
	this:RemoveComponent(object)
end
