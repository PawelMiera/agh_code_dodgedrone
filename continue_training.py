#!/usr/bin/env python3
import argparse
import math
#
import os
from ctypes import Union

import numpy as np
import torch
from flightgym import VisionEnv_v1
from ruamel.yaml import YAML, RoundTripDumper, dump
from stable_baselines3.common.utils import get_device
from stable_baselines3.ppo.policies import MlpPolicy

from rpg_baselines.torch.common.ppo import PPO
from rpg_baselines.torch.envs import vec_env_wrapper as wrapper
from rpg_baselines.torch.common.util import test_policy
from typing import Any, Callable, Dict, Optional, Type, Union



def configure_random_seed(seed, env=None):
    if env is not None:
        env.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def main():
    random_seed = False
    render = False
    policy_path = 'saved/PPO_89'
    policy_number = 300

    model_path = os.path.join(policy_path, os.path.join("Model", 'model_{:05d}'.format(policy_number)))

    flightmare_path = "/home/pawel/agile_flight/flightmare"

    cfg = YAML().load(open(policy_path + "/config.yaml"))

    if render:
        cfg["unity"]["render"] = "yes"

    train_env = VisionEnv_v1(dump(cfg, Dumper=RoundTripDumper), False)
    train_env = wrapper.FlightEnvVec(train_env)

    old_num_envs = cfg["simulation"]["num_envs"]
    cfg["simulation"]["num_envs"] = 1
    eval_env = wrapper.FlightEnvVec(VisionEnv_v1(dump(cfg, Dumper=RoundTripDumper), False))
    cfg["simulation"]["num_envs"] = old_num_envs

    rsg_root = os.path.dirname(os.path.abspath(__file__))
    log_dir = rsg_root + "/saved"
    os.makedirs(log_dir, exist_ok=True)

    #weight_path = os.path.join(policy_path, os.path.join("Policy", 'iter_{:05d}.pth'.format(policy_number)))

    env_rms_path = os.path.join(policy_path, os.path.join("RMS", 'iter_{:05d}.npz'.format(policy_number)))

    eval_env.load_rms(env_rms_path)
    train_env.load_rms(env_rms_path)

    device = get_device("auto")
    #saved_variables = torch.load(weight_path, map_location=device)
    # Create policy object
    #policy = MlpPolicy(**saved_variables["data"])

    # Load weights
    #policy.load_state_dict(saved_variables["state_dict"], strict=False)
    #policy.to(device)

    print("loading model")

    model = PPO.load(model_path)

    model.set_env(train_env)
    model.eval_env = eval_env

    """model = PPO(
        tensorboard_log=log_dir,
        policy=Union["dsads", policy],
        env=train_env,
        eval_env=eval_env,
        use_tanh_act=True,
        gae_lambda=0.95,
        gamma=0.99,
        n_steps=200,
        ent_coef=0.0,
        vf_coef=0.5,
        max_grad_norm=0.5,
        batch_size=40000,
        clip_range=0.2,
        use_sde=False,  # don't use (gSDE), doesn't work
        env_cfg=cfg,
        verbose=1,
        n_epochs=160,
    )"""

    model.learn(total_timesteps=int(1 * 1e8), log_interval=(10, 50))



if __name__ == "__main__":
    main()
