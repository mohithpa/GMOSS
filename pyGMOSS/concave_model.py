import numpy as np
import pandas as pd
from scipy.optimize import minimize, Bounds
import matplotlib.pyplot as plt

class ConcaveModel:
    def __init__(self, DATA):
        self.T_e = 8000
        self.nu_t = 0.001
        self.DATA = DATA
        self.brightness_temperature_df = pd.read_csv(f"{self.DATA}brightness_temp_per_pixel.csv")
        self.convexity_df = pd.read_csv(f"{self.DATA}convexity.csv")
        self.frequencies_string = np.array(["22", "45", "150", "408", "1420", "23000"]) # MHz
        self.frequencies = np.array([22, 45, 150, 408, 1420, 23000]) # MHz
        self.frequencies = self.frequencies * 1e-3 # GHz
        self.df = pd.merge(self.brightness_temperature_df, self.convexity_df, on = "PIXEL")
        self.df_concave = self.df.loc[self.df.loc[:, "Concave/Convex"] == "Concave", :]
        self.df_concave.reset_index(inplace =  True, drop = True)
        self.pixels = self.df_concave.loc[:, "PIXEL"]
        self.df_concave.set_index("PIXEL", inplace = True)

    def concave_func(self, x, C_1, C_2, alpha_1, alpha_2, I_x, nu_t, T_e): 
        one = np.power(x, -alpha_1)
        two = (C_2 / C_1) * np.power(x, -alpha_2)
        three = I_x * np.power(x, -2.1)
        expo = np.exp(-1 * np.power((nu_t / x), 2.1))
        eqn_one = C_1 * (one + two + three) * expo
        eqn_two = T_e * (1 - expo)
        return eqn_one + eqn_two


    def chisq(self, params, xobs, yobs):
        ynew = self.concave_func(xobs, *params)
        yerr = np.sum(((yobs- ynew)/ynew)**2)
        return yerr

    def fit(self):
        to_save_list = []
        for pixel in self.pixels:
            to_save = {}
            print(f"Pixel Number: {pixel}")

            self.b_temp = np.array([])
            for f in self.frequencies_string:
                self.b_temp = np.append(self.b_temp, self.df_concave.loc[pixel, f"{f}MHz"])
            
            alpha_1 = self.df.loc[pixel, "ALPHA_1"]
            alpha_2 = self.df.loc[pixel, "ALPHA_2"]

            fnorm1 = self.b_temp[2] / np.power(self.frequencies[2], -1 * alpha_1)
            fnorm2 = (self.b_temp[3] / np.power(self.frequencies[3], -1 * alpha_2)) / fnorm1
            extn = np.exp(-1 * np.power(self.nu_t / self.frequencies[5], 2.1))
            T_x = (1. / np.power(self.frequencies[5], -2.1)) * ((self.b_temp[5] - self.T_e * (1. - extn)) / (fnorm1 * extn)) - ((np.power(self.frequencies[5], -1. * alpha_1)) + (fnorm2 * np.power(self.frequencies[5], -1. * alpha_2)))

            if T_x <= 0:
                T_x = 1e-10
            
            x0 = [fnorm1, fnorm2, alpha_1, alpha_2, T_x, self.nu_t, self.T_e]
            bounds = ((-np.inf, np.inf), (-np.inf, np.inf), (2,3), (2,3), (-np.inf, np.inf), (-np.inf, np.inf), (0,10000))

            self.result = minimize(self.chisq, args = (self.frequencies, self.b_temp), x0 = x0, method = "Nelder-Mead", bounds = bounds)

            to_save["PIXEL"] = pixel
            to_save["FNORM1"] = self.result.x[0]
            to_save["FNORM2"] = self.result.x[1]
            to_save["ALPHA_1"] = self.result.x[2]
            to_save["ALPHA_2"] = self.result.x[3]
            to_save["T_X"] = self.result.x[4]
            to_save["NU_T"] = self.result.x[5]
            to_save["T_E"] = self.result.x[6]

            to_save_list.append(to_save)

        return pd.DataFrame(to_save_list)


if __name__ == "__main__":
    from dotenv import load_dotenv
    import os

    load_dotenv()
    DATA = os.environ.get("DATA")

    x = np.linspace(-300, 24000, 1000) * 1e-3
    model = ConcaveModel(DATA)
    df = model.fit()

    df.to_csv(f"{DATA}concave_pixel_fits.csv", index = False)