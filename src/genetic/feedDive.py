import ast
from tqdm import tqdm
import logging

from ..execution import Preprocess, FaultLocalization
from ..transform import VariableMap, SWTVariables, NodeMap, Fixer
from ..utils import regularize, Randoms



class FeedDive:
    def __init__(self, preproc:Preprocess, logfile:str):
        logging.basicConfig(filename=logfile, 
                            level=logging.DEBUG, 
                            format='%(message)s', 
                            filemode='w')

        self.preproc = preproc
        self.tester = preproc.tester
        self.solutions = dict()


    def population(self, pop_size:int, programs:dict) -> dict:
        # return {f'{file}_0':regularize(code) for file, code in programs.items()}
        file_list = list(programs.keys())
        sample_list = Randoms.sample(file_list, pop_size)
        return {f'{file}_0':regularize(programs[file]) for file in sample_list}
    
    def selection(self, p_id_1:str, populations:dict):
        select_dict = {}
        failed_tcs = []
        
        parent1, test_hist, _, trace_hist1 = self.preproc.run_data[p_id_1]
        tree1 = ast.parse(parent1)

        populations_keys = list(populations.keys())
        populations_keys.remove(p_id_1)

        line_node_map = NodeMap.get_line_node_map(tree1)

        for testcase_no, result in test_hist.items():
            if result == 'Success' or testcase_no not in self.preproc.trace_data.keys(): continue
            failed_tcs.append(testcase_no)
            traces = trace_hist1[testcase_no]
            wrong_node_names = [line_node_map[line].__class__.__name__ for line in traces if line in line_node_map.keys()]
            for p_id_2, refer_nodes in self.preproc.trace_data[testcase_no].items():
                if p_id_2 not in populations_keys: continue
                refer_node_names = [node.__class__.__name__ for node in refer_nodes]
                if wrong_node_names == refer_node_names:
                    select_dict[testcase_no] = p_id_2
                    # break

        testcase_no = Randoms.choice(list(select_dict.keys())) if select_dict else \
                        Randoms.choice(failed_tcs) if failed_tcs else \
                        Randoms.choice(list(test_hist.keys()))
        candidates = [p_id for p_id in populations_keys 
                        if testcase_no in self.preproc.trace_data.keys() and 
                        p_id in self.preproc.trace_data[testcase_no].keys()]
        p_id_2 = select_dict[testcase_no] if select_dict else \
                    Randoms.choice(candidates) if candidates else \
                    Randoms.choice(populations_keys)
        
        mod = 'crossover' if select_dict else \
                'mutation' if not failed_tcs else \
                Randoms.choice(['crossover', 'mutation'])

        return p_id_2, testcase_no, mod

    def modification(self, p_id_1:str, p_id_2:str, testcase_no:int, mod:str) -> str:
        parent1, test_hist1, vari_hist1, trace_hist1 = self.preproc.run_data[p_id_1]
        parent2, test_hist2, vari_hist2, trace_hist2 = self.preproc.run_data[p_id_2]
        tree1 = ast.parse(parent1)
        tree2 = ast.parse(parent2)

        logging.debug(f'# {p_id_1}\n{parent1}\n')
        logging.debug(f'# {p_id_2}\n{parent2}\n')
        logging.debug(f'# Operator: {mod}')

        tree2 = self.swt_variables(tree1, tree2, vari_hist1, vari_hist2)
        
        if mod == 'crossover':
            child = self.crossover(tree1, tree2, trace_hist1[testcase_no], trace_hist2[testcase_no])
        elif mod == 'mutation':
            child = self.mutation(tree1, test_hist1, trace_hist1, tree2)
        
        return child
    
    def swt_variables(self, tree1, tree2, vari_hist1, vari_hist2):
        # Switch variables
        var_map = VariableMap(self.tester.get_tc_no_list()).run(tree1, vari_hist1, tree2, vari_hist2)
        tree2 = SWTVariables(var_map).visit(tree2)
        return tree2
    
    def crossover(self, tree1, tree2, traces1, traces2):
        # Crossover
        node_map = NodeMap.run(tree1, traces1, tree2, traces2)
        child = Fixer(node_map).run(tree1)
        return regularize(child)

    def mutation(self, tree1, test_hist1, trace_hist1, tree2):
        # Mutation
        node_map1 = NodeMap.get_line_node_map(tree1)
        
        # With FL
        # fl = FaultLocalization()
        # suspiciousness = fl.run_core(ast.unparse(tree1), test_hist1, trace_hist1, formula='jaccard')
        # lineno = fl.get_nth_fl(suspiciousness, n=1)
        # node1 = node_map1[lineno]
        # name1 = node1.__class__.__name__
	
        # Without FL
        node_list1 = list(node_map1.values())
        node1 = Randoms.choice(node_list1)
        name1 = node1.__class__.__name__

        node_map2 = NodeMap.get_line_node_map(tree2)
        node_list2 = [node2 for node2 in node_map2.values() if node2.__class__.__name__ == name1]
        node2 = Randoms.choice(node_list2) if node_list2 else None
        
        child = Fixer({node1:node2}).run(tree1)
        return regularize(child)

    def fitness(self, p_id:str, code:str) -> float:
        child = code
        self.preproc.core_procs(p_id, code)
        test_hist = self.preproc.run_data[p_id][1]
        passed, failed = self.tester.split_test_hist(test_hist)
        score = len(passed) / len(test_hist)

        origin_p_id, generation = p_id.rsplit('_', 1)
        if score == 1: self.solutions.setdefault(origin_p_id, {})[int(generation)] = code
        return score, child
    

    def run(self, programs:dict, pop_size:int=2, generations:int=50):
        populations = self.population(pop_size, programs)
        for generation in tqdm(range(1, generations+1), desc='Generation'):
            logging.debug(f'# Generation: {generation}')
            descendant = {}

            for p_id_1 in tqdm(populations.keys(), total=len(populations), desc='pop_size', leave=False):
                origin_p_id = p_id_1.rsplit("_", 1)[0]
                new_p_id = f'{origin_p_id}_{generation}'
                p_id_2, testcase_no, mod = self.selection(p_id_1, populations)
                child = self.modification(p_id_1, p_id_2, testcase_no, mod)
                score = self.fitness(new_p_id, child)
                descendant[new_p_id] = child

                logging.debug(f'# Child: {new_p_id}\n{child}\n')
                logging.debug(f'# Score: {score}\n\n')

            # Delete data of previous generation
            for p_id in populations.keys():
                del self.preproc.run_data[p_id]
            self.preproc.trace_data = {k: 
                                       {i: j 
                                        for i, j in v.items() 
                                        if i not in populations.keys()} 
                                        for k, v in self.preproc.trace_data.items()}
            
            populations = descendant
        
        return self.solutions