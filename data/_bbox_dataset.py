import os
import cv2
import numpy as np
from data.face_dataset import FaceDataset
from data import utils

class BBoxDataset(FaceDataset):

    def __init__(self,
                 img_dir,
                 ldmk_dir,
                 bbox_dir,
                 bin_dir,
                 bins=[1,2,3,4,5,6,7,8,9,10,11],
                 phase='train',
                 shape=(224, 224)):
        super(BBoxDataset, self).__init__(img_dir, ldmk_dir, bin_dir, bins, phase, shape)
        self.bboxes = [os.path.join(bbox_dir, f + '.rect') for f in self.file_list]

    def __getitem__(self, item):
        image, landmarks = super(BBoxDataset, self).__getitem__(item)
        bbox_path = self.bboxes[item]
        try:
            bbox = utils.read_bbox(bbox_path)
        except:
            bbox = [0, 0, image.shape[1] - 1, image.shape[0] - 1]

        minx, miny, maxx, maxy = bbox
        image = image[miny:maxy + 1, minx:maxx + 1, :]
        image = cv2.resize(image, self.shape)

        image = np.transpose(image, (2, 0, 1)).astype(np.float32)
        return image, np.reshape(landmarks, (-1)), np.array(bbox), self.file_list[item]


if __name__ == '__main__':
    a = BBoxDataset('/data/icme/data/picture',
                    '/data/icme/data/landmark',
                    '/data/icme/bbox',
                    '/data/icme/train')
    a.__getitem__(1)