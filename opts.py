import argparse


def parse_opts():
    parser = argparse.ArgumentParser()
    arguments = {
        'coefficients': [
            dict(name='--lambda_0',
                 default='0.5',
                 type=float,
                 help='Penalty Coefficient that Controls the Penalty Extent in PCCE'),
        ],
        'paths': [
            dict(name='--resnet101_pretrained',
               #   default='/home/jjr/srtp/VAANet-master/data/resnet-101-kinetics.pth',
                 default='/data/jjr/dataset/resnet-101-kinetics.pth',
                 type=str,
                 help='Global path of pretrained 3d resnet101 model (.pth)'),
            dict(name='--root_path',
               #   default="/home/ubuntu/private/project/vaanet",
                 default="/home/jjr/srtp/VAANet-master",
                 type=str,
                 help='Global path of root directory'),
            dict(name="--video_path",
               #   default="VideoEmotion8--imgs",
                 default="/data/jjr/VideoEmotion8--imgs",
                 type=str,
                 help='Local path of videos', ),
            dict(name="--annotation_path",
               #   default='ve8_01.json',
                 default='/data/jjr/ve8_01.json',
                 type=str,
                 help='Local path of annotation file'),
            dict(name="--result_path",
               #   default='results',
                 default='/data/jjr/results',
                 type=str,
                 help="Local path of result directory"),
            dict(name='--expr_name',
                 type=str,
                 default=''),
            dict(name='--audio_path',
                 type=str,
               #   default='VideoEmotion8--mp3',
                 default='/data/jjr/VideoEmotion8--mp3',
                 help='Local path of audios')

        ],
        'core': [
            dict(name='--batch_size',
                 default=8,
                 type=int,
                 help='Batch Size'),
            dict(name='--snippet_duration',
                 default=16,
                 type=int),
            dict(name='--sample_size',
                 default=112,
                 type=int,
                 help='Heights and width of inputs'),
            dict(name='--n_classes',
                 default=8,
                 type=int,
                 help='Number of classes'),
            dict(name='--seq_len',
                 default=12,
                 type=int),
            dict(name='--loss_func',
                 default='pcce_ve8',
                 type=str,
                 help='ce | pcce_ve8'),
            dict(name='--learning_rate',
                 default=1e-4,
                 type=float,
                 help='Initial learning rate', ),
            dict(name='--weight_decay',
                 default=0.0,
                 type=float,
                 help='Weight Decay'),
            dict(name='--fps',
                 default=30,
                 type=int,
                 help='fps')

        ],
        'network': [
            {
                'name': '--audio_embed_size',
                'default': 256,
                'type': int,
            },
            {
                'name': '--audio_n_segments',
                'default': 16,
                'type': int,
            }
        ],

        'common': [
            dict(name='--dataset',
                 type=str,
                 default='ve8',
                 ),
            dict(name='--use_cuda',
                 action='store_true',
                 default=False,
                 help='only cuda supported!'
                 ),
            dict(name='--debug',
                 default=False,
                 action='store_true'),
            dict(name='--dl',
                 action='store_true',
                 default=False,
                 help='drop last'),
            dict(
                name='--n_threads',
                default=0,
                type=int,
                help='Number of threads for multi-thread loading',
            ),
            dict(
                name='--n_epochs',
                default=100,
                type=int,
                help='Number of total epochs to run',
            )
        ]
    }

    for group in arguments.values():
        for argument in group:
            name = argument['name']
            del argument['name']
            parser.add_argument(name, **argument)

    args = parser.parse_args()
    return args
