import copy

import numpy as np
import scipy as sp
import scipy.signal as sig

from functools import reduce

def reconstruct(lpc_frame):
    gain = lpc_frame.get_gain()
    coefficients = lpc_frame.get_coefficients()
    residue = process_residue(lpc_frame.get_residue())
    return sig.lfilter(np.asarray([gain]), coefficients, residue) 

def process_residue(residue):
    return residue

class Synthesizer():
    """
    Class decodes lpc packets into an array.
    """

    def __init__(self, lpc_frame_array):
        """
        """
        self._frame_array = lpc_frame_array

    def decode(self):
        """
        Decodes an lpcframearray into an array representing an audio signal.
        """
        audio_frames = self._reconstruct_frames()
        audio_array = self._merge_frames(audio_frames)
        return audio_array

    def _reconstruct_frames(self):
        frames = self.get_frame_array().get_frames()
        return np.asarray(map(reconstruct, frames))

    def _merge_frames(self, audio_frames):
        lpc_frame_array = self.get_frame_array()
        lpc_frames = lpc_frame_array.get_frames()
        lpc_length = lpc_frames.shape[0]
        samples_per_frame = lpc_frame_array.get_fs() * lpc_frame_array.get_frame_size()
        base_window = np.hamming(samples_per_frame * 2)
        window = np.insert(base_window, base_window.size // 2, np.ones(samples_per_frame))
        windows = np.tile(window, (lpc_length, 1))
        windows[0, :samples_per_frame] = np.ones(samples_per_frame)
        windows[-1, -samples_per_frame:] = np.ones(samples_per_frame)
        tapered_audio = audio_frames * windows
        def merge(arr1, arr2):
            combined_overlap = arr1[-samples_per_frame:] + arr2[:samples_per_frame]
            return np.concatenate((arr1[:-samples_per_frame], combined_overlap, arr2[samples_per_frame:]))
        return reduce(merge, tapered_audio)
        

    #Accessor methods
    def get_frame_array(self):
        return self._frame_array

    def get_fs(self):
        return self.get_frame_array().get_fs()

