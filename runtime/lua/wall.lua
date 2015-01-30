-- %{Name=Wall;Type=SceneCreate;Menu=Physic Structure%}
execution_context = gs.ScriptContextAll

width = 10 --> float
height = 10 --> float
length = 1 --> float

nb_width = 5 --> int
nb_height = 5 --> int

cube_width = 0
cube_height = 0
cube_length = 0

node_list_wall = {}

function CreateRenderGeometry(uname, cube_width, cube_height, cube_length)
	geo = gs.CoreGeometry()
	geo:SetName(uname)

	d = gs.Vector3(cube_width, cube_height, cube_length)
	d = d * 0.5

	geo:AllocateMaterialTable(1)
	geo:SetMaterial(0, "@core/materials/default.xml", true)

	-- generate vertices
	if geo:AllocateVertex(8) == 0 then
		return
	end

	geo:SetVertex(0,-d.x, d.y, d.z);
	geo:SetVertex(1, d.x, d.y, d.z);
	geo:SetVertex(2, d.x, d.y, -d.z);
	geo:SetVertex(3,-d.x, d.y, -d.z);
	geo:SetVertex(4,-d.x, -d.y, d.z);
	geo:SetVertex(5, d.x, -d.y, d.z);
	geo:SetVertex(6, d.x, -d.y, -d.z);
	geo:SetVertex(7,-d.x, -d.y, -d.z);

	-- build polygons
	if geo:AllocatePolygon(6) == 0 then
		return
	end

	for n=0,6 do
	   geo:SetPolygon(n, 4, 0)
	end

	if geo:AllocatePolygonBinding() == 0 then
		return
	end

	geo:SetPolygonBinding(0, {0,1,2,3})
	geo:SetPolygonBinding(1, {3,2,6,7})
	geo:SetPolygonBinding(2, {7,6,5,4})
	geo:SetPolygonBinding(3, {4,5,1,0})
	geo:SetPolygonBinding(4, {2,1,5,6})
	geo:SetPolygonBinding(5, {0,3,7,4})

	geo:ComputeVertexNormal(0.7)

	return render_system:CreateGeometry(geo)
end

function GetUniqueName(cube_width, cube_height, cube_length)
	return "@gen/brick_"..cube_width.."_"..cube_height.."_"..cube_length
end

function Setup()
	Delete()

	scene = this:GetScene()

	cube_width = width / nb_width
	cube_height = height / nb_height
	cube_length = length

	render_system = engine:GetRenderSystemAsync()

	uname = GetUniqueName(cube_width, cube_height, cube_length)
	render_geo = render_system:HasGeometry(uname)

	if render_geo == nil then
		render_geo = CreateRenderGeometry(uname, cube_width, cube_height, cube_length)
	end

	-- create the wall using the render geo
	count = 1
	for h=0,(nb_height-1) do
		for w=0,(nb_width-1) do
			node = gs.Node()
			node:SetDoNotSerialize(true)

			node:SetName("brick")
			transform = gs.Transform()
			transform:SetPosition(gs.Vector3(w * cube_width, h* cube_height, 0))
			transform:SetParent(this)
			node:AddComponent(transform)
			object = gs.Object()
			object:SetGeometry(render_geo)
			node:AddComponent(object)

			node:AddComponent(gs.BulletRigidBody())
			box_collision = gs.BulletBoxCollision()
			box_collision:SetDimensions(gs.Vector3(cube_width, cube_height, cube_length))
			node:AddComponent(box_collision)

			node:SetInstantiatedBy(this)
			scene:AddNode(node)

			node_list_wall[count] = node
			count = count+1
		end
	end

end

function OnEditorSetParameter(name)
	Setup() -- simply regenerate the geometry on parameter change
end

function Delete()
	for i=1, #node_list_wall do
		scene:RemoveNode(node_list_wall[i])
	end
	node_list_wall = {}
end
