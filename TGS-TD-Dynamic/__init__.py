from .dynamic_node import DynamicNode
from .TOP_flipflop_node import TOP_flipflop
from .TOP_flip_node import TOP_flip

NODE_CLASS_MAPPINGS = {
    "TOP_flip": TOP_flip,
    "TOP_flipflop": TOP_flipflop,
    "DynamicNode": DynamicNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "TOP_flip": "TOP_flip Node",
    "TOP_flipflop": "TOP_flipflop Node",
    "DynamicNode": "Dynamic Node"
    
}