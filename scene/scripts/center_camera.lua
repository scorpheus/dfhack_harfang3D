
function Setup()
	keyboard_device = gs.GetInputSystem():GetDevice("keyboard")
end

function Update()
	if keyboard_device:IsDown(gs.InputDevice.KeyLeft) then
		this.transform:SetRotation(this.transform:GetRotation() - gs.Vector3(0,0.01,0))
	else
		if keyboard_device:IsDown(gs.InputDevice.KeyRight) then
			this.transform:SetRotation(this.transform:GetRotation() + gs.Vector3(0,0.01,0))
		end
	end
end