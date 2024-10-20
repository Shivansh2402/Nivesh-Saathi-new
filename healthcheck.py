from healthcheck import HealthCheck, EnvironmentDump

from metahackathonfinance import app

health = HealthCheck()
envdump = EnvironmentDump()


def app_status():
    return True, "SUCCESS"


health.add_check(app_status)


# add your own data to the environment dump
def application_data():
    return {"maintainer": "Team Engati", }


envdump.add_section("application", application_data)

# Add a flask route to expose information
app.add_api_route("/healthcheck", lambda: health.run())
app.add_api_route("/environment", lambda: envdump.run())