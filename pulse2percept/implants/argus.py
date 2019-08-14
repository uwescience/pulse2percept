import numpy as np
import collections as coll
from .base import (DiskElectrode, ElectrodeArray, ElectrodeGrid,
                   ProsthesisSystem)


class ArgusI(ProsthesisSystem):
    # remove the tack

    def __init__(self, x=0, y=0, z=0, rot=0, eye='RE', stim=None,
                 use_legacy_names=False):
        """Create an ArgusI array on the retina
        This function creates an ArgusI array and places it on the retina
        such that the center of the array is located at 3D location (x,y,z),
        given in microns, and the array is rotated by rotation angle `rot`,
        given in radians.

        The array is oriented in the visual field as shown in Fig. 1 of
        Horsager et al. (2009); that is, if placed in (0,0), the top two
        rows will lie in the lower retina (upper visual field):

        .. raw:: html
          <pre>
            -y      A1 B1 C1 D1                     260 520 260 520
            ^       A2 B2 C2 D2   where electrode   520 260 520 260
            |       A3 B3 C3 D3   diameters are:    260 520 260 520
            -->x    A4 B4 C4 D4                     520 260 520 260
          </pre>

        Electrode order is: A1, B1, C1, D1, A2, B2, ..., D4.
        If `use_legacy_names` is True, electrode order is: L6, L2, M8, M4, ...
        An electrode can be addressed by index (integer) or name. Column
        order is reversed in the left eye.

        Parameters
        ----------
        x : float, optional, default: 0
            x coordinate of the array center (um)
        y : float, optional, default: 0
            y coordinate of the array center (um)
        z : float || array_like, optional, default: 0
            Distance of the array to the retinal surface (um). Either a list
            with 16 entries or a scalar.
        rot : float, optional, default: 0
            Rotation angle of the array (rad). Positive values denote
            counter-clock-wise (CCW) rotations in the retinal coordinate
            system.
        eye : {'LE', 'RE'}, optional, default: 'RE'
            Eye in which array is implanted.

        Examples
        --------
        Create an ArgusI array centered on the fovea, at 100um distance from
        the retina:

        >>> from pulse2percept import implants
        >>> argus = implants.ArgusI(x=0, y=0, z=100, rot=0)

        Get access to electrode 'B1':

        >>> my_electrode = argus['B1']

        """
        # Argus I is a 4x4 grid of electrodes with 200um in diamater, spaced
        # 525um apart, with rows labeled alphabetically and columsn
        # numerically:
        self.eye = eye
        shape = (4, 4)
        r_arr = np.array([260, 520, 260, 520]) / 2.0
        r_arr = np.concatenate((r_arr, r_arr[::-1], r_arr, r_arr[::-1]),
                               axis=0)
        spacing = 800.0

        # In older papers, Argus I electrodes go by L and M
        self.old_names = names = ['L6', 'L2', 'M8', 'M4',
                                  'L5', 'L1', 'M7', 'M3',
                                  'L8', 'L4', 'M6', 'M2',
                                  'L7', 'L3', 'M5', 'M1']

        names = self.old_names if use_legacy_names else ('1', 'A')

        self.earray = ElectrodeGrid(shape, x=x, y=y, z=z, rot=rot, r=r_arr,
                                    spacing=spacing, names=names)

        # Set stimulus if available:
        self.stim = stim

        # Set left/right eye:
        if not isinstance(eye, str):
            raise TypeError("'eye' must be a string, either 'LE' or 'RE'.")
        if eye != 'LE' and eye != 'RE':
            raise ValueError("'eye' must be either 'LE' or 'RE'.")
        self.eye = eye
        # Unfortunately, in the left eye the labeling of columns is reversed...
        if eye == 'LE':
            # FIXME: Would be better to have more flexibility in the naming
            # convention. This is a quick-and-dirty fix:
            names = list(self.earray.keys())
            objects = list(self.earray.values())
            names = np.array(names).reshape(self.earray.shape)
            # Reverse column names:
            for row in range(self.earray.shape[0]):
                names[row] = names[row][::-1]
            # Build a new ordered dict:
            electrodes = coll.OrderedDict([])
            for name, obj in zip(names.ravel(), objects):
                electrodes.update({name: obj})
            # Assign the new ordered dict to earray:
            self.earray.electrodes = electrodes

        # # Alternating electrode sizes, arranged in checkerboard pattern
        # r_arr = np.array([260, 520, 260, 520]) / 2.0
        # r_arr = np.concatenate((r_arr, r_arr[::-1], r_arr, r_arr[::-1]),
        #                        axis=0)

        # # Set left/right eye
        # self.eye = eye

        # # # In older papers, Argus I electrodes go by L and M
        # self.old_names = names = ['L6', 'L2', 'M8', 'M4',
        #                           'L5', 'L1', 'M7', 'M3',
        #                           'L8', 'L4', 'M6', 'M2',
        #                           'L7', 'L3', 'M5', 'M1']
        # # # In newer papers, they go by A-D: A1, B1, C1, D1, A1, B2, ..., D4
        # # # Shortcut: Use `chr` to go from int to char

        # self.new_names = [chr(i) + str(j) for j in range(1, 5)
        #                   for i in range(65, 69)]
        # if self.eye == 'RE':
        #    self.new_names = [chr(i) + str(j) for j in range(1, 5)
        #                      for i in range(65, 69)]
        # else:
        #   self.new_names = [chr(i) + str(j) for j in range(1, 5)
        #                      for i in range(68, 64, -1)]
        # # # A10, ... A1

        # names = self.old_names if use_legacy_names else self.new_names

        # if isinstance(z, (list, np.ndarray)):
        #     z_arr = np.asarray(z).flatten()
        #     if z_arr.size != len(r_arr):
        #         e_s = "If `z` is a list, it must have 16 entries."
        #         raise ValueError(e_s)
        # else:
        #     # All electrodes have the same height
        #     z_arr = np.ones_like(r_arr) * z

        # # Equally spaced electrodes: n_rows x n_cols = 16
        # e_spacing = 800  # um
        # n_cols = 4  # number of electrodes horizontally (same vertically)
        # x_arr = np.arange(n_cols) * e_spacing - (n_cols / 2 - 0.5) * e_spacing
        # if self.eye == 'LE':
        #     # Left eye: Need to invert x coordinates and rotation angle
        #     x_arr = x_arr[::-1]

        # x_arr, y_arr = np.meshgrid(x_arr, x_arr, sparse=False)
        # if self.eye == 'LE':
        #     # Left eye: Need to invert y coordinates and rotation angle
        #     y_arr = y_arr[::-1]

        # # Rotation matrix
        # R = np.array([np.cos(rot), -np.sin(rot),
        #               np.sin(rot), np.cos(rot)]).reshape((2, 2))

        # # Set the x, y location of the tack
        # if self.eye == 'RE':
        #     self.tack = np.matmul(R, [-(n_cols / 2 + 0.5) * e_spacing, 0])
        # else:
        #     self.tack = np.matmul(R, [(n_cols / 2 + 0.5) * e_spacing, 0])
        # self.tack = tuple(self.tack + [x, y])

        # # Rotate the array
        # xy = np.vstack((x_arr.flatten(), y_arr.flatten()))
        # xy = np.matmul(R, xy)
        # x_arr = xy[0, :]
        # y_arr = xy[1, :]

        # # Apply offset
        # x_arr += x
        # y_arr += y

        # self.earray = ElectrodeArray([])
        # for x, y, z, r, name in zip(x_arr, y_arr, z_arr, r_arr, names):
        #     self.earray.add_electrode(name, DiskElectrode(x, y, z, r))
        # self.stim = stim


class ArgusII(ProsthesisSystem):

    def __init__(self, x=0, y=0, z=0, rot=0, eye='RE', stim=None):
        """Create an ArgusII array on the retina

        This function creates an ArgusII array and places it on the retina
        such that the center of the array is located at (x,y,z), given in
        microns, and the array is rotated by rotation angle `rot`, given in
        radians.

        The array is oriented upright in the visual field, such that an
        array with center (0,0) has the top three rows lie in the lower
        retina (upper visual field), as shown below:

        .. raw:: html
          <pre>
                    A1 A2 A3 A4 A5 A6 A7 A8 A9 A10
            -y      B1 B2 B3 B4 B5 B6 B7 B8 B9 B10
            ^       C1 C2 C3 C4 C5 C6 C7 C8 C9 C10
            |       D1 D2 D3 D4 D5 D6 D7 D8 D9 D10
            -->x    E1 E2 E3 E4 E5 E6 E7 E8 E9 E10
                    F1 F2 F3 F4 F5 F6 F7 F8 F9 F10
          </pre>

        Electrode order is: A1, A2, ..., A10, B1, B2, ..., F10.
        An electrode can be addressed by index (integer) or name. Note
        that the columns move from 10 to 1 in the left eye.

        Parameters
        ----------
        x : float
            x coordinate of the array center (um)
        y : float
            y coordinate of the array center (um)
        z: float || array_like
            Distance of the array to the retinal surface (um). Either a list
            with 60 entries or a scalar.
        rot : float
            Rotation angle of the array (rad). Positive values denote
            counter-clock-wise (CCW) rotations in the retinal coordinate
            system.
        eye : {'LE', 'RE'}, optional, default: 'RE'
            Eye in which array is implanted.

        Examples
        --------
        Create an ArgusII array centered on the fovea, at 100um distance from
        the retina:

        >>> from pulse2percept import implants
        >>> argus = implants.ArgusII(x=0, y=0, z=100, rot=0)

        Get access to electrode 'E7':

        >>> my_electrode = argus['E7']

        """
        # Argus II is a 6x10 grid of electrodes with 200um in diamater, spaced
        # 525um apart, with rows labeled alphabetically and columsn
        # numerically:
        shape = (6, 10)
        r = 100.0
        spacing = 525.0
        names = ('A', '1')
        self.earray = ElectrodeGrid(shape, x=x, y=y, z=z, rot=rot, r=r,
                                    spacing=spacing, names=names)

        # Set stimulus if available:
        self.stim = stim

        # Set left/right eye:
        if not isinstance(eye, str):
            raise TypeError("'eye' must be a string, either 'LE' or 'RE'.")
        if eye != 'LE' and eye != 'RE':
            raise ValueError("'eye' must be either 'LE' or 'RE'.")
        self.eye = eye
        # Unfortunately, in the left eye the labeling of columns is reversed...
        if eye == 'LE':
            # FIXME: Would be better to have more flexibility in the naming
            # convention. This is a quick-and-dirty fix:
            names = list(self.earray.keys())
            objects = list(self.earray.values())
            names = np.array(names).reshape(self.earray.shape)
            # Reverse column names:
            for row in range(self.earray.shape[0]):
                names[row] = names[row][::-1]
            # Build a new ordered dict:
            electrodes = coll.OrderedDict([])
            for name, obj in zip(names.ravel(), objects):
                electrodes.update({name: obj})
            # Assign the new ordered dict to earray:
            self.earray.electrodes = electrodes
