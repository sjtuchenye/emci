import os
import cv2
import numpy as np
from torch.utils.data import Dataset, DataLoader
from random import shuffle
from data import utils


class FaceDataset(Dataset):
    def __init__(self, root_dir, bin_dir, shape=(224, 224)):
        """
        :param root_dir: icme文件夹路径，见README
        :param bin_dir:  train或者valid文件夹路径，见README
        :param phase:
        :param transform:
        """
        super(FaceDataset, self).__init__()
        self.shape = shape
        # bin_dir为pdb.py中的图片输出目录（即cmd里的目录），root_dir为数据集根目录
        bins = os.listdir(bin_dir)
        s = []
        for b in bins:
            curr = os.path.join(bin_dir, b)
            s.append(len(os.listdir(curr)))

        # 所有pose都采样到约max_n张，1.2倍是我随便设置的
        max_n = int(max(s) * 1.2)
        file_list = []
        for b in bins:
            curr = os.path.join(bin_dir, b)
            files = os.listdir(curr)
            for i in files:
                p = max_n / len(files)
                # 万一出现max_n是某个pose数量的2倍以上
                while p > 1:
                    file_list.append(i)
                    p -= 1
                # 掷色子决定是否再次重采样
                dice = np.random.uniform(0, 1)
                if dice < p:
                    file_list.append(i)
        # 打乱顺序
        shuffle(file_list)
        img_dir = os.path.join(root_dir, 'data/picture')
        landmark_dir = os.path.join(root_dir, 'data/landmark')
        bbox_dir = os.path.join(root_dir, 'bbox')
        self.images = [os.path.join(img_dir, f) for f in file_list]
        self.landmarks = [os.path.join(landmark_dir, f + '.txt') for f in file_list]
        self.bboxes = [os.path.join(bbox_dir, f + '.rect') for f in file_list]

    def __len__(self):
        return len(self.images)

    def __getitem__(self, i):
        img_path = self.images[i]
        bbox_path = self.bboxes[i]
        landmark_path = self.landmarks[i]
        bbox = utils.read_bbox(bbox_path)
        landmarks = utils.read_mat(landmark_path)
        landmarks = utils.norm_landmarks(landmarks, bbox)
        image = cv2.imread(img_path)
        # minx, miny, maxx, maxy = bbox
        # image = image[miny:maxy+1, minx:maxx+1, :]
        # image = cv2.resize(image, self.shape)
        # cv2.imshow("t", image)
        # cv2.waitKey(0)
        image = np.transpose(image, (2, 0, 1)).astype(np.float32)
        #print('origin', origin_landmarks)
        return image, np.reshape(landmarks, (-1)), np.reshape(np.array(bbox), (2, 2))


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    a = FaceDataset("/home/orion/Desktop/ecmi/emci/data/icme", "/home/orion/Desktop/ecmi/emci/data/icme/train")
    image, lankmark, bbox= a.__getitem__(0)
    image = np.transpose(image, (1, 2, 0)).astype(np.uint8)
    plt.imshow(image)
    plt.show()
    print(image)
    print(image.shape)
    print(lankmark.shape)

