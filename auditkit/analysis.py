"""Descriptive paired comparisons. None of these metrics measures accuracy."""
from collections import Counter

LABELS = frozenset(('on_topic', 'off_topic'))

def repeat_state(labels):
    """A missing call is unavailable, never an off-topic prediction."""
    labels = tuple(labels)
    if not labels:
        raise ValueError('At least one repetition is required')
    if any(x is not None and x not in LABELS for x in labels):
        raise ValueError('Unknown label')
    if any(x is None for x in labels):
        return 'unavailable'
    return labels[0] if len(set(labels)) == 1 else 'mixed'

def paired_transitions(control, treatment):
    """Pair by unique ID, fail on missing IDs, and report missing calls separately."""
    if set(control) != set(treatment):
        raise ValueError('Control and treatment IDs must match exactly')
    counts = Counter(); unavailable = 0
    for key, a in control.items():
        b = treatment[key]
        if any(x is not None and x not in LABELS for x in (a,b)):
            raise ValueError('Unknown label')
        if a is None or b is None:
            unavailable += 1
        else:
            counts[f'{a} -> {b}'] += 1
    n = sum(counts.values())
    changed = counts['off_topic -> on_topic'] + counts['on_topic -> off_topic']
    return {'complete_pairs': n, 'unavailable_pairs': unavailable,
            'transitions': dict(counts), 'changed': changed,
            'change_fraction': changed / n if n else None}
