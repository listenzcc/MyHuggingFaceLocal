"""
File: img2img.py
Author: Chuncheng Zhang
Date: 2023-04-18
Copyright & Email: chuncheng.zhang@ia.ac.cn

Functions:
    1. Pending
    2. Pending
    3. Pending
    4. Pending
    5. Pending
"""


# %% ---- 2023-04-18 ------------------------
# Pending
import argparse
import os
import sys
import glob
import PIL
import torch
import numpy as np
from omegaconf import OmegaConf
from PIL import Image
from tqdm import tqdm, trange
from itertools import islice
from einops import rearrange, repeat
from torchvision.utils import make_grid
from torch import autocast
from contextlib import nullcontext
import time
from pytorch_lightning import seed_everything

from ldm.util import instantiate_from_config
from ldm.models.diffusion.ddim import DDIMSampler
from ldm.models.diffusion.plms import PLMSSampler

# %%
import json
import random
from pathlib import Path

# %% ---- 2023-04-18 ------------------------
# Pending


class Option(object):
    def __init__(self):
        self.prompt = ''
        self.init_img = ''
        self.outdir = 'outputs/img2img/'
        self.skip_grid = False
        self.skip_save = False
        self.ddim_steps = 50
        self.plms = False
        self.fixed_code = False
        self.ddim_eta = 0.0
        self.n_iter = 2
        self.C = 4
        self.f = 8
        self.n_samples = 3
        self.n_rows = 3
        self.scale = 5.0
        self.strength = 0.75
        self.from_file = ''
        self.config = 'configs/stable-diffusion/v1-inference.yaml'
        self.ckpt = "models/ldm/stable-diffusion-v1/model.ckpt"
        self.seed = 42
        self.precision = 'autocast'  # ['full', 'autocast']

        self.update_outdir()

    def update_outdir(self):
        self.outdir = 'outputs/img2img/{}-{:.8f}'.format(
            time.strftime('%Y-%m-%d-%H-%M-%S'), random.random())


opt = Option()
opt_img2img = opt
print(opt.__dict__)

# %%
device = torch.device(
    "cuda") if torch.cuda.is_available() else torch.device("cpu")

# %% ---- 2023-04-18 ------------------------
# Pending


def chunk(it, size):
    it = iter(it)
    return iter(lambda: tuple(islice(it, size)), ())


def load_model_from_config(config, ckpt, verbose=False):
    print(f"Loading model from {ckpt}")
    pl_sd = torch.load(ckpt, map_location="cpu")
    if "global_step" in pl_sd:
        print(f"Global Step: {pl_sd['global_step']}")
    sd = pl_sd["state_dict"]
    model = instantiate_from_config(config.model)
    m, u = model.load_state_dict(sd, strict=False)
    if len(m) > 0 and verbose:
        print("missing keys:")
        print(m)
    if len(u) > 0 and verbose:
        print("unexpected keys:")
        print(u)

    model.cuda()
    model.eval()
    return model


def load_img(path):
    image = Image.open(path).convert("RGB")
    w, h = image.size
    print(f"loaded input image of size ({w}, {h}) from {path}")
    # resize to integer multiple of 32
    w, h = map(lambda x: x - x % 64, (w, h))
    image = image.resize((w, h), resample=PIL.Image.LANCZOS)
    image = np.array(image).astype(np.float32) / 255.0
    image = image[None].transpose(0, 3, 1, 2)
    image = torch.from_numpy(image)
    return 2.*image - 1.


# %% ---- 2023-04-18 ------------------------
# Pending
config = OmegaConf.load(f"{opt.config}")
model = load_model_from_config(config, f"{opt.ckpt}")
model = model.to(device)

if opt.plms:
    raise NotImplementedError("PLMS sampler not (yet) supported")
    sampler = PLMSSampler(model)
else:
    sampler = DDIMSampler(model)


# %% ---- 2023-04-18 ------------------------
# Pending
def perform_img2img(opt):
    '''
    Perform img2img operation.

    Setup the opt is required,
    - opt.prompt = 'bala bala'
    - opt.init_img = (str) image path
    '''

    opt.update_outdir()
    print(opt.__dict__)

    outpath = opt.outdir

    os.makedirs(outpath, exist_ok=True)
    outpath = outpath

    json.dump(opt.__dict__, open(Path(outpath, 'setup.json'), 'w'))

    batch_size = opt.n_samples
    n_rows = opt.n_rows if opt.n_rows > 0 else batch_size
    if not opt.from_file:
        prompt = opt.prompt
        assert prompt is not None
        data = [batch_size * [prompt]]

    else:
        print(f"reading prompts from {opt.from_file}")
        with open(opt.from_file, "r") as f:
            data = f.read().splitlines()
            data = list(chunk(data, batch_size))

    sample_path = os.path.join(outpath, "samples")
    os.makedirs(sample_path, exist_ok=True)
    base_count = len(os.listdir(sample_path))
    grid_count = len(os.listdir(outpath)) - 1

    assert os.path.isfile(opt.init_img)
    init_image = load_img(opt.init_img).to(device)
    init_image = repeat(init_image, '1 ... -> b ...', b=batch_size)
    init_latent = model.get_first_stage_encoding(
        model.encode_first_stage(init_image))  # move to latent space

    sampler.make_schedule(ddim_num_steps=opt.ddim_steps,
                          ddim_eta=opt.ddim_eta, verbose=False)

    assert 0. <= opt.strength <= 1., 'can only work with strength in [0.0, 1.0]'
    t_enc = int(opt.strength * opt.ddim_steps)
    print(f"target t_enc is {t_enc} steps")

    precision_scope = autocast if opt.precision == "autocast" else nullcontext

    img_path_list = []
    with torch.no_grad():
        with precision_scope("cuda"):
            with model.ema_scope():
                tic = time.time()
                all_samples = list()
                for n in trange(opt.n_iter, desc="Sampling"):
                    for prompts in tqdm(data, desc="data"):
                        uc = None
                        if opt.scale != 1.0:
                            uc = model.get_learned_conditioning(
                                batch_size * [""])
                        if isinstance(prompts, tuple):
                            prompts = list(prompts)
                        c = model.get_learned_conditioning(prompts)

                        # encode (scaled latent)
                        z_enc = sampler.stochastic_encode(
                            init_latent, torch.tensor([t_enc]*batch_size).to(device))
                        # decode it
                        samples = sampler.decode(z_enc, c, t_enc, unconditional_guidance_scale=opt.scale,
                                                 unconditional_conditioning=uc,)

                        x_samples = model.decode_first_stage(samples)
                        x_samples = torch.clamp(
                            (x_samples + 1.0) / 2.0, min=0.0, max=1.0)

                        if not opt.skip_save:
                            for x_sample in x_samples:
                                x_sample = 255. * \
                                    rearrange(x_sample.cpu().numpy(),
                                              'c h w -> h w c')

                                latest_img_path = os.path.join(
                                    sample_path, f"{base_count:05}.png")
                                img_path_list.append(latest_img_path)
                                Image.fromarray(x_sample.astype(
                                    np.uint8)).save(latest_img_path)

                                base_count += 1
                        all_samples.append(x_samples)

                if not opt.skip_grid:
                    # additionally, save as grid
                    grid = torch.stack(all_samples, 0)
                    grid = rearrange(grid, 'n b c h w -> (n b) c h w')
                    grid = make_grid(grid, nrow=n_rows)

                    # to image
                    grid = 255. * \
                        rearrange(grid, 'c h w -> h w c').cpu().numpy()
                    Image.fromarray(grid.astype(np.uint8)).save(
                        os.path.join(outpath, f'grid-{grid_count:04}.png'))
                    grid_count += 1

                toc = time.time()

                print('The img2img operation took {} seconds'.format(toc - tic))

    print(f"Your samples are ready and waiting for you here: \n{outpath} \n"
          f" \nEnjoy.")

    return img_path_list

# %%
