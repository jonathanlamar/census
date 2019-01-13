import pandas as pd


#########################################################################################
# This class contains methods that define indices into a square array of shape (dim, dim)
# in such a way that lower indices are grouped closer to the bottom-right corner of the
# square, while the higher indices are grouped farther away.
#########################################################################################
class SquareIndex:
    def spiral(dim):
        def loop(acc, to_add):
            if to_add == 0:
                return acc
            else:
                N = acc.shape[0]
                if acc.shape[1] != N:
                    raise RecusionError('Error in recursion.')
                new_acc = np.zeros((N+1, N+1))
                new_acc[1:, 1:] = acc
                entry = N**2
                for i in range(N, -1, -1):
                    new_acc[i, 0] = entry
                    entry += 1
                for i in range(1, N+1):
                    new_acc[0, i] = entry
                    entry += 1
                return loop(new_acc, to_add - 1)
        return loop(np.zeros((0, 0)), dim)

    def dovetail(dim):
        def loop(acc, to_add):
            if to_add == 0:
                return acc
            else:
                N = acc.shape[0]
                if acc.shape[1] != N:
                    raise RecusionError('Error in recursion.')
                new_acc = np.zeros((N+1, N+1))
                new_acc[1:, 1:] = acc
                entry = N**2
                for i in range(N, -1, -1):
                    new_acc[0, i] = entry
                    entry += 2
                entry = N**2 + 1
                for i in range(N, 0, -1):
                    new_acc[i, 0] = entry
                    entry += 2
                return loop(new_acc, to_add - 1)
        if dim == 0:
            return np.zeros((0, 0))
        else:
            return loop(np.zeros((1, 1)), dim - 1)
