# Shell Dictionary

Simple online dictionary that operates in a shell and shows word forms,
meanings, synonyms, and usage examples. Outputs this information by making
requests to https://www.macmillandictionary.com and
https://context.reverso.net. Written in pure Python🐍

Thinking on whether to link tma and memo projects..


## Installation

1. Clone the repo to a folder of your choice and cd into it.

```bash
git clone https://github.com/lukoshkin/tma.git ~/Workspace/tma
cd ~/Workspace/tma
```

2. Make a python environment with conda, venv, or similar tools.

```bash
## you can name it memo or tma, for example
conda create -n tma python=3.10
```

Install dependencies.

```bash
pip install -r requirements.txt
```

Add an alias to your bash or zsh rc-file. Use the names of folder and env you
used in the first and second step, respectively. (Here I show how to do it for
`bash + conda` configuration.)


```bash
echo 'alias tt="${CONDA_PREFIX_1:-$CONDA_PREFIX}/envs/tma ~/Workspace/tma/api.py"' >> ~/.bashrc

```

## Usage

⚙️  Customization is available via `config.yaml`.


| non-interactive <br> `tt perforation` | interactive <br> `tt`  <br> succint (deliberate mistake) |
|:-------------------------------------:|:--------------------------------------------------------:|
| <img src="https://github.com/lukoshkin/tma/blob/master/png/usage-1.png" width="400" height="350"> | <img src="https://github.com/lukoshkin/tma/blob/master/png/usage-2.png" width="400" height="350"> |

<!--
| ![](png/usage-1.png =400x350) | ![](png/usage-2.png =400x350) |
-->
