from ..utils import regularize, get_stmt_list
from .tester import Tester
from ..transform import NodeParser

class FaultLocalization:
    def __init__(self, success:str='Success'):
        self.__success = success

    def get_nth_fl(self, suspiciousness:dict, n:int=1):
        rankings = self.sort(suspiciousness)
        return list(rankings.keys())[n-1]

    def sort(self, suspiciousness:dict):
        return dict(sorted(suspiciousness.items(), key=lambda x:x[1], reverse=True))

    def trantula(self, code:str, test_hist:dict, trace_hist:dict) -> dict:
        total_pass = 0
        total_fail = 0
        pass_cnt_dict = {}
        fail_cnt_dict = {}

        code = regularize(code)
        stmt_list = get_stmt_list(code)
        for lineno in range(len(stmt_list)):
            pass_cnt_dict[lineno] = 0
            fail_cnt_dict[lineno] = 0

        for testcase_no, status in test_hist.items():
            for lineno in set(trace_hist[testcase_no]):
                if status != self.__success:
                    total_fail += 1
                    fail_cnt_dict[lineno] += 1
                else:
                    total_pass += 1
                    pass_cnt_dict[lineno] += 1
        
        NodeParser.run(code)
        line_node_map = NodeParser.line_node_map
        suspiciousness = {}
        for lineno in range(len(stmt_list)):
            if lineno not in line_node_map.keys(): continue
            pass_cnt = pass_cnt_dict[lineno]
            fail_cnt = fail_cnt_dict[lineno]
            score = 0
            try: score = round((fail_cnt / total_fail) / ((fail_cnt / total_fail) + (pass_cnt / total_pass)), 1)
            except ZeroDivisionError:
                if fail_cnt > 0 and pass_cnt == 0:
                    score = 1
            suspiciousness[lineno] = score
        
        return suspiciousness
    
    def jaccard(self, code:str, test_hist:dict, trace_hist:dict) -> dict:
        total_fail = 0
        exec_cnt_dict = {}
        fail_cnt_dict = {}

        code = regularize(code)
        stmt_list = get_stmt_list(code)
        for lineno in range(len(stmt_list)):
            exec_cnt_dict[lineno] = 0
            fail_cnt_dict[lineno] = 0

        for testcase_no, status in test_hist.items():
            if status != self.__success:
                total_fail += 1
            for lineno in set(trace_hist[testcase_no]):
                exec_cnt_dict[lineno] += 1
                if status != self.__success:
                    fail_cnt_dict[lineno] += 1
        
        NodeParser.run(code)
        line_node_map = NodeParser.line_node_map
        suspiciousness = {}
        for lineno in range(len(stmt_list)):
            if lineno not in line_node_map.keys(): continue
            exec_cnt = exec_cnt_dict[lineno]
            fail_cnt = fail_cnt_dict[lineno]
            score = 0
            try: score = round((fail_cnt / (exec_cnt + (total_fail - fail_cnt))), 1)
            except ZeroDivisionError:
                if fail_cnt > 0 and exec_cnt == 0:
                    score = 1
            suspiciousness[lineno] = score
        
        return suspiciousness
    
    def run_core(self, code:str, test_hist:dict, trace_hist:dict, formula:str="jaccard") -> dict:
        if formula == "trantula":
            suspiciousness = self.trantula(code, test_hist, trace_hist)
        elif formula == "jaccard":
            suspiciousness = self.jaccard(code, test_hist, trace_hist)
        return suspiciousness
    
    def run(self, code:str, tester:Tester, formula:str="jaccard") -> dict:
        test_hist, _, trace_hist = tester.trace(code)
        suspiciousness = self.run_core(code, test_hist, trace_hist, formula)
        return suspiciousness