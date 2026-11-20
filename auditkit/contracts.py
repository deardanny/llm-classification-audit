"""Strict structural checks. Valid structure is not semantic correctness."""
import json

def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON key')
        result[key] = value
    return result

def parse_binary(text, expected_id, *, stop_reason):
    """Accept one complete JSON object; do not infer or repair a label."""
    if type(expected_id) is not int or stop_reason != 'end_turn':
        raise ValueError('Invalid expected ID or incomplete generation')
    value = json.loads(text, object_pairs_hook=_unique_object)
    if not isinstance(value, dict) or set(value) != {'id','off_topic'}:
        raise ValueError('Unexpected fields')
    if type(value['id']) is not int or value['id'] != expected_id:
        raise ValueError('ID mismatch')
    if type(value['off_topic']) is not bool:
        raise ValueError('Expected a JSON boolean')
    return 'off_topic' if value['off_topic'] else 'on_topic'

def validate_source_ids(status, ids, available_ids):
    """Evidence must point to supplied input spans, not generated quotations."""
    if status not in ('match', 'no_match', 'insufficient_context'):
        raise ValueError('Unknown status')
    if not isinstance(ids,list) or any(type(x) is not int for x in ids):
        raise ValueError('Source IDs must be integers')
    if len(set(ids)) != len(ids) or any(x not in available_ids for x in ids):
        raise ValueError('Invalid source reference')
    if (status == 'match') != bool(ids):
        raise ValueError('Status/evidence mismatch')
    return True
