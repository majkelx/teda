import math
import numpy as np
from scipy import optimize


def fit_gauss_1d_zero_c(x, y):
    """
    Fits a*gaussian(0, sig) + sky of mu=0

    Returns
    -------
    model, a, sig, c, rmse
    """
    x, y = np.asarray(x), np.asarray(y)
    gauss0 = lambda x, a, c, sig2: c + a * np.exp(-x ** 2 / (2 * sig2))

    opt, cov = optimize.curve_fit(gauss0, x, y, p0=[1.0, 0.0, 1.0])
    res = gauss0(x, *opt) - y
    rmse = math.sqrt((res * res).sum() / len(res))
    try:
        sig = math.sqrt(opt[2])
    except ValueError:
        sig = 0
    return gauss0, opt[0], sig, opt[1], rmse

def fit_gauss_2d_c(xy ,values, initial_mu = None, mu_radius=(np.inf, np.inf)):
    """
    Fits a*gaussian(mu_x, mu_y, sig) + sky

    Parameters
    ----------
    xy:
        List of coordinates, shape: Nx2

    Returns
    -------
    model, a, mu_x, mu_y, sig, c, rmse
    """
    if initial_mu is None: # initial guess
        initial_mu = xy[0]


    xy = np.asarray(xy).T  # transpose xy[0]=x  xy[1] = y

    def gauss(xy, a, c, mu_x, mu_y, sig2):
        val = c + a * np.exp(-((mu_x - xy[0])** 2 + (mu_y - xy[1])** 2) / (2 * sig2))
        return val

    # gauss = lambda xy, a, c, mu_x, mu_y, sig2: c + a * np.exp(-((mu_x - xy[0])** 2 + (mu_y - xy[1])** 2) / (2 * sig2))

    minimal = np.nanmin(values)
    maximal = np.nanmax(values)
    opt, cov = optimize.curve_fit(gauss, xy, values,
                                  p0=[maximal - minimal, minimal, initial_mu[0], initial_mu[1], 1.0],
                                  bounds=(
                                      [0.0,     -2.0**18, initial_mu[0]-mu_radius[0], initial_mu[1]-mu_radius[1], 0.0],
                                      [2.0**19,  2.0**18, initial_mu[0]+mu_radius[0], initial_mu[1]+mu_radius[1], 1e10])
                                  )
    res = (gauss(xy, *opt) - values)
    rmse = math.sqrt((res * res).sum() / len(values)),
    try:
        sig = math.sqrt(opt[4])
    except ValueError:
        sig = 0
    return gauss, opt[0], opt[2], opt[3], sig, opt[1], rmse