from typing import Iterator, Tuple, Any

import h5py
import os
import glob
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
import tensorflow_datasets as tfds
from roboset.conversion_utils import MultiThreadedDatasetBuilder
from roboset.instructions import path2instruct


DATA_PATH = "/Users/karl/Downloads/mnt"


def _generate_examples(paths) -> Iterator[Tuple[str, Any]]:
    """Yields episodes for list of data paths."""
    # the line below needs to be *inside* generate_examples so that each worker creates it's own model
    # creating one shared model outside this function would cause a deadlock

    def _parse_example(episode, file_path, trial_id):
        # determine language instruction based on file path
        try:
            instruction = path2instruct(file_path)
        except Exception:
            print(f"No matching instruction for {file_path}!")
            return None

        # extract fields
        try:
            img_left = episode['rgb_left'][()]
            img_right = episode['rgb_right'][()]
            img_top = episode['rgb_top'][()]
            img_wrist = episode['rgb_wrist'][()]
            ctrl_arm = episode['ctrl_arm'][()]
            ctrl_ee = episode['ctrl_ee'][()]
            qp_arm = episode['qp_arm'][()]
            qp_ee = episode['qp_ee'][()]
            qv_arm = episode['qv_arm'][()]
            qv_ee = episode['qv_ee'][()]
        except Exception:
            print(f"Could not load data for {file_path}, trial {trial_id}.")
            return None

        if not (
            img_left.shape[0]
            == img_right.shape[0]
            == img_top.shape[0]
            == img_wrist.shape[0]
            == ctrl_arm.shape[0]
            == ctrl_ee.shape[0]
            == qp_arm.shape[0]
            == qp_ee.shape[0]
            == qv_arm.shape[0]
            == qv_ee.shape[0]
        ):
            print(f"Array lengths are not consistent for {file_path}, trial {trial_id}.")
            return None

        # assemble episode --> here we're assuming demos so we set reward to 1 at the end
        episode = []
        for i in range(img_left.shape[0]):
            if (
                np.any(np.isnan(qp_arm[i]))
                or np.any(np.isnan(qv_arm[i]))
                or np.any(np.isnan(qp_ee[i]))
                or np.any(np.isnan(qv_ee[i]))
                or np.any(np.isnan(ctrl_arm[i]))
                or np.any(np.isnan(ctrl_ee[i]))
            ):
                continue

            episode.append({
                'observation': {
                    'image_left': img_left[i],
                    'image_right': img_right[i],
                    'image_top': img_top[i],
                    'image_wrist': img_wrist[i],
                    'state': np.asarray(
                        np.concatenate((qp_arm[i], qp_ee[i][None]), axis=-1), dtype=np.float32),
                    'state_velocity': np.asarray(
                        np.concatenate((qv_arm[i], qv_ee[i][None]), axis=-1), dtype=np.float32),
                },
                'action': np.asarray(np.concatenate((ctrl_arm[i], ctrl_ee[i]), axis=-1), dtype=np.float32),
                'discount': 1.0,
                'reward': 0.,
                'is_first': not episode,
                'is_last': False,
                'is_terminal': False,
                'language_instruction': instruction,
            })

        # set reward of 1 on final step of episode
        episode[-1]['reward'] = 1.0
        episode[-1]['is_last'] = True
        episode[-1]['is_terminal'] = True

        # create output data sample
        sample = {
            'steps': episode,
            'episode_metadata': {
                'file_path': file_path,
                'trial_id': trial_id,
            }
        }

        # if you want to skip an example for whatever reason, simply return None
        return file_path + '_' + trial_id, sample

    for sample in paths:
        h5 = h5py.File(sample, 'r')
        trial_keys = h5.keys()      # contains ['Trial0', 'Trial1', ...]
        for key in trial_keys:
            yield _parse_example(h5[key]['data'], sample, key)


class Roboset(MultiThreadedDatasetBuilder):
    """DatasetBuilder for example dataset."""

    VERSION = tfds.core.Version('1.0.0')
    RELEASE_NOTES = {
      '1.0.0': 'Initial release.',
    }
    N_WORKERS = 2             # number of parallel workers for data conversion
    MAX_PATHS_IN_MEMORY = 4   # number of paths converted & stored in memory before writing to disk
                               # -> the higher the faster / more parallel conversion, adjust based on avilable RAM
                               # note that one path may yield multiple episodes and adjust accordingly
    PARSE_FCN = _generate_examples      # handle to parse function from file paths to RLDS episodes

    def _info(self) -> tfds.core.DatasetInfo:
        """Dataset metadata (homepage, citation,...)."""
        return self.dataset_info_from_configs(
            features=tfds.features.FeaturesDict({
                'steps': tfds.features.Dataset({
                    'observation': tfds.features.FeaturesDict({
                        'image_left': tfds.features.Image(
                            shape=(240, 424, 3),
                            dtype=np.uint8,
                            encoding_format='jpeg',
                            doc='Left camera RGB observation.',
                        ),
                        'image_right': tfds.features.Image(
                            shape=(240, 424, 3),
                            dtype=np.uint8,
                            encoding_format='jpeg',
                            doc='Right camera RGB observation.',
                        ),
                        'image_top': tfds.features.Image(
                            shape=(240, 424, 3),
                            dtype=np.uint8,
                            encoding_format='jpeg',
                            doc='Top camera RGB observation.',
                        ),
                        'image_wrist': tfds.features.Image(
                            shape=(240, 424, 3),
                            dtype=np.uint8,
                            encoding_format='jpeg',
                            doc='Wrist camera RGB observation.',
                        ),
                        'state': tfds.features.Tensor(
                            shape=(8,),
                            dtype=np.float32,
                            doc='Robot state, consists of [7x robot joint angles, '
                                '1x gripper position].',
                        ),
                        'state_velocity': tfds.features.Tensor(
                            shape=(8,),
                            dtype=np.float32,
                            doc='Robot state, consists of [7x robot joint velocities, '
                                '1x gripper velocity].',
                        ),
                    }),
                    'action': tfds.features.Tensor(
                        shape=(8,),
                        dtype=np.float32,
                        doc='Robot action, consists of [7x joint velocities, '
                            '1x gripper velocity -- -1 = open, +1 = close].',
                    ),
                    'discount': tfds.features.Scalar(
                        dtype=np.float32,
                        doc='Discount if provided, default to 1.'
                    ),
                    'reward': tfds.features.Scalar(
                        dtype=np.float32,
                        doc='Reward if provided, 1 on final step for demos.'
                    ),
                    'is_first': tfds.features.Scalar(
                        dtype=np.bool_,
                        doc='True on first step of the episode.'
                    ),
                    'is_last': tfds.features.Scalar(
                        dtype=np.bool_,
                        doc='True on last step of the episode.'
                    ),
                    'is_terminal': tfds.features.Scalar(
                        dtype=np.bool_,
                        doc='True on last step of the episode if it is a terminal step, True for demos.'
                    ),
                    'language_instruction': tfds.features.Text(
                        doc='Language Instruction.'
                    ),
                }),
                'episode_metadata': tfds.features.FeaturesDict({
                    'file_path': tfds.features.Text(
                        doc='Path to the original data file.'
                    ),
                    'trial_id': tfds.features.Text(
                        doc='ID of trial in file.'
                    ),
                }),
            }))

    def _split_paths(self):
        """Define filepaths for data splits."""
        paths = glob.glob(os.path.join(DATA_PATH, '**/*.h5'), recursive=True)
        print(f"Found {len(paths)} paths!")
        return {
            'train': paths,
        }

