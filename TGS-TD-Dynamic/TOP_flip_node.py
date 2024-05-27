
import json
import os

def generate_input_name(index, input_type):
    return "In{}({})".format(index, input_type)

def create_dynamic_node():
    # Get the path to the directory where this script is located
    script_dir = os.path.dirname(__file__)
    configJSON = os.path.join(script_dir, 'TOP_flip_config.json')
    
    # Load the configuration from the JSON file
    with open(configJSON, "r") as config_file:
        config = json.load(config_file)

    class TOP_flip:
        @classmethod
        def INPUT_TYPES(cls):
            inputs = config["input_types"]
            parsed_inputs = {"required": {}, "optional": {}}
            for index, (key, value) in enumerate(inputs["required"].items(), start=1):
                input_type, properties = value
                input_name = generate_input_name(index, input_type)
                parsed_inputs["required"][input_name] = (input_type, properties)
            
            for key, value in inputs.get("optional", {}).items():
                input_type, properties = value
                parsed_inputs["optional"][key] = (input_type, properties)
                
            return parsed_inputs

        RETURN_TYPES = tuple(config["output_types"])
        FUNCTION = "node_function"

        def node_function(self, **inputs):
            # Example logic that uses dynamic inputs
            output = "Processed inputs: {}".format(inputs)
            return (output,)

    return TOP_flip

# Create an instance of the dynamic node
TOP_flip = create_dynamic_node()
