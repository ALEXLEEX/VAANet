import torch
import torch.utils.data as data

from torchvision import get_image_backend

from PIL import Image

import json
import os
import functools
import librosa
import numpy as np


def load_value_file(file_path):
    with open(file_path, 'r') as input_file:
        return float(input_file.read().rstrip('\n\r'))


def load_annotation_data(data_file_path):
    with open(data_file_path, 'r') as data_file:
        return json.load(data_file)


def get_video_names_and_annotations(data, subset):
    video_names = []
    annotations = []
    for key, value in data['database'].items():
        if value['subset'] == subset:
            label = value['annotations']['label']
            video_names.append('{}/{}'.format(label, key))
            annotations.append(value['annotations'])
    return video_names, annotations


def get_class_labels(data):
    class_labels_map = {}
    index = 0
    for class_label in data['labels']:
        class_labels_map[class_label] = index
        index += 1
    return class_labels_map


def pil_loader(path):
    # open path as file to avoid ResourceWarning (https://github.com/python-pillow/Pillow/issues/835)
    with open(path, 'rb') as f:
        with Image.open(f) as img:
            return img.convert('RGB')


def accimage_loader(path):
    try:
        import accimage
        return accimage.Image(path)
    except IOError:
        # Potentially a decoding problem, fall back to PIL.Image
        return pil_loader(path)


def get_default_image_loader():
    if get_image_backend() == 'accimage':
        return accimage_loader
    else:
        return pil_loader


def video_loader(video_dir_path, frame_indices, image_loader):
    video = []
    for i in frame_indices:
        image_path = os.path.join(video_dir_path, '{:06d}.jpg'.format(i))
        assert os.path.exists(image_path), "image does not exists"
        video.append(image_loader(image_path))
    return video


def get_default_video_loader():
    image_loader = get_default_image_loader()
    return functools.partial(video_loader, image_loader=image_loader)


def preprocess_audio(audio_path):
    "Extract audio features from an audio file"
    y, sr = librosa.load(audio_path, sr=44100)
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=32)
    return mfccs

# 以上会不会有重名函数的问题
# 现在就是处理这里 把这里弄成正确输出的VA值
import json
import torch

class zjuVADataset(data.Dataset):
    def __init__(self,
                 video_path,
                 audio_path,
                 annotation_path,
                 subset,
                 fps=30,
                 spatial_transform=None,
                 temporal_transform=None,
                 target_transform=None,
                 get_loader=get_default_video_loader,
                 need_audio=True):
        # 加载标签文件 (假设是JSON格式)
        with open(annotation_path, 'r') as f:
            self.annotations = json.load(f)  # 加载整个JSON文件

        self.valence = self.annotations["Valence"]  # 获取Valence字典
        self.arousal = self.annotations["Arousal"]  # 获取Arousal字典
        
        self.data, self.class_names = make_dataset(
            video_root_path=video_path,
            annotation_path=annotation_path,
            audio_root_path=audio_path,
            subset=subset,
            fps=fps,
            need_audio=need_audio
        )

        self.spatial_transform = spatial_transform
        self.temporal_transform = temporal_transform
        self.target_transform = target_transform
        self.loader = get_loader()
        self.fps = fps
        self.ORIGINAL_FPS = 24
        self.need_audio = need_audio

    def __getitem__(self, index):
        data_item = self.data[index]
        video_path = data_item['video']
        frame_indices = data_item['frame_indices']
        snippets_frame_idx = self.temporal_transform(frame_indices)

        # 音频处理
        if self.need_audio:
            timeseries_length = 4096
            audio_path = data_item['audio']
            feature = preprocess_audio(audio_path).T
            k = timeseries_length // feature.shape[0] + 1
            feature = np.tile(feature, reps=(k, 1))
            audios = feature[:timeseries_length, :]
            audios = torch.FloatTensor(audios)
        else:
            audios = []

        # 处理视频片段
        # TODO: 检查是否存在缓存文件
        snippets = []
        for snippet_frame_idx in snippets_frame_idx:
            snippet = self.loader(video_path, snippet_frame_idx)
            snippets.append(snippet)

        self.spatial_transform.randomize_parameters()
        snippets_transformed = []
        for snippet in snippets:
            snippet = [self.spatial_transform(img) for img in snippet]
            snippet = torch.stack(snippet, 0).permute(1, 0, 2, 3)
            snippets_transformed.append(snippet)
        snippets = snippets_transformed
        snippets = torch.stack(snippets, 0)
        
        # TODO:缓存snippets，保存成pytorch的权重文件，调用torch.save()

        # 获取目标标签 (Valence and Arousal) 从JSON标签文件
        sample_id = data_item['video_id']  # 假设video_id对应SampleID
        valence_value = self.valence.get(sample_id, 0)  # 默认为0，如果SampleID没有找到
        arousal_value = self.arousal.get(sample_id, 0)  # 默认为0，如果SampleID没有找到

        va_target = torch.tensor([valence_value, arousal_value])  # 将Valence和Arousal值作为标签

        visualization_item = [data_item['video_id']]

        return snippets, va_target, audios, visualization_item

    def __len__(self):
        return len(self.data)

    
    
def make_dataset(video_root_path, annotation_path, audio_root_path, subset, fps=30, need_audio=True):
    # 加载标签文件
    with open(annotation_path, 'r') as f:
        annotations = json.load(f)  # 包含 Valence 和 Arousal 字段
    
    # 获取视频目录
    video_dirs = [d for d in os.listdir(video_root_path) if os.path.isdir(os.path.join(video_root_path, d))]
    
    dataset = []
    for i, video_dir in enumerate(video_dirs):
        if i % 100 == 0:
            print(f"Dataset loading [{i}/{len(video_dirs)}]")
        
        video_path = os.path.join(video_root_path, video_dir)  # 视频目录路径
        
        if need_audio:
            audio_path = os.path.join(audio_root_path, f"{video_dir}.mp3")  # 音频路径
        else:
            audio_path = None
        
        assert os.path.exists(video_path), f"Video directory not found: {video_path}"
        if need_audio:
            assert os.path.exists(audio_path), f"Audio file not found: {audio_path}"
        
        # 从 annotations 中获取 VA 值
        valence_value = annotations["Valence"].get(video_dir, 0)  # 默认为 0
        arousal_value = annotations["Arousal"].get(video_dir, 0)  # 默认为 0
        
        # 获取帧数（假设 JPEG 文件以连续数字命名，例如 1.jpg, 2.jpg...）
        frame_files = [f for f in os.listdir(video_path) if f.endswith('.jpg')]
        n_frames = len(frame_files)
        if n_frames <= 0:
            print(f"No frames found in: {video_path}")
            continue
        
        begin_t = 1
        end_t = n_frames
        sample = {
            'video': video_path,
            'segment': [begin_t, end_t],
            'n_frames': n_frames,
            'video_id': video_dir,
        }

        # 添加音频路径
        if need_audio:
            sample['audio'] = audio_path
        
        # 将 VA 值作为 target
        va_target = [valence_value, arousal_value]
        sample['target'] = va_target

        # 计算帧索引
        ORIGINAL_FPS = 24  # 假设原始帧率为 24
        step = ORIGINAL_FPS // fps
        sample['frame_indices'] = list(range(1, n_frames + 1, step))
        
        dataset.append(sample)
    
    return dataset, video_dirs