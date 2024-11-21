import logging

logger = logging.getLogger(__name__)

def clean_asset_name(asset):
    """Remove LD prefix and handle special cases."""
    logger.info(f"Asset before cleaning: {asset}")
    if asset.startswith('LD'):
        return asset[2:]  # Remove 'LD' prefix
    return asset
