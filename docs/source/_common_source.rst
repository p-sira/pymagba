.. method:: compute_B(points)
   :no-index:

   Compute the magnetic flux density B at a batch of observer points.

   :param points: Array of shape (N, 3) containing the observer positions [x, y, z] in meters.
   :type points: numpy.ndarray
   :return: Array of shape (N, 3) with the [Bx, By, Bz] field vectors in Tesla at each observer point.
   :rtype: numpy.ndarray
