import ast

from .nodeParser import NodeParser
from ..utils import Randoms

class NodeMap:
    @classmethod
    def get_line_node(cls, tree:ast, lineno:int) -> dict:
        return cls.get_line_node_map(tree)[lineno]
    
    @classmethod
    def get_line_node_map(cls, tree:ast) -> dict:
        NodeParser.run(tree=tree)
        return NodeParser.line_node_map
    
    @classmethod
    def run(cls, a_tree:ast, a_trace:list, b_tree:ast, b_trace:list) -> dict:
        node_map = {}
        a_line_node_map = cls.get_line_node_map(a_tree)
        a_node_map = {a_line_node_map[lineno]:a_line_node_map[lineno].__class__.__name__ 
                      for lineno in a_trace if lineno in a_line_node_map.keys()}
        b_line_node_map = cls.get_line_node_map(b_tree)
        b_node_map = {b_line_node_map[lineno]:b_line_node_map[lineno].__class__.__name__ 
                      for lineno in b_trace if lineno in b_line_node_map.keys()}
        
        if list(a_node_map.values()) == list(b_node_map.values()):
            node_map = {a_node:b_node 
                        for a_node, b_node in 
                        zip(list(a_node_map.keys()), list(b_node_map.keys()))}
        else:
            for a_node, a_name in a_node_map.items():
                candidate = [b_node for b_node, b_name in b_node_map.items() 
                             if b_name == a_name and b_node not in node_map.values()]
                if candidate: node_map[a_node] = Randoms.choice(candidate)
                # else: node_map[a_node] = None # Delete Node
            
            # for b_node in b_node_map.keys():
            #     if b_node not in node_map.values():
            #         node_map[b_node] = b_node # Insert Node
                    
        return node_map
