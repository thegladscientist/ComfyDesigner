import numpy as np
import touchpy as tp
import json

class ExampleRunComp:
    def __init__(self):
        self.inputs = []
        self.outputs = []
        self.parameters = []

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

        generate_json_config(this.inputs, this.outputs, this.parameters, 'dynamic_config-flip.json')

    def runComp(self, tox_path):
        comp = tp.Comp(tox_path)

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

# Function to convert parameter Python types to ComfyUI types
def convert_param_type(param_type):
    param_type_mapping = {
        "int": "INT",
        "float": "FLOAT",
        "str": "STRING",
        "bool": "BOOLEAN",
        # Add more mappings if needed
    }
    return param_type_mapping.get(param_type, "UNKNOWN")

# Function to generate JSON config
def generate_json_config(inputs, outputs, parameters, output_json_path):
    config = {
        "input_types": {
            "required": {
                f"In{index + 1}({convert_type(input_type)})": [convert_type(input_type), {"default": None}]
                for index, (name, input_type) in enumerate(inputs)
            },
            "optional": {
                f"{par}({convert_param_type(par_type)})": [convert_param_type(par_type), {"default": default_value}]
                for par, par_type, default_value in parameters
            }
        },
        "output_types": [convert_type(output_type) for name, output_type in outputs]
    }

    with open(output_json_path, "w") as config_file:
        json.dump(config, config_file, indent=4)

# Main execution
if __name__ == "__main__":
    example = ExampleRunComp()
    example.runComp('TOP_flip.tox')
