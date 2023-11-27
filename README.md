# FeedDive:Automated Feedback Generation for Programming Assignments through Diversifications

## Abstract

Automated Feedback Generation (AFG) technique repair students wrong programs and provides them as feedback. AFG techniques generate feedback of wrong programs by using correct programs. Therefore the performance of AFG techniques are depends on the diversity of correct programs. However, in small programming classes or new Online Judge problems, the diversity of correct programs may be lacking, which leads to poor performance of AFG. To solve these problems, we propose FeedDive, which provides diverse feedback. Our key idea is generating diverse feedback without correct programs. To evaluate FeedDive, we used the dataset from Refactory, which is a real-world student programming assignment. FeedDive generated 5970 diverse correct programs without correct programs and we also generated feedback for 73\% of wrong programs. By generating a diversity of correct programs, we were able to provide an average of 3 feedbacks for one wrong program. Therefore, we expect that FeedDive can improve students  programming skills by providing diversity of solutions.

## Dataset

We use dataset of Refactory. See the [ASE-2019 Refactory paper](https://ieeexplore.ieee.org/abstract/document/8952522). for more details.

data.pkl : The original dataset.  
preproc.pkl : Preprocessed dataset  
refactor_sample_100_0.pickle : Refactored Correct programs for 1 reference program by Refactory  
refactory_online.csv : Result of Refactory executed with 1 correct program(reference.py)  

```
|-data
    |-question_xxx
    |    |-data.pkl
    |    |-preproc.pkl
    |    |-refactor_sample_100_0.pickle
    |    |-refactory_online.csv
    |-...
```

## Setup

For reproduction of performance, be sure to experiment in the same environment. This is because the random seed value varies depending on the OS.

`python >= 3.11`

`OS = Mac`

#### Extract Dataset

```
unzip data.zip
```

#### Install library

```
pip install -r requirements.txt
```

## How to Run

Reproduction of Results with best random seed

```
python run.py -d data/question_1 -b
```

### Command line arguments

- `-d` flag specifies the path of data directory
- `-t` flag specifies the timeout for test case validation
- `-g` flag specifies the number of generations of Genetic Programming
- `-s` flag specifies the number of random seed
- `-b` flag specifies the best seed value to reproduce the paper's experimental results
- `-a` flag specifies the approach, choose feeddive or assignmentmender. The default is feeddive.
