import ast

from .variableMap import VariableMap

from ..utils import Randoms

operators = [ast.Add(), ast.Sub(), 
            ast.Mult(), ast.MatMult(), 
            ast.Div(), ast.Mod(), ast.Pow(), 
            ast.LShift(), ast.RShift(), 
            ast.BitOr(), ast.BitXor(), 
            ast.BitAnd(), ast.FloorDiv()]

class AMMutator(ast.NodeTransformer):
    '''AssignmentMender's Mutation'''
    def __init__(self, lineno:int, vari_hist:dict):
        self.lineno = lineno
        self.vari_hist = vari_hist
        self.var_type_dict = {}
        self.vm = VariableMap()

        # OR: Operator Replacement
        # VNR: Variable Name Replacement
        # SD: Statement Deletion
        self.mutation = Randoms.choice(['OR', 'VNR', 'SD'])
        if self.mutation == 'VNR':
            self.var_type_dict = self.vm.get_var_type_dict(self.vari_hist)

    def visit(self, node):
        if hasattr(node, 'lineno') and node.lineno-1 == self.lineno:
            if self.mutation == 'OR':
                if isinstance(node, ast.BinOp):
                    new_op = Randoms.choice(operators)
                    while new_op == node.op:
                        new_op = Randoms.choice(operators)
                    node.op = new_op
            elif self.mutation == 'VNR':
                if isinstance(node, (ast.Name)):
                    new_var = self.vm.get_same_type_var(node.id, self.var_type_dict)
                    if new_var is not None:
                        node.id = new_var
                elif isinstance(node, ast.arg):
                    new_var = self.vm.get_same_type_var(node.arg, self.var_type_dict)
                    if new_var is not None:
                        node.arg = new_var
            else:
                return None
        return self.generic_visit(node)

    def run(self, tree):
        swt_tree = self.visit(tree)
        return ast.unparse(swt_tree)