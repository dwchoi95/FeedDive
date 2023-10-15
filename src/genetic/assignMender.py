import ast
from tqdm import tqdm
import logging

from ..execution import Preprocess, FaultLocalization
from ..transform import AMMutator
from ..utils import regularize, Randoms



class AssignMender:
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
    
    def mutation(self, parent:str, lineno:int, vari_hist) -> str:
        tree = ast.parse(parent)
        amm = AMMutator(lineno, vari_hist)
        child = amm.run(tree)
        return regularize(child)

    def fitness(self, p_id:str, code:str) -> float:
        self.preproc.core_procs(p_id, code)
        test_hist = self.preproc.run_data[p_id][1]
        passed, failed = self.tester.split_test_hist(test_hist)
        score = len(passed) / len(test_hist)

        origin_p_id, generation = p_id.rsplit('_', 1)
        if score == 1: self.solutions.setdefault(origin_p_id, {})[int(generation)] = code
        return score

    def run(self, programs:dict, pop_size:int=2, generations:int=50):
        populations = self.population(pop_size, programs)
        for p_id in tqdm(populations.keys(), total=len(populations), desc='AssignMender'):
            parent, test_hist, vari_hist, trace_hist = self.preproc.run_data[p_id]
            fl = FaultLocalization()
            suspiciousness = fl.run_core(parent, test_hist, trace_hist, formula='jaccard')

            logging.debug(f'# Parent\n{parent}\n\n')

            origin_p_id = p_id.rsplit("_", 1)[0]
            for lineno in suspiciousness.keys():
                try:
                    child = self.mutation(parent, lineno, vari_hist)
                    new_p_id = f'{origin_p_id}_{lineno+1}'
                    score = self.fitness(new_p_id, child)
                
                    logging.debug(f'# Child: {new_p_id}\n{child}\n\n')
                    logging.debug(f'# Score: {score}\n')
                except: continue
            
        return self.solutions
    