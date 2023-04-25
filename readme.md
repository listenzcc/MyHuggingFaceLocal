# OpenAI 模型的本地化笔记

HuggingFace 是著名的 AI 模型社区，提供了大量好玩的开源模型。于是我抱着学习和未雨绸缪的心态将它部署在了本地服务器上，并且提供了一个好用的网页控制器，本笔记对这一过程进行了记录和说明，开源代码可见我的 Github 笔记本。

[https://github.com/listenzcc/MyHuggingFaceLocal](https://github.com/listenzcc/MyHuggingFaceLocal)

---
- [OpenAI 模型的本地化笔记](#openai-模型的本地化笔记)
  - [模型出处](#模型出处)
  - [模型部署](#模型部署)
  - [模型可用性](#模型可用性)


## 模型出处

HuggingFace 是著名的 AI 模型社区，提供了大量好玩的开源模型。于是我抱着学习和未雨绸缪的心态将它部署在了本地服务器上，初步部署的模型为 AI 画图的 stable-diffusion-v1-5 模型，采用的功能为其中的 txt2img 和 img2img 两个功能。

[runwayml/stable-diffusion-v1-5 · Hugging Face](https://huggingface.co/runwayml/stable-diffusion-v1-5)

## 模型部署

部署深度学习的 AI 模型最重要的是两件事情

- 一是提供模型框架，即在本地建立深度神经网络框架；
- 二是为模型提供参数，即在网络框架的每个“神经元”上赋予合适的预训练参数。

虽然官方对两个过程都进行了较为明确的方法描述，但在本地部署的过程中，除在官方教程之外，这两个事情都需要进行一些小操作，才能合理地绕开 The great wall 可能造成的小麻烦。因为我们要做的是在本地服务器上进行安装，而不方便将本地服务器暴露给梯子，因此这些小操作主要是用于应对你的电脑有梯子，但你要安装的服务器没有梯子的情况。

首先是环境的安装，pytorch 的配置可以套用官方自带的 environment.yaml 文件中对安装环境的描述。这里要采取的操作是针对 github 安装的情况。由于某些原因，这样的安装形式需要较为稳定的网络连接，但这一点往往无法满足，因此本次安装采取预先 clone + pip install 的形式，让机器“误”认为自己已经具备的 ldm 环境的安装条件，从而完成模型搭建。这一步完成后，我们即在本地建立了运行 stable-diffusion 的深度神经网络框架

```yaml
# Remove the github install,
# and clone the project into src/clip src/taming-transofmers in advance,
# of course, you should pip ./setup.py install the packages by your self.
name: ldm
channels:
  - pytorch
  - defaults
dependencies:
  - ...
  - pip:
    # - -e git+http://github.com/CompVis/taming-transformers.git@master#egg=taming-transformers
    # - -e git+http://github.com/openai/CLIP.git@main#egg=clip
```

接下来需要为模型提供预训练参数，该工作可以在梯子上下载预训练参数集来完成，虽然它比较大（经过剪枝后仍然达到了 7.2G 的规模），但部署过程相对简单，通过软链接链接到相应位置即可

```bash
$ ll stable-diffusion-v1-5/model                                                                                       [15:55:30]
total 12G
-rw-rw-r-- 1 zcc zcc 7.2G 4月  16 14:34 v1-5-pruned.ckpt
-rw-rw-r-- 1 zcc zcc 4.0G 4月  16 14:00 v1-5-pruned-emaonly.ckpt

$ ll stable-diffusion-v1-5/models/ldm/stable-diffusion-v1                                                              [15:55:39]
total 4.0K
lrwxrwxrwx 1 zcc zcc 76 4月  16 14:41 model.ckpt -> /.../v1-5-pruned.ckpt
```

## 模型可用性

为了提升模型可用性，我使用 Flask 搭建了 stable-diffusion 服务，搭建服务出于两个目的，首先，开源代码提供的样例在每次绘图时均需要进行模型载入，这个过程相当耗时。而模型载入后程序随即关闭，这导致了资源浪费；其次，开源代码提供的样例只限于命令行操作，可用性不强，也不利于历史数据追溯。

因此，在模型本地化的同时使用 Flask 搭建了 stable-diffusion 服务，提供方便的网页端操作，它的功能有三点

1. 提高了绘图效率，现在模型参数载入后在后台进行服务，这些资源在 Flask 服务结束前不会释放，从而提升单个 prompt 的绘图效率；
2. 提高查询效率，目前的版本针对 txt2img 的图像，支持对其进行历史数据查询和 prompt 还原，并且支持在已有图像上基础上重新进行 img2img 操作；
3. 使用 bootstrap 框架进行操作框架部署，增强多端适配能力。

主界面如下，可以通过 prompt 生成图像。经实验看到，该模型在生成动画场景和雕塑类美术场景方面具有优势。但人体及面部信息则漏洞百出，因为过于吓人，就不在这里放图了。

![Example-1, DC characters.](OpenAI%20%E6%A8%A1%E5%9E%8B%E7%9A%84%E6%9C%AC%E5%9C%B0%E5%8C%96%E7%AC%94%E8%AE%B0%2094a72c583343435fb618ecb3c2e1e9bb/%25E9%25A3%259E%25E4%25B9%25A620230425-161952.png)

Example-1, DC characters.

![Example-2, Mongila warrior.](OpenAI%20%E6%A8%A1%E5%9E%8B%E7%9A%84%E6%9C%AC%E5%9C%B0%E5%8C%96%E7%AC%94%E8%AE%B0%2094a72c583343435fb618ecb3c2e1e9bb/%25E9%25A3%259E%25E4%25B9%25A620230425-162017.png)

Example-2, Mongila warrior.

另外，img2img 的图像修改功能样例如下，样例是在蓝色车的基础上加一个蜘蛛侠，顺序是从左图变到右图。

![Blue truck](OpenAI%20%E6%A8%A1%E5%9E%8B%E7%9A%84%E6%9C%AC%E5%9C%B0%E5%8C%96%E7%AC%94%E8%AE%B0%2094a72c583343435fb618ecb3c2e1e9bb/000021.png)

Blue truck

![Blue truck + spider man](OpenAI%20%E6%A8%A1%E5%9E%8B%E7%9A%84%E6%9C%AC%E5%9C%B0%E5%8C%96%E7%AC%94%E8%AE%B0%2094a72c583343435fb618ecb3c2e1e9bb/00002.png)

Blue truck + spider man

```json
{
    "prompt": "A nice blue car is transforming into a truck.",
    "skip_grid": false,
    "skip_save": false,
    "ddim_steps": 50,
    "plms": false,
    "laion400m": false,
    "fixed_code": false,
    "ddim_eta": 0.0,
    "n_iter": 2,
    "H": 512,
    "W": 512,
    "C": 4,
    "f": 8,
    "n_samples": 3,
    "n_rows": 3,
    "scale": 7.5,
    "from_file": "",
    "config": "configs/stable-diffusion/v1-inference.yaml",
    "ckpt": "models/ldm/stable-diffusion-v1/model.ckpt",
    "seed": 42,
    "precision": "autocast",
    "outdir": "outputs/txt2img/2023-04-18-18-01-48-0.32806818"
}

{
    "prompt": "Add the spider-man on the right. Keep the truck unchanged.",
    "init_img": "outputs/txt2img/2023-04-18-18-01-48-0.32806818/samples/00002.png",
    "outdir": "outputs/img2img/2023-04-18-22-18-46-0.38229466",
    "skip_grid": false,
    "skip_save": false,
    "ddim_steps": 50,
    "plms": false,
    "fixed_code": false,
    "ddim_eta": 0.0,
    "n_iter": 2,
    "C": 4,
    "f": 8,
    "n_samples": 3,
    "n_rows": 3,
    "scale": 5.0,
    "strength": 0.75,
    "from_file": "",
    "config": "configs/stable-diffusion/v1-inference.yaml",
    "ckpt": "models/ldm/stable-diffusion-v1/model.ckpt",
    "seed": 42,
    "precision": "autocast"
}
```