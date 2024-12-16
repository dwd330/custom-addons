import logging

_logger = logging.getLogger(__name__)

CONFIG_URIS = {
    'access_token': 'https://business-api.tiktok.com/open_api/v1.3/oauth2/access_token/',
    'download_leads': 'https://business-api.tiktok.com/open_api/v1.3/page/lead/task/download/',
    'lead_task': 'https://business-api.tiktok.com/open_api/v1.3/page/lead/task/',
}

def get_uri(key, error_message):
    """Retrieve a URI from the configuration."""
    uri = CONFIG_URIS.get(key)
    if not uri:
        _logger.error("Configuration error: %s", error_message)
        raise ValueError(error_message)
    return uri

def get_config_param(env, key, error_message):
    """Retrieve configuration parameter from Odoo."""
    param = env['ir.config_parameter'].sudo().get_param(key)
    if not param:
        _logger.error("Configuration error: %s", error_message)
        raise ValueError(error_message)
    return param

