import numpy as np
from sklearn.externals import joblib
import pdb
import cv2


class Align(object):

    def __init__(self,
                 reference='../cache/mean_landmarks.pkl',
                 scale=(128, 128),
                 margin=(0.15, 0.1),
                 idx=None):
        """
        :param reference: 参考landmark的路径or reference np.array
        :param scale: 输出图片大小，tuple, (rows, cols)
        :param margin: tuple，(x_margin, y_margin)人脸和边界之间的距离，左右margin为x_margin*W,上下margin为y_margin*H，
                       其中W和H为人脸的宽度和高度
        """
        if isinstance(reference, str):
            self.reference = joblib.load(reference)
        else:
            self.reference = reference
        if not (idx is None):
            self.reference = self.reference[idx]
            self.idx = idx
        else:
            self.idx = list(range(106))
        # plt.subplot(1, 2, 1)
        # plt.scatter(self.reference[:, 0], self.reference[:, 1])
        max_y, min_y, max_x, min_x = [max(self.reference[:, 1]), min(self.reference[:, 1]),
                                      max(self.reference[:, 0]), min(self.reference[:, 0])]
        h = max_y - min_y
        w = max_x - min_x
        margin_x, margin_y = margin
        k_x, b_x = [1 / w, margin_x - min_x / w]
        k_y, b_y = [1 / h, margin_y - min_y / h]

        self.reference[:, 0] = (k_x * self.reference[:, 0] + b_x) / (2 * margin_x + 1) * scale[0]
        self.reference[:, 1] = (k_y * self.reference[:, 1] + b_y) / (2 * margin_y + 1) * scale[1]
        self.scale = scale
        self.n = np.array([[1, 0, 0],
                      [0, 1, 0],
                      [-self.scale[1] / 2, -self.scale[0] / 2, 1]], dtype=np.float32)
        self.p = np.array([[1, 0, 0],
                      [0, 1, 0],
                      [self.scale[1] / 2, self.scale[0] / 2, 1]], dtype=np.float32)

    def __call__(self, image, landmarks, noise=(0, 0), radian=0):
        """
        :param image: (H, W, 3)
        :param landmarks: (N, 2), unnormalized
        :param bbox: [[min_x, min_y]
                       max_x, max_y]]
        :return: aligned image
        """
        landmarks = landmarks[self.idx,:]
        ones = np.ones(len(landmarks), dtype=np.float32)
        x = np.c_[landmarks, ones]
        reference = self.reference
        # reference[: 0] += noise[0]
        # reference[:, 1] += noise[1]
        T = pdb.procrustes(x, reference)
        rotate = np.array([[np.cos(radian), np.sin(radian), 0],
                           [-np.sin(radian), np.cos(radian), 0],
                           [0, 0, 1]], dtype=np.float32)

        T = np.c_[T, np.array([0, 0, 1], dtype=np.float32)]
        T = (T @ self.n @ rotate @ self.p)[:, 0:2]
        T[2, 0] += noise[0]
        T[2, 1] += noise[1]
        # T = n[:, 0:2]
        landmarks = x @ T

        image = cv2.warpAffine(image, np.transpose(T), self.scale)
        return image, landmarks, T

    def inverse(self, landmarks, T):
        """
        返回到对齐前的坐标系
        :return: 原坐标系中对应的landmark坐标
        """
        landmarks = (landmarks - T[2:, :]) @ np.linalg.inv(T[0:2, ])
        return landmarks


if __name__ == '__main__':


    # 示例代码：
    import os
    import matplotlib.pyplot as plt
    import data.utils as ul
    root_dir = '/data/icme'
    bin_dir = '/data/icme/train'
    pose = 1
    a = Align()
    bins = os.listdir(bin_dir)

    file_list = []
    b = bins[pose]
    curr = os.path.join(bin_dir, b)
    files = os.listdir(curr)
    for i in files:
        file_list.append(i)
    for i in range(100):
        img_dir = os.path.join(root_dir, 'data/picture')
        landmark_dir = os.path.join(root_dir, 'data/landmark')
        bbox_dir = os.path.join(root_dir, 'bbox')
        images = [os.path.join(img_dir, f) for f in file_list]
        landmarks = [os.path.join(landmark_dir, f + '.txt') for f in file_list]
        bboxes = [os.path.join(bbox_dir, f + '.rect') for f in file_list]
        img_path = images[i]
        bbox_path = bboxes[i]
        landmark_path = landmarks[i]
        bbox = ul.read_bbox(bbox_path)
        landmarks = ul.read_mat(landmark_path)
        image = cv2.imread(img_path)

        image, landmark, t = a(image, landmarks)

        plt.imshow(image)
        plt.scatter(landmark[:, 0], landmark[:, 1])
        # plt.scatter(self.reference[:, 0], self.reference[:, 1])
        # plt.plot(bbox[:, 0], bbox[:, 1])
        plt.xlim(0, a.scale[0])
        plt.ylim(a.scale[1], 0)
        plt.show()