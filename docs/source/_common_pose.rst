.. property:: position
   :type: ArrayLike3
   :no-index:

   Position of the object [x, y, z] in meters.

.. property:: orientation
   :type: scipy.spatial.transform.Rotation
   :no-index:

   Orientation as a scipy.spatial.transform.Rotation object.

.. method:: translate(translation)
   :no-index:

   Translate the object by a displacement vector.

   :param translation: Displacement [dx, dy, dz] in meters.
   :type translation: ArrayLike3

.. method:: rotate(rot)
   :no-index:

   Rotate the object about its own origin.

   :param rot: Rotation to apply. Can be a scipy.spatial.transform.Rotation object or a unit quaternion as a list.
   :type rot: Rotation | ArrayLike4

.. method:: rotate_anchor(rot, anchor)
   :no-index:

   Rotate the object about an arbitrary anchor point.

   :param rot: Rotation to apply.
   :type rot: Rotation | ArrayLike4
   :param anchor: Anchor point [x, y, z] in meters about which to rotate.
   :type anchor: ArrayLike3
