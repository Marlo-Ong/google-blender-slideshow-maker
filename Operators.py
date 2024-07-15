import bpy
from bpy.types import Operator, Panel
from bpy.props import StringProperty, IntProperty

# Date Input
class DateInputOperator(Operator):
    bl_idname = "example.date_input"
    bl_label = "Enter Date"
    bl_options = {'REGISTER', 'UNDO'}

    year: IntProperty(
        name="Year",
        description="Enter the year",
        min=1900,
        max=2100,
        default=2024
    )
    month: IntProperty(
        name="Month",
        description="Enter the month",
        min=1,
        max=12,
        default=7
    )
    day: IntProperty(
        name="Day",
        description="Enter the day",
        min=1,
        max=31,
        default=13
    )

    def execute(self, context):
        date_string = f"{self.year:04d}-{self.month:02d}-{self.day:02d}"
        context.scene.user_input_date_start = date_string
        self.report({'INFO'}, f"Date entered: {date_string}")
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

class DateInputPanel(Panel):
    bl_label = "Date Input Example"
    bl_idname = "OBJECT_PT_date_input"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tools'

    def draw(self, context):
        layout = self.layout
        
        # Display the current date
        layout.label(text="Current Date:")
        layout.label(text=context.scene.user_input_date_start if context.scene.user_input_date_start else "Not set")
        
        # Add a button to change the date
        layout.operator("example.date_input", text="Change Date")
        
# Set up directory selector
class SelectFolderOperator(Operator):
    bl_idname = "example.select_folder"
    bl_label = "Select Folder"
    
    directory: StringProperty(
        name="Folder Path",
        description="Choose a folder:",
        subtype='DIR_PATH'
    )
    
    def execute(self, context):
        # The selected path is stored in self.directory
        print(f"Selected folder: {self.directory}")
        
        # You can save this to a custom property, or use it as needed
        context.scene.photos_path = self.directory
        
        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
class WaitForFolderSelectionOperator(Operator):
    bl_idname = "example.wait_for_folder_selection"
    bl_label = "Wait for Folder Selection"

    def execute(self, context):
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if event.type == 'TIMER':
            if context.scene.photos_path:
                print("Folder selected, continuing execution...")
                return {'FINISHED'}
        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, window=context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

def register():
    bpy.utils.register_class(SelectFolderOperator)
    bpy.utils.register_class(WaitForFolderSelectionOperator)

    # Where the chosen path is saved
    bpy.types.Scene.photos_path = StringProperty(
        name="Photos Path",
        description="Stores the selected path containing photos for slideshow",
        default=""
    )
    
    bpy.utils.register_class(DateInputOperator)
    bpy.utils.register_class(DateInputPanel)
    bpy.types.Scene.user_input_date_start = StringProperty(
        name="User Input Date Start",
        description="Stores the start date entered by the user",
        default=""
    )
    bpy.types.Scene.user_input_date_end = StringProperty(
        name="User Input Date End",
        description="Stores the end date entered by the user",
        default=""
    )

def select_folder_and_wait():
    bpy.context.scene.photos_path = ""  # Reset the path
    bpy.ops.example.select_folder('INVOKE_DEFAULT')
    bpy.ops.example.wait_for_folder_selection('INVOKE_DEFAULT')
    return bpy.context.scene.photos_path

def get_date_input():
    bpy.ops.example.date_input('INVOKE_DEFAULT')
    return bpy.context.scene.user_input_date_start