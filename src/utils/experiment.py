import ast

from .ted import TED
from ..transform import DefUseChain

class Experiment:
    def __init__(self, solutions):
        self.solutions = solutions

    def minimization(self, programs:dict) -> dict:
        feedbacks = {}
        # self._filtering()
        # self._deduplication()
        for file, childs in self.solutions.items():
            parent = programs[file]
            parent_ast_size = sum(1 for _ in ast.walk(ast.parse(parent)))
            # First fit generation and patch
            first_gen, first_patch = min(childs.items()) 
            # Minimum ted generation and patch
            min_gen, min_patch = min(childs.items(), key=lambda x: TED().run(parent, x[1]) / parent_ast_size)
            feedbacks[file] = (first_gen, first_patch, min_gen, min_patch)
        return feedbacks
    
    def _filtering(self):
        # Filtering programs that has unbound variables
        for file, programs in self.solutions.items():
            valid_programs = []
            for code in set(programs):
                duc = DefUseChain()
                duc.run(code)
                if duc.unbound_vars:
                    continue
                valid_programs.append(code)
            self.solutions[file] = valid_programs
    
    def _deduplication(self):
        # Deduplication programs that has same AST
        nomalize_dict = {}
        for file, programs in self.solutions.items():
            for code in programs:
                nomalize_code = self.__normalize(code)
                nomalize_dict.setdefault(nomalize_code, {}).setdefault(file, []).append(code)
        for file, programs in nomalize_dict.values().items():
            if 1 < len(programs):
                self.solutions[file] = [programs[0]]

    def __normalize(self, code):
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                node.name = "class"
            if isinstance(node, ast.FunctionDef):
                node.name = "func"
            if isinstance(node, ast.Name):
                node.id = "name"
            if isinstance(node, ast.arg):
                node.arg = "arg"
        return ast.dump(tree)
    
    