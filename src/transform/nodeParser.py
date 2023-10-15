from ordered_set import OrderedSet
import ast
import keyword
import builtins

RESERVED_WORDS = OrderedSet(keyword.kwlist)
BUILTIN_WORDS = OrderedSet(dir(builtins))
MODULE_WORDS = OrderedSet(globals())

class NodeParser(ast.NodeVisitor):
    line_node_map = dict()
    var_name_list = OrderedSet()
    lineno = 0
    key_input = False

    @classmethod
    def init_global_vars(cls):
        cls.line_node_map = dict()
        cls.var_name_list = OrderedSet()
        cls.lineno = 0
        cls.key_input = False
    
    def visit(self, node):
        if hasattr(node, 'lineno'):
            self.lineno = node.lineno -1

        if isinstance(node, ast.stmt) and hasattr(node, 'lineno'):
            self.line_node_map[node.lineno-1] = node
            # if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Import, ast.ImportFrom)):
            #     self.line_node_map[node.lineno-1] = node
        
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)
    
    def visit_Name(self, node):
        if hasattr(node, 'id'):
            if node.id == 'input' and isinstance(node.ctx, ast.Load):
                self.key_input = True
            elif isinstance(node.ctx, ast.Store):
                var_name = str(node.id)
                if var_name not in RESERVED_WORDS and \
                    var_name not in BUILTIN_WORDS and \
                    var_name not in MODULE_WORDS:
                    self.var_name_list.add(var_name)
        self.generic_visit(node)

    def visit_arg(self, node):
        self.var_name_list.add(str(node.arg))
        self.generic_visit(node)

    def visit_Attribute(self, node):
        if hasattr(node, 'attr'):
            if node.attr in ['readline', 'stdin']:
                self.key_input = True
        self.generic_visit(node)
    
    @classmethod
    def run(cls, code:str='', tree:ast=''):
        cls.init_global_vars()
        if code: tree = ast.parse(code)
        node_parser = NodeParser()
        node_parser.visit(tree)