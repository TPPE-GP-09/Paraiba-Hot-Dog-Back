import os
import requests

SONAR_TOKEN = os.getenv("SONAR_TOKEN", "")
SONAR_URL = os.getenv("SONAR_URL", "http://localhost:9000")
PROJECT_KEY = "paraiba-hot-dog-back"


def get_metrics():
    metrics = "coverage,bugs,vulnerabilities,code_smells,duplicated_lines_density"
    url = f"{SONAR_URL}/api/measures/component"
    params = {"component": PROJECT_KEY, "metricKeys": metrics}
    headers = {"Authorization": f"Bearer {SONAR_TOKEN}"}
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    data = get_metrics()
    for measure in data.get("component", {}).get("measures", []):
        print(f"{measure['metric']}: {measure.get('value', 'N/A')}")
