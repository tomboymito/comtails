"""Формирование звёздного фона для фотометрического сравнения синтетических карт."""
import os
import requests
import numpy as np

from constants import FLOAT_TYPE
from utils.coordinate_transforms import std_coor


class StarField:
    """
    Class for downloading and processing star field data.

    This class handles fetching star positions from catalogs
    and converting them to the image coordinate system.
    """

    def __init__(self, config):
        """
        Initialize the star field handler.

        Args:
            config: SimulationConfig object
        """
        self.config = config
        self.output_dir = "output"
        self.stars = []
        self.flux_array = np.zeros((config.nx, config.ny), dtype=FLOAT_TYPE)
        self.star_count = 0

        # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
        os.makedirs(self.output_dir, exist_ok=True)

    def download_star_field(self, apply_filtering=False, max_stars=10000):
        """
        Download star field data from Gaia EDR3.

        Args:
            apply_filtering: Whether to filter stars by magnitude and count
            max_stars: Maximum number of stars to return

        Returns:
            bool: True if successful, False otherwise
        """
        # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
        ra_str = f"{self.config.ra:.3f}"
        de_str = f"{self.config.dec:.3f}"

        # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
        sign = '+' if self.config.dec >= 0 else ''

        # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
        base_url = "https://irsa.ipac.caltech.edu/cgi-bin/Gator/nph-query"

        # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
        # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
        params = {
            "catalog": "gaia_edr3_source",
            "spatial": "cone",
            "objstr": f"{ra_str} {sign}{de_str}",
            "radius": "3600",   # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
            "outfmt": "1",
            "selcols": "ra,dec,phot_g_mean_mag,phot_rp_mean_mag,phot_bp_mean_mag"
        }

        # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
        print(f"Query coordinates: RA={ra_str}, DEC={sign}{de_str}")
        print(f"Magnitude limit: {self.config.maglim}")

        # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
        try:
            print("Downloading star field coordinate/mag table...")
            response = requests.get(base_url, params=params)

            if response.status_code != 200:
                print(f"Error downloading star data: HTTP {response.status_code}")
                return False

            # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
            if 'stat="ERROR"' in response.text:
                print(f"Server returned an error in response")
                print(response.text[:500])   # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
                return False

            # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
            star_data_file = f'{self.output_dir}/star.dat'
            with open(star_data_file, 'w') as f:
                f.write(response.text)

            print(f"Star data saved to {star_data_file}")

            # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
            with open(star_data_file, 'r') as f:
                content = f.read()
                if '|' not in content:
                    print("Warning: Downloaded file does not contain expected column separator '|'")
                    print("First 100 characters of response:")
                    print(content[:100])
                else:
                    # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
                    data_lines = sum(1 for line in content.splitlines() if '|' in line)
                    print(f"Downloaded approximately {data_lines} data lines")

            return True

        except Exception as e:
            print(f"Error in download_star_field: {e}")
            return False

    def process_star_field(self, apply_filtering=False):
        """
        Process downloaded star field data.

        Args:
            apply_filtering: Whether to filter stars by magnitude

        Returns:
            int: Number of stars processed
        """
        star_data_file = f'{self.output_dir}/star.dat'
        output_file = f'{self.output_dir}/starpos.dat'

        # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
        self.flux_array = np.zeros((self.config.nx, self.config.ny), dtype=FLOAT_TYPE)

        try:
            # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
            with open(output_file, 'w') as star_file:
                print(f"Processing star data from {star_data_file}")

                # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
                with open(star_data_file, 'r') as f:
                    lines = f.readlines()

                # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
                header_end = 0
                for i, line in enumerate(lines):
                    if '|' in line and 'ra' in line.lower() and 'dec' in line.lower():
                        header_end = i
                        break

                # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
                data_start = header_end + 4

                # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
                self.star_count = 0
                processed_count = 0   # Комментарий (RU): астрофизическая логика и назначение описаны в коде.

                for i in range(data_start, len(lines)):
                    line = lines[i].strip()
                    if not line or line.startswith('\\'):
                        continue

                    # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
                    parts = [p for p in line.split() if p]

                    if len(parts) < 7:   # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
                        continue

                    try:
                        # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
                        ra_star = float(parts[0])
                        de_star = float(parts[1])

                        # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
                        if parts[4].lower() == 'null' or parts[5].lower() == 'null' or parts[6].lower() == 'null':
                            continue

                        # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
                        gmag = float(parts[4])   # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
                        rpmag = float(parts[5])   # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
                        bpmag = float(parts[6])   # Комментарий (RU): астрофизическая логика и назначение описаны в коде.

                        processed_count += 1

                        # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
                        if apply_filtering and gmag > self.config.maglim:
                            continue

                        # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
                        xtemp, ytemp = std_coor(
                            self.config.ra,
                            self.config.dec,
                            ra_star,
                            de_star
                        )

                        # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
                        posx = int(xtemp * self.config.arcsec_rad / self.config.scale) + self.config.inuc
                        posy = int(ytemp * self.config.arcsec_rad / self.config.scale) + self.config.jnuc

                        # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
                        posx = self.config.nx - posx
                        posy = self.config.ny - posy

                        # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
                        # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
                        xtemp = bpmag - rpmag
                        ytemp = (0.02275 + 0.3691 * xtemp - 0.1243 * xtemp ** 2 -
                                0.01396 * xtemp ** 3 + 0.003775 * xtemp ** 4)
                        rmag = gmag - ytemp

                        starmag = rmag
                        starflux = 10 ** (-0.4 * (starmag + 10.925))

                        # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
                        if (posx >= 0 and posx < self.config.nx and
                                posy >= 0 and posy < self.config.ny):

                            # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
                            if starmag < self.config.maglim:
                                # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
                                star_file.write(
                                    f"{posx:5d} {posy:5d} {starmag:12.4e} {starflux:12.4e}\n")

                                # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
                                self.flux_array[posx, posy] += starflux

                                # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
                                self.stars.append({
                                    'ra': ra_star,
                                    'dec': de_star,
                                    'x': posx,
                                    'y': posy,
                                    'mag': starmag,
                                    'flux': starflux
                                })

                                self.star_count += 1

                    except Exception as e:
                        # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
                        continue

                print(f"Processed {processed_count} stars, {self.star_count} added within magnitude limit {self.config.maglim}")
                return self.star_count

        except Exception as e:
            print(f"Error processing star field: {e}")
            return 0

    def get_flux_array(self):
        """
        Get the star flux array.

        Returns:
            ndarray: Star flux array
        """
        return self.flux_array
