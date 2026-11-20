"""Dictionary masking regression fix: exclude the known aggregate dictionary value."""
import re

VERSION='dictionary-mask-v2-exclude-aggregate-all'


def build_school_pattern(school_values):
    """Keep real school strings intact, including names containing the word All."""
    school_values=list(school_values)
    if any(not isinstance(value,str) for value in school_values):
        raise ValueError('School dictionary entries must be strings')
    schools={value for value in school_values if value and value.casefold()!='all'}
    if not schools:return re.compile(r'(?!)')
    return re.compile(r'(?<!\w)(?:'+'|'.join(re.escape(s) for s in sorted(schools,key=lambda s:(-len(s),s)))+r')(?!\w)',re.I)
