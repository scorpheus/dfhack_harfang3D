-- %{Name=Plane;Type=SceneCreate;Menu=Primitive%}
execution_context = gs.ScriptContextAll

width = 1 --> float
length = 1 --> float

function CreateRenderGeometry(uname)
	geo = gs.CoreGeometry()
	geo:SetName(uname)

	d = gs.Vector2(width, length)
	d = d * 0.5

	geo:AllocateMaterialTable(1)
	geo:SetMaterial(0, "@core/materials/default.xml", true)

	-- generate vertices
	if geo:AllocateVertex(4) == 0 then
		return
	end

	geo:SetVertex(0,-d.x, 0, -d.y);
	geo:SetVertex(1, -d.x, 0, d.y);
	geo:SetVertex(2, d.x, 0, d.y);
	geo:SetVertex(3, d.x, 0, -d.y);

	-- build polygons
	if geo:AllocatePolygon(1) == 0 then
		return
	end

	geo:SetPolygon(0, 4, 0)

	if geo:AllocatePolygonBinding() == 0 then
		return
	end

	geo:SetPolygonBinding(0, {0,1,2,3})

	geo:ComputeVertexNormal(0.7)

	return render_system:CreateGeometry(geo)
end

function GetUniqueName()
	return "@gen/plane_"..width.."_"..length
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
	Setup() -- simply regenerate the geometry on parameter change
end

function Delete()
	this.object:SetGeometry(nil)
end
