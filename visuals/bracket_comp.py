import numpy as np

#################################################################################################
# This class contains some metrics for comparing the difference between two sets of binned data.
# As an example, the census and demo atom give us measures of household income breakdowns for a
# census tract (num households in 0-15K$/yr, 15-20, etc.).  Those sets of data can be represented
# as arrays and passed to one of the metrics here.
#################################################################################################
class BinnedDataMetrics:
    def overestimate_expectation(census, demo, midpoints, normalize_first=False):
        # census, demo, and midpoints should be np arrays of shape (n,)
        # normalize first indicates whether we should divide each array by its sum.
        census = census.reshape(-1)
        demo = demo.reshape(-1)
        midpoints = midpoints.reshape(-1)

        if normalize_first:
            if census.sum() > 0:
                census = census / census.sum()
            if demo.sum() > 0:
                demo = demo / demo.sum()

        if any([x != census.shape[0] for x in [demo.shape[0], midpoints.shape[0]]]):
            raise ValueError('Invalid input dimensions.')
        else:
            N = census.shape[0]

        # Precompute underestimates and get sum for the expectation
        under_ests = -1 * np.ones(N)
        for j in range(N):
            if demo[j] > census[j]:
                continue
            under_ests[j] = census[j] - demo[j]

        total_underest = under_ests[under_ests != -1].sum()

        acc = 0
        for i in range(N):
            if demo[i] <= census[i]:
                continue # Only count error when demo overestimates the number in a bracket

            over_est = demo[i] - census[i] # number of people in this bracket who shouldn't be
            prob = over_est / demo[i] # probability someone in this bracket shouldn't be
            
            expectation = 0
            if total_underest > 0:
                for j in range(N):
                    if under_ests[j] == -1:
                        continue # Sum over all the underestimates that could balance out the overestimate

                    expectation += np.abs(midpoints[i] - midpoints[j]) * (under_ests[j] / total_underest)
            acc += (prob * expectation)

        return acc

    def avg_abs_err(census, midpoints):
        census = census.reshape(-1)
        midpoints = midpoints.reshape(-1)

        if census.shape[0] != midpoints.shape[0]:
            raise ValueError('Invalid input dimensions.')
        else:
            N = census.shape[0]

        midpoint_summary = midpoints[census.argmax()]

        if census.sum() > 0:
            census = census / census.sum()

        acc = 0
        for i in range(N):
            acc += census[i] * np.abs(midpoints[i] - midpoint_summary)

        return acc

    def lebesgue(census, demo, p, normalize_first=True):
        census = census.reshape(-1)
        demo = demo.reshape(-1)

        if normalize_first:
            if census.sum() > 0:
                census = census / census.sum()
            if demo.sum() > 0:
                demo = demo / demo.sum()

        if census.shape[0] != demo.shape[0]:
            raise ValueError('Invalid input dimensions.')
        else:
            N = census.shape[0]

        return sum( np.abs(census - demo)**p )*(1/p)
