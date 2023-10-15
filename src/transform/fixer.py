import ast

class Fixer(ast.NodeTransformer):
    def __init__(self, node_map:dict):
        self.node_map = node_map
        self.node_tree = dict()
    
    def check(self, node):
        stack = [node]
        while stack:
            current = stack.pop()
            for attr_name in ["body", "orelse"]:
                if hasattr(current, attr_name):
                    for child in getattr(current, attr_name):
                        if child in self.node_map.keys():
                            return True
                        stack.append(child)
        return False

    def visit(self, node):
        if isinstance(node, ast.stmt) and hasattr(node, 'body'):
            self.node_tree[node] = [c for c in node.body]

        if node in self.node_map.keys():
            patch = self.node_map[node]
            if patch is None: # Delete Node
                delete = False
                for parent, childs in self.node_tree.items():
                    if node in childs and len(childs) > 1:
                        delete = True
                        childs.remove(node)
                        self.node_tree[parent] = childs
                        break
                if delete: return None # Delete Node
            else: # Replace Node
                if self.check(node):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        if node.name == patch.name:
                            node.args = patch.args
                    elif isinstance(node, ast.ClassDef):
                        pass
                    elif isinstance(node, (ast.For, ast.AsyncFor)):
                        node.target = patch.target
                        node.iter = patch.iter
                    elif isinstance(node, (ast.While, ast.If)):
                        node.test = patch.test
                    elif isinstance(node, (ast.With, ast.AsyncWith)):
                        node.items = patch.items
                    
                    # Insert Node
                    # insert_idx = 0
                    # for child in patch.body:
                    #     if child in self.node_map.keys() and not self.check(child):
                    #         node.body.insert(insert_idx, child)
                    #     insert_idx += 1

                else: # Replace | Insert Node
                    node = patch
            
        return self.generic_visit(node)

    def run(self, tree):
        tree = self.visit(tree)
        return ast.unparse(tree)
