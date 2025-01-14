

# TODO:
"""
 [ ] Finalise docstrings
 [ ] Add unittests
 [ ] Clean-up uncertainty/inversion methods
"""

# Importing python compatibility functions
from __future__ import print_function

import emcee
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import leastsq, curve_fit

from rawPy.friction_rsf import rsf_framework
from rawPy.integrator import integrator_class
from rawPy.bayes import bayes_framework

import warnings
warnings.simplefilter("once", UserWarning)


class rsf_inversion(integrator_class, rsf_framework, bayes_framework):
    """
    Main API for the RSF inversion tool
    """

    solver_modes = ("dense", "step")

    def __init__(self):
        integrator_class.__init__(self)
        rsf_framework.__init__(self)
        bayes_framework.__init__(self)
        pass

    def set_params(self, params):
        """
        Set the parameter dictionary and perform sanity checks. The following
        parameters are required: (a, b, Dc, mu0, V0, V1)
        Input: parameter dictionary
        Returns: None
        """
        # TODO: Add check for cut-off velocity, turn on cut-off if found
        # Also print warning that cut-off is enabled

        self.params = params

        required_params = ("a", "b", "Dc", "mu0", "V0", "V1")

        # Perform sanity check
        error = False
        for key in required_params:
            if key not in self.params:
                print("Parameter '%s' missing" % key)
                error = True

        # If we caught an error, exit program
        if error:
            exit()

        self.params["inv_Dc"] = 1.0/self.params["Dc"]
        self.params["inv_V0"] = 1.0 / self.params["V0"]

        pass

    def set_state_evolution(self, law):
        """
        Define the state evolution law as used in the simulations
        Input: (aging, ageing, slip)
        Returns: None
        """

        law = law.lower()
        law_book = self.law_book

        # Check is state evolution law exists
        for key, val in law_book.items():
            if law in val:
                law = key
                break
        else:
            print("The requested state evolution law (%s) is not available" % law)
            msg = ", ".join("%s => %s" % (key, val) for (key, val) in law_book.items())
            print("Available laws: %s" % msg)
            exit()

        # Set evolution law
        law_func = "_%s_law" % law
        self.params["state_evolution"] = law
        self._state_evolution = getattr(self, law_func)

        pass

    def forward(self, t, mode="dense"):
        """
        Construct forward RSF model at specified time intervals
        Input: time vector
        Returns: dictionary of friction, velocity, and state parameter
        """
        self.solver_mode = mode
        result = self.integrate(t)
        return result

    @staticmethod
    def interpolate(tx, t, y):
        """Interpolate y-data with corresponding t-data to desired tx nodes"""
        y_interp = np.interp(tx, t, y)
        return y_interp

    def error(self, p):
        """Calculate the misfit between data and model friction"""

        # Prepare parameter dict based in input parameters
        self.unpack_params(p)
        y0 = np.array([
            self.params["V0"],
            self.params["Dc"] / self.params["V0"]
        ])
        self.set_initial_values(y0)

        # Run forward model
        result = self.forward(self.data["t"])

        # Difference between data and forward model
        diff = self.data["mu"] - result["mu"]
        return diff

    def error_curvefit(self, t, *p):
        """Construct forward model along nodes in t, for given parameters *p"""
        self.unpack_params(p)
        y0 = np.array([
            self.params["V0"],
            self.params["Dc"] / self.params["V0"]
        ])
        self.set_initial_values(y0)
        result = self.forward(t, mode=self.solver_mode)
        mu = result["mu"]
        if self.solver_mode == "step":
            mu = self.interpolate(t, result["t"], result["mu"])
        return mu

    @staticmethod
    def estimate_uncertainty(pcov):
        """
        Estimate the uncertainty in the inverted parameters, based
        on the covariance matrix provided by the curve_fit function
        See https://bit.ly/2GRnjGJ for discussion
        """
        return np.sqrt(np.diag(pcov))

    def print_result(self, popt, err):
        """Print the results of the inversion on-screen (TODO)"""

        return None

        params = self.unpack_params(popt)

        print("\nResult of inversion:\n")
        for key, val in params.items():
            print("%s = %.3e +/- %.3e" % (key, popt[i], err[i]))
        print("\n(errors reported as single standard deviation) \n")

        pass

    def pack_params(self):
        """
        Auxiliary function to prepare the vector containing the
        to-be inverted parameters from the params dict
        """
        x = [self.params[key] for key in self.inversion_params]
        return x

    def unpack_params(self, p):
        """
        Auxiliary function to prepare the params dict from the
        vector of to-be inverted parameters
        """
        params = dict((key, val) for key, val in zip(self.inversion_params, p))
        params["inv_Dc"] = 1.0/params["Dc"]
        self.params.update(params)

        return params

    def inv_curvefit(self):
        """Perform non-linear least-squares"""

        # Prepare a vector with our initial guess
        x0 = self.pack_params()

        # NL-LS inversion
        popt, pcov = curve_fit(self.error_curvefit, xdata=self.data["t"], ydata=self.data["mu"], p0=x0)

        # Return best-fit parameters and covariance matrix
        return popt, pcov

    def inversion(self, data_dict, inversion_params, plot=True, bayes=False, load_pickle=False, mode="dense"):
        """Main inversion API function"""

        # Check if supplied solver mode is valid
        if mode not in self.solver_modes:
            print("Illegal solver mode '%s'. Available options: %r" % (mode, self.solver_modes))
            exit()

        # Set solver mode
        self.solver_mode = mode

        # Make sure the set of inversion parameters is a tuple
        inversion_params = tuple(inversion_params)

        # Store input parameters
        self.inversion_params = inversion_params
        self.data = data_dict

        if bayes is True:
            # Perform Bayesian inference
            if load_pickle is not False:
                self.inversion_params += "sigma",
                self.unpickle_chain(load_pickle)
                popt, uncertainty = self.get_mcmc_stats().T
            else:
                popt0, _ = self.inv_curvefit()
                self.inversion_params += "sigma",
                self.params["sigma"] = 1.0
                popt0 = np.hstack([popt0, self.params["sigma"]])
                popt, uncertainty = self.inv_bayes(popt0)
        else:
            # Get best-fit parameters and covariance matrix
            popt, pcov = self.inv_curvefit()

            # Calculate one standard error of estimate
            uncertainty = self.estimate_uncertainty(pcov)

        # Print results to screen
        self.print_result(popt, uncertainty)

        # Prepare output dictionary
        out = {}
        for i, key in enumerate(self.inversion_params):
            # Each parameter result is stored as a pair of
            # (value, uncertainty) in output dict
            out[key] = (popt[i], uncertainty[i])
            params = self.unpack_params(popt)
            result = self.forward(self.data["t"])

            mu_model = result["mu"]
            t = result['t']
        # Check if a plot is requested
        if plot is True:

            # Construct forward model with best-fit parameters
        
            plt.figure()
            plt.plot(t, self.data["mu"], label="Data")
            plt.plot(t, mu_model, label="Inversion")
            plt.legend(loc=1)
            plt.xlabel("time")
            plt.ylabel("friction [-]")
            plt.tight_layout()
            plt.show()

        return out,mu_model,t
