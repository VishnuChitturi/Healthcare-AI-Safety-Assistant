from modules.risk_classifier import assess_risk


def check_risk(query):
    return assess_risk(query)["level"]