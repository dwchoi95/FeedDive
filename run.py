import argparse
import csv
import os
import ast
import pickle

from src.genetic import FeedDive, AssignMender, Prioritization
from src.execution import Tester, Preprocess
from src.utils import Dataset, Randoms, regularize, relative_patch_size


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dataset', nargs='?', required=True,
                        help="The path of the dataset directory")
    parser.add_argument('-t', '--timeout', type=int, default=1,
                        help="Set timeout for compile program, default is 1sec")
    parser.add_argument('-g', '--generations', type=int, default=10,
                        help="Number of generations, default is 10")
    parser.add_argument('-s', '--seed', type=int, default=1,
                        help="Set start of random seed value, default is 1")
    parser.add_argument('-b', '--best_seed', action='store_true', default=False,
                        help="Set start of best seed value,")
    parser.add_argument('-a', '--approach', type=str, default="FeedDive",
                        help="The approach of the AFG")
    args = parser.parse_args()

    data_dir_path = args.dataset
    data_dir, _ = os.path.splitext(data_dir_path)
    project = os.path.basename(data_dir)
    approach = args.approach.lower()
    generations = args.generations
    logfile = os.path.join(data_dir_path, f'{approach}.log')
    csvfile = os.path.join(data_dir_path, f'{approach}.csv')


    """Settings"""
    ## Dataset
    dataset = Dataset()
    data_path = os.path.join(data_dir_path, 'data.pkl')
    with open(data_path, 'rb') as f:
        dataset = pickle.load(f)
    programs = dataset.wrong_progs
    total = len(programs)
    print(f'Wrong Programs: {total}')


    """Genetic Programming"""
    ## Preprocessing
    tester = Tester(dataset.testcases, args.timeout)
    preproc = Preprocess(tester)
    preproc.run(programs)

    ## Run Genetic Programming
    if approach == "feeddive":
        genetic = FeedDive(preproc, logfile)
        best_seed = {'question_1':100, 'question_2':73, 'question_3':26, 'question_4':22, 'question_5':21}
        seed = best_seed[project]
    elif approach == "assignmentmender":
        genetic = AssignMender(preproc, logfile)
        best_seed= {'question_1':1, 'question_2':1, 'question_3':7, 'question_4':11, 'question_5':1}
        seed = best_seed[project]
    else:
        raise Exception("Choose FeedDive or AssignmentMender as approach of AFG")
    
    ## Random seeds
    print(f'SEED: {seed}')
    Randoms.seed = seed
    
    ## Generate Feedbacks
    solutions = genetic.run(programs, pop_size=total, generations=generations)
    total_sol = sum(len(value) for value in solutions.values())
    print(f'{total_sol} Solutions are generated.')
    
    prior = Prioritization(programs)
    feedbacks = prior.run(solutions)
    print(f'{len(feedbacks)} Feedbacks are generated.')

    total_rps = 0
    success = 0
    """Save Results"""
    with open(csvfile, 'w', newline='') as f:
        wr = csv.writer(f)
        wr.writerow(['File', 'Status', 'Wrong', 'Patch(MIN)', 'Patch(First)', 'Generation(MIN)', 'Generation(First)', 'RPS'])
        for file, wrong in programs.items():
            wrong = regularize(wrong)
            if file in feedbacks.keys():
                first_gen, first_patch, min_gen, min_patch = feedbacks[file]
                rps = relative_patch_size(wrong, min_patch)
                wr.writerow([file, 'success', wrong, min_patch, first_patch, min_gen, first_gen, rps])
                total_rps += rps
                success += 1
            else:
                wr.writerow([file, 'fail', wrong, None, None, None, None, None])


    print(f'Feedback Rate: {round(success/total, 2)*100}')
    print(f'AVG RPS: {total_rps/success}')
    