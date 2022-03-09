import numpy as np
from scipy import optimize


def ln_return(S: np.ndarray):
    """Calculate Natural Log return of a price list

    Parameters:
    S : Asset prices array

    Returns:
    ndarray : Log Return array
    """

    # return np.apply_along_axis(lambda x: 1-(x[0]/x[1]), 1, list(zip(S[1:], S[:-1])))
    return np.apply_along_axis(lambda x: np.log(x[1]/x[0]), 1, list(zip(S[1:], S[:-1])))


def standard_deviation_p(w: np.ndarray, cov: np.ndarray):
    """Calculate portfolio standard deviation (sigma-p)
    
    Parameters:
    w : allocation vector of assets
    cov : covariance matrix of assets
        shape : w x w
    
    Returns:
    float : standard deviation
    """
    
    return float(np.apply_along_axis(lambda x: np.sqrt(np.dot(x, np.dot(cov, x.T))), 0, np.array(w)))


def mean_return_p(w: np.ndarray, r: np.ndarray):
    """Calculate portfolio mean return
    
    Parameters:
    w : allocation vector of assets
    r : mean return of assets
    
    Returns:
    float : mean return
    """

    return (w * r).sum()


def sharper_ratio(Er: float, std: float, Rf=0.03):
    """Calculate sharper ratio (slope of the market line)
    
    Parameters:
    Er : mean return / expected return of portfolio
    std : standard deviation of portfolio
    Rf : risk-free rate
    
    Returns:
    float : sharper ratio
    """

    return (Er - Rf) / std


def risky_allocation(Er: float, std: float, Rf=0.01, A=10):
    """Calculate capital allocation to risk-free asset

    Parameters:
    Er : mean return / expected return of portfolio
    std : standard deviation of portfolio
    Rf : risk-free rate
    A : measure of investor's risk aversion

    Returns:
    float : y* is the proportion of portfolio in risky portfolio
    """

    return (Er - Rf) / (A * std)


def optimize_p(w: np.ndarray, r: np.ndarray, cov: np.ndarray):
    """Calculate sharper ratio (slope of the market line)
    
    Parameters:
    w : allocation vector of assets
    r : mean return of assets
    cov : covariance matrix of assets
        shape : w x w
    
    Returns:
    np.ndarray : res (from optimize.minimize)
    float : final minimized score
    """

    def shp_min(w0):
        return -sharper_ratio(mean_return_p(w0, r), standard_deviation_p(w0, cov))
    
    cons = {'type': 'eq', 'fun': lambda x: sum(x) - 1}
    bou = optimize.Bounds(0, 10)
    res = optimize.minimize(shp_min, w)

    res_per = [x/sum(res.x) for x in res.x]
    new_sharper = sharper_ratio(mean_return_p(res_per, r), standard_deviation_p(res_per, cov))

    return (res_per, new_sharper)
