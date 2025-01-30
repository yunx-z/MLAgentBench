import os

# TODO: automatically read from base_exp idea_evals.json

ALL_BASE_RUNTIME = {
        "base-competition" : {
            "dev" : 100,
            "test" : 100,
            },
        "llm-merging" : {
            "dev" : 3338.01,
            "test" : 2428.07,
            },
        "backdoor-trigger-recovery" : {
            "dev" : 597.55,
            "test" : 498.13,
            "debug" : 400,
            },
        "perception_temporal_action_loc" : {
            "dev" : 1025.33,
            "test" : 313.69,
            "debug" : 100,
        },
        "machine_unlearning":{
            "dev": 517.7307,
            "test": 233, # random number, ignore
            "debug": 233,
        },
        # TODO: add the runtime (unit in seconds) of your new tasks here.
        "meta-learning": {
            "val" : 16.12773323059082,
            "test" : 27.63893985748291
        },
        "erasing_invisible_watermarks": {
            "beige": {
                "stegastamp": {
                    "dev": 27,     
                    "test": 120    
                },
                "treering": {
                    "dev": 29,     
                    "test": 128    
                }
            },
            "black": {
                "dev": 56,         
                "test": 223       
            }
        }
    }

ALL_BASE_PERFORMANCE = {
        "base-competition" : {
            "dev" : 0.5,
            "test" : 0.5,
            },
        "llm-merging" : {
            # range 0-1
            "dev" : 0.727,
            "test" : 0.493,
            },
        "backdoor-trigger-recovery" : {
            # range 0-100
            "dev" : 3.758,
            "test" : 9.369,
            "debug" : 2,
            },
        "perception_temporal_action_loc" : {
            # range 0-1
            "dev" : 0.2359,
            "test" : 0.1234,
            "debug" : 0.2
        },
         "machine_unlearning":{
             # range 0-1
            "dev": 0.0542,
            "test": 0.0611,
            "debug": 233,
        },
        # TODO: add the baseline performance of your new tasks here.
        "meta-learning": {
            # range 0-1
            "val" : 0.1886189034134081,
            "test" : 0.3657513612634356
        },
        "erasing_invisible_watermarks": {
            "beige": {
                "stegastamp": {
                    "dev": 0.1700,   # Overall Score
                    "test": 0.1774   # Overall Score
                },
                "treering": {
                    "dev": 0.2494,   # Overall Score
                    "test": 0.2486   # Overall Score
                }
            },
            "black": {
                "dev": 0.2061,     # Overall Score
                "test": 0.1935     # Overall Score
            }
        }
    }



MLR_BENCH_DIR = os.getenv("MLR_BENCH_DIR", "~/MLAgentBench") # absolute path is preferred
