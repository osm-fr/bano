def find_cp_in_tags(tags):
    return tags.get('addr:postcode') or tags.get('postal_code') or ''


def is_valid_housenumber(hsnr):
    return len(hsnr) <= 11
