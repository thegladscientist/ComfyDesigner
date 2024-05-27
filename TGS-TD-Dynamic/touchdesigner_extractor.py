import numpy as np
import touchpy as tp
import json
import os

class ExampleRunComp:
    def __init__(self, tox_path):
        self.inputs = []
        self.outputs = []
        self.parameters = []
        self.tox_path = tox_path

    @staticmethod
    def on_layout_change(comp, this):
        print('layout changed:')
        print('in tops:', comp.in_tops.names)
        print('out tops:', comp.out_tops.names)
        print('in chops:', comp.in_chops.names)
        print('out chops:', comp.out_chops.names)
        print('in dats:', comp.in_dats.names)
        print('out dats:', comp.out_dats.names)
        print('pars:', comp.par.names)

        # Collect input names and types
        this.inputs = []
        for input_type, input_collection in [("TOP", comp.in_tops), ("CHOP", comp.in_chops), ("DAT", comp.in_dats)]:
            for name in input_collection.names:
                this.inputs.append((name, input_type))

        # Collect output names and types
        this.outputs = []
        for output_type, output_collection in [("TOP", comp.out_tops), ("CHOP", comp.out_chops), ("DAT", comp.out_dats)]:
            for name in output_collection.names:
                this.outputs.append((name, output_type))

        # Collect parameter names and types
        this.parameters = []
        for par in comp.par.names:
            par_value = comp.par[par].val
            par_type = type(par_value).__name__
            this.parameters.append((par, par_type, par_value))

        tox_name = os.path.splitext(os.path.basename(this.tox_path))[0]
        config_filename = f'{tox_name}_config.json'
        dynamic_node_filename = f'{tox_name}_node.py'

        generate_json_config(this.inputs, this.outputs, this.parameters, config_filename)
        generate_dynamic_node(dynamic_node_filename, config_filename, tox_name)
        update_init_file(tox_name)

    def runComp(self):
        comp = tp.Comp(self.tox_path)

        comp.set_on_layout_change_callback(self.on_layout_change, self)

        comp.start()
        comp.unload()

# Function to convert TouchDesigner types to ComfyUI types
def convert_type(touch_type):
    type_mapping = {
        "TOP": "IMAGE",
        "CHOP": "FLOAT",
        "DAT": "STRING"
    }
    return type_mapping.get(touch_type, "UNKNOWN")

# Function to generate JSON config
def generate_json_config(inputs, outputs, parameters, output_json_path):
    config = {
        "input_types": {
            "required": {
                "In{}({})".format(index + 1, convert_type(input_type)): [convert_type(input_type), {"default": None}]
                for index, (name, input_type) in enumerate(inputs)
            },
            "optional": {
                "{}({})".format(par, par_type): [par_type, {"default": default_value}]
                for par, par_type, default_value in parameters
            }
        },
        "output_types": [convert_type(output_type) for name, output_type in outputs]
    }

    with open(output_json_path, "w") as config_file:
        json.dump(config, config_file, indent=4)

# Function to add new dynamic node to the init file to be loaded as a custom node
def update_init_file(tox_name):
    init_path = os.path.join(os.path.dirname(__file__), '__init__.py')
    
    # Read the current contents of the init file
    with open(init_path, "r") as init_file:
        lines = init_file.readlines()

    # Prepare the new import and mapping lines
    import_line = "from .{}_node import {}\n".format(tox_name, tox_name)
    class_mapping_line = '    "{}": {},\n'.format(tox_name, tox_name)
    display_name_mapping_line = '    "{}": "{} Node",\n'.format(tox_name, tox_name)

    # Insert the import line at the top, after the initial imports
    for i, line in enumerate(lines):
        if not line.startswith("from") and not line.startswith("import"):
            lines.insert(i, import_line)
            break

    # Find the positions to insert the new mappings
    class_mapping_index = None
    display_name_mapping_index = None

    for i, line in enumerate(lines):
        if line.strip() == "NODE_CLASS_MAPPINGS = {":
            class_mapping_index = i + 1
        elif line.strip() == "NODE_DISPLAY_NAME_MAPPINGS = {":
            display_name_mapping_index = i + 2

    # Insert the new mappings in the appropriate places
    if class_mapping_index is not None:
        lines.insert(class_mapping_index, class_mapping_line)
    
    if display_name_mapping_index is not None:
        lines.insert(display_name_mapping_index, display_name_mapping_line)

    # Write the updated contents back to the init file
    with open(init_path, "w") as init_file:
        init_file.writelines(lines)

# Function to generate dynamic node Python file
def generate_dynamic_node(filename, config_filename, class_name):
    node_code = """
import json
import os

def generate_input_name(index, input_type):
    return "In{{}}({{}})".format(index, input_type)

def create_dynamic_node():
    # Get the path to the directory where this script is located
    script_dir = os.path.dirname(__file__)
    configJSON = os.path.join(script_dir, '{}')
    
    # Load the configuration from the JSON file
    with open(configJSON, "r") as config_file:
        config = json.load(config_file)

    class {}:
        @classmethod
        def INPUT_TYPES(cls):
            inputs = config["input_types"]
            parsed_inputs = {{"required": {{}}, "optional": {{}}}}
            for index, (key, value) in enumerate(inputs["required"].items(), start=1):
                input_type, properties = value
                input_name = generate_input_name(index, input_type)
                parsed_inputs["required"][input_name] = (input_type, properties)
            
            for key, value in inputs.get("optional", {{}}).items():
                input_type, properties = value
                parsed_inputs["optional"][key] = (input_type, properties)
                
            return parsed_inputs

        RETURN_TYPES = tuple(config["output_types"])
        FUNCTION = "node_function"

        def node_function(self, **inputs):
            # Example logic that uses dynamic inputs
            output = "Processed inputs: {{}}".format(inputs)
            return (output,)

    return {}

# Create an instance of the dynamic node
{} = create_dynamic_node()
""".format(config_filename, class_name, class_name, class_name)

    with open(filename, "w") as node_file:
        node_file.write(node_code)

# Main execution
if __name__ == "__main__":
    # IMPORTANT
    ORIGINAL_TOX_NAME = 'TOP_flip'  # Update me for each TOX to extract from
    # IMPORTANT
    tox_path = ORIGINAL_TOX_NAME + '.tox'
    example = ExampleRunComp(tox_path)
    example.runComp()
