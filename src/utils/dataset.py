import os
import pickle


class Dataset:
    def __init__(self):
        self.testcases = []
        self.wrong_progs = {}
        self.refer_progs = {}
        self.difficulty = ''

    def read_dataset(self, ques_dir_path:str):
        ans_dir_path = os.path.join(ques_dir_path, 'ans')
        wrong_dir_path = os.path.join(ques_dir_path, 'code', 'wrong')
        refer_dir_path = os.path.join(ques_dir_path, 'code', 'correct')

        testcases = self.get_dataset(ans_dir_path, ".txt")
        self.seperate_tc(testcases)

        front_code = ''
        front_code_path = os.path.join(ques_dir_path, 'code', 'global.py')
        if os.path.isfile(front_code_path):
            front_code = open(front_code_path).read()

        end_code = ''
        end_code_path = os.path.join(ques_dir_path, 'code', 'global_append.py')
        if os.path.isfile(end_code_path):
            end_code = open(end_code_path).read()
        
        self.wrong_progs = self.get_dataset(wrong_dir_path, '.py')
        self.wrong_progs = self.append_skeleton_code(self.wrong_progs, front_code, end_code)
        self.refer_progs = self.get_dataset(refer_dir_path, '.py')
        self.refer_progs = self.append_skeleton_code(self.refer_progs, front_code, end_code)
    
    def append_skeleton_code(self, programs:dict, front_code:str='', end_code:str='') -> dict:
        if not front_code and not end_code:
            return programs
        return {file:f'{front_code}\n\n{code}\n\n{end_code}' for file, code in programs.items()}

    def get_dataset(self, dir_path:str, extension:str) -> dict:
        data_dict = {}
        for (file_path, dir, files) in os.walk(dir_path):
            for file in files:
                filename, extension_ = os.path.splitext(file)
                if extension_ == extension:
                    path = os.path.join(file_path, file)
                    data = open(path).read().strip()
                    if extension == '.txt':
                        tc_id = int(filename.split('_')[1])
                        in_out = 'input'
                        if 'output' in filename:
                            in_out = 'output'
                        if in_out not in data_dict.keys():
                            data_dict[in_out] = {}
                        data_dict[in_out][tc_id] = data
                    else:
                        data_dict[filename] = data
        data_dict = dict(sorted(data_dict.items()))
        return data_dict
    
    def seperate_tc(self, testcases:dict[str,dict]):
        input_tc_list = testcases['input']
        output_tc_list = testcases['output']
        for testcase_no, input_tc in input_tc_list.items():
            self.testcases.append(
                {
                    'testcase_no': int(testcase_no),
                    'input_tc': input_tc,
                    'output_tc': output_tc_list[testcase_no]
                }
            )
        

            