import logging

class HouseSignificatorEngine:
    """Simple engine to analyze KP cusp sub-lords."""

    def __init__(self, house_system: str, query_type: str, api_data: dict):
        self.house_system = house_system
        self.query_type = query_type
        self.api_data = api_data

    def analyze_sublords(self) -> dict:
        """Return sub-lords of 1st, 6th and 10th cusps.

        Also captures the Moon sub-lord for context.
        """
        cusp_sublords = self.api_data["houses_data"]
        first_sub = cusp_sublords[0]["SubLord"]
        sixth_sub = cusp_sublords[5]["SubLord"]
        tenth_sub = cusp_sublords[9]["SubLord"]

        moon_info = [p for p in self.api_data["planets_data"] if p["Object"] == "Moon"][0]
        moon_sublord = moon_info["SubLord"]

        logging.info(
            "Using %s: 1st sub-lord = %s, 6th = %s, 10th = %s",
            self.house_system,
            first_sub,
            sixth_sub,
            tenth_sub,
        )

        return {
            "first_sub": first_sub,
            "sixth_sub": sixth_sub,
            "tenth_sub": tenth_sub,
            "moon_sublord": moon_sublord,
        }
