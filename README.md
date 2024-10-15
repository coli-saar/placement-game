🚧  Under construction 🚧

(*The repo is being updated.*)

# A Dialogue Game for Eliciting Balanced Collaboration

This is the repository containing the crowdsourced data of pairs playing the 2D object placement game we developed, and the game itself, as detailed in our paper ["A Dialogue Game for Eliciting Balanced Collaboration"]((https://aclanthology.org/2024.sigdial-1.41/)) ([**Paper web page**](https://coli-saar.github.io/balancedcollab)). 

#### IMPORTANT!

**The raw jsonl files can be found in the [```/crowdsourced_data```](https://github.com/coli-saar/placement-game/tree/main/crowdsourced_data) subdirectory, while the code and deployment instructions can be found in the [```/code```](https://github.com/coli-saar/placement-game/tree/main/code) subdirectory.**  The ```/images``` subdirectory contains the front-end elements loaded into the game.

## Table of contnets:

1. [Project description](#project-description) 
2. [Repository structure](#repository-structure)
3. [Contact](#contact)
4. [Licence and use](#licence-and-use)


## Project description

Collaboration is an integral part of human dialogue. Typical task-oriented dialogue games assign asymmetric roles to the participants, which limits their ability to elicit naturalistic role-taking in collaboration and its negotiation. We present a novel and simple online setup that favors balanced collaboration: a two-player 2D object placement game in which the players must negotiate the goal state themselves. We show empirically that human players exhibit a variety of role distributions, and that balanced collaboration improves task performance. We also present an LLM-based baseline agent which demonstrates that automatic playing of our game is an interesting challenge for artificial systems.

## Repository structure

        .
        └── code
            └── placement 
                └── [scripts for deploying the game]
            ├── README.md
            └── requirements.txt
        └── crowdsourced_data
            └── data
                └── [raw .jsonl files]
            ├── README.md
            └── strategy_breakdown.json
        └── images
            └── [front-end .png elements]

## Contact

For any questions about the game or dataset, please contact **Isidora Jeknic** (email adress: jeknic [at] lst [dot] uni [dash] saarland [dot] de).


## Licence and use

If you use the dataset or game for your research, please cite our resources in the following way:

        @inproceedings{jeknic-etal-2024-dialogue,
            title = "A Dialogue Game for Eliciting Balanced Collaboration",
            author = "Jeknic, Isidora  and
            Schlangen, David  and
            Koller, Alexander",
            editor = "Kawahara, Tatsuya  and
            Demberg, Vera  and
            Ultes, Stefan  and
            Inoue, Koji  and
            Mehri, Shikib  and
            Howcroft, David  and
            Komatani, Kazunori",
            booktitle = "Proceedings of the 25th Annual Meeting of the Special Interest Group on Discourse and Dialogue",
            month = sep,
            year = "2024",
            address = "Kyoto, Japan",
            publisher = "Association for Computational Linguistics",
            url = "https://aclanthology.org/2024.sigdial-1.41",
            doi = "10.18653/v1/2024.sigdial-1.41",
            pages = "477--489",
            abstract = "Collaboration is an integral part of human dialogue. Typical task-oriented dialogue games assign asymmetric roles to the participants, which limits their ability to elicit naturalistic role-taking in collaboration and its negotiation. We present a novel and simple online setup that favors balanced collaboration: a two-player 2D object placement game in which the players must negotiate the goal state themselves. We show empirically that human players exhibit a variety of role distributions, and that balanced collaboration improves task performance. We also present an LLM-based baseline agent which demonstrates that automatic playing of our game is an interesting challenge for artificial systems.",
        }


